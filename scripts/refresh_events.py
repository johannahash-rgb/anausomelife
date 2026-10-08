#!/usr/bin/env python3
"""Conservative, dependency-free calendar maintenance for static GitHub Pages.

No general web scraping: fetch only configured official URLs, honor robots.txt,
never execute external content, and queue newly discovered listings for review.
A successful HTTP fetch is NOT a fresh editorial verification of event details.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import socket
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urljoin
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser
from zoneinfo import ZoneInfo

UTC = timezone.utc
UA = 'AnAusomeLife-Events/1.0 (public event source checks; daily)'
MAX_BYTES = 2_000_000
STATES = {'CT', 'ME', 'MA', 'NH', 'RI', 'VT'}
EXPLICIT = re.compile(r'\b(sensory[\s-]*(?:friendly|inclusive)|autism[\s-]*friendly|relaxed performance)\b', re.I)
# Organizer opt-out, approved by the owner on 2026-10-08. Keep this guard even
# when an old source configuration or review queue is supplied to a refresh.
EXCLUDED_SOURCE_IDS = {'friends-in-action'}
EXCLUDED_HOSTS = {'friendsinactionnh.org'}


def excluded_listing(record):
    if record.get('id') in EXCLUDED_SOURCE_IDS or record.get('sourceId') in EXCLUDED_SOURCE_IDS:
        return True
    for key in ('url', 'sourceUrl', 'organizerUrl'):
        host = (urlparse(record.get(key) or '').hostname or '').lower()
        if any(host == blocked or host.endswith('.' + blocked) for blocked in EXCLUDED_HOSTS):
            return True
    return False


def now_iso(value):
    return value.astimezone(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')


def parse_time(value, zone='America/New_York'):
    """Require an exact timestamp; never turn a date-only event into midnight."""
    if not isinstance(value, str) or 'T' not in value:
        raise ValueError('An exact event time is required')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    tz = ZoneInfo(zone)
    if stamp.tzinfo is None:
        # Reject ambiguous / nonexistent local times, rather than invent an offset.
        early, late = stamp.replace(tzinfo=tz, fold=0), stamp.replace(tzinfo=tz, fold=1)
        if early.utcoffset() != late.utcoffset():
            raise ValueError('Ambiguous or nonexistent local time')
        if early.astimezone(UTC).astimezone(tz).replace(tzinfo=None) != stamp:
            raise ValueError('Nonexistent local time')
        stamp = early
    return stamp.astimezone(tz)


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def clean(value, limit=1200):
    p = TextOnly()
    p.feed(str(value or ''))
    return re.sub(r'\s+', ' ', html.unescape(' '.join(p.parts))).strip()[:limit]


def safe_url(value, allowed_hosts=None):
    if not isinstance(value, str): return None
    p = urlparse(value)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443):
        return None
    if allowed_hosts is not None and p.hostname.lower() not in allowed_hosts:
        return None
    return value


class RestrictedRedirect(HTTPRedirectHandler):
    def __init__(self, hosts): self.hosts = hosts
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not safe_url(newurl, self.hosts):
            raise ValueError('Redirect left the approved organizer host')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Fetcher:
    def __init__(self): self.robots = {}
    def _get(self, url, hosts, limit=MAX_BYTES):
        if not safe_url(url, hosts): raise ValueError('URL outside the configured allowlist')
        opener = build_opener(RestrictedRedirect(hosts))
        with opener.open(Request(url, headers={'User-Agent': UA, 'Accept': 'text/html, application/ld+json, application/json, text/calendar'}), timeout=15) as response:
            body = response.read(limit + 1)
            if len(body) > limit: raise ValueError('Response exceeds size limit')
            encoding = response.headers.get_content_charset() or 'utf-8'
            return body.decode(encoding, errors='replace')
    def get(self, source):
        url = source['url']
        hosts = [h.lower() for h in source['allowedHosts']]
        origin = 'https://' + urlparse(url).netloc
        if origin not in self.robots:
            robot = RobotFileParser()
            try:
                body = self._get(origin + '/robots.txt', hosts, limit=256_000)
                robot.parse(body.splitlines())
            except HTTPError as error:
                if error.code == 404:
                    robot.parse([])
                else:
                    raise ValueError('Robots unavailable or denied; source skipped') from error
            self.robots[origin] = robot
        if not self.robots[origin].can_fetch(UA, url):
            raise ValueError('Robots disallow this source')
        return self._get(url, hosts)


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.in_json, self.parts, self.documents = False, [], []
    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type', '').lower() == 'application/ld+json':
            self.in_json, self.parts = True, []
    def handle_data(self, data):
        if self.in_json: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == 'script' and self.in_json:
            self.in_json = False
            self.documents.append(json.loads(''.join(self.parts)))


def walk_events(value):
    if isinstance(value, list):
        for child in value: yield from walk_events(child)
    elif isinstance(value, dict):
        types = value.get('@type', [])
        if isinstance(types, str): types = [types]
        if any(t == 'Event' or str(t).endswith('/Event') for t in types): yield value
        else:
            for child in value.values(): yield from walk_events(child)


def extract_jsonld(body):
    p = JsonLdParser()
    p.feed(body)
    result = list(walk_events(p.documents))
    if not result: raise ValueError('No structured Event data; manual review needed')
    return result


def normalize(raw, source, checked):
    if excluded_listing(source) or excluded_listing(raw): return None
    title, description = clean(raw.get('name'), 180), clean(raw.get('description'))
    if not EXPLICIT.search(title + ' ' + description): return None
    if source['state'] not in STATES: return None
    start = parse_time(raw.get('startDate'), source['timezone'])
    end = parse_time(raw.get('endDate'), source['timezone'])
    if end <= start or end - start > timedelta(days=1):
        raise ValueError('Event has invalid or multi-day timing')
    url = safe_url(raw.get('url') or source['url'], source['allowedHosts'])
    if not url: raise ValueError('Event URL outside approved host')
    place = raw.get('location') or {}
    if not isinstance(place, dict): place = {}
    address = place.get('address') or {}
    if not isinstance(address, dict): address = {}
    region = clean(address.get('addressRegion')) or source['state']
    if region != source['state']: raise ValueError('Unverified event region')
    city = clean(address.get('addressLocality')) or source.get('city', '')
    venue = clean(place.get('name')) or source.get('venue', '')
    street = clean(address.get('streetAddress')) or source.get('address', '')
    if not title or not city or not venue: raise ValueError('Missing event identity or venue')
    key = '|'.join((source['id'], url, start.isoformat()))
    status = 'cancelled' if str(raw.get('eventStatus', '')).endswith('EventCancelled') else 'scheduled'
    return {'id': 'feed-' + hashlib.sha256(key.encode()).hexdigest()[:20], 'title': title,
            'start': start.isoformat(), 'end': end.isoformat(), 'timezone': source['timezone'],
            'state': source['state'], 'city': city, 'venue': venue, 'address': street,
            'cost': 'Check organizer', 'ages': 'Check organizer', 'summary': description,
            'accessibility': ['Organizer labels this event sensory-friendly or autism-friendly; review details.'],
            'sourceId': source['id'], 'sourceUrl': url, 'ticketUrl': None,
            'registration': 'Check organizer', 'cancellationPolicy': 'Check organizer',
            'notes': [], 'lastVerified': None, 'lastFetched': checked,
            'verificationMethod': 'Structured organizer data; awaiting review',
            'reviewRequired': True, 'status': status}


def event_key(event):
    return (clean(event['title']).casefold(), parse_time(event['start']).astimezone(UTC).isoformat(),
            clean(event['venue']).casefold(), event['state'])


def validate(event):
    for key in ('id', 'title', 'start', 'end', 'timezone', 'state', 'city', 'venue', 'sourceUrl'):
        if not event.get(key): raise ValueError('Missing required event field: ' + key)
    if event['state'] not in STATES: raise ValueError('Event is outside New England')
    if not safe_url(event['sourceUrl']): raise ValueError('Unsafe event source URL')
    if event.get('ticketUrl') and not safe_url(event['ticketUrl']): raise ValueError('Unsafe ticket URL')
    start, end = parse_time(event['start'], event['timezone']), parse_time(event['end'], event['timezone'])
    if end <= start: raise ValueError('End must be after start')
    if 'reviewRequired' not in event: raise ValueError('Review flag required')
    if not isinstance(event['reviewRequired'], bool): raise ValueError('Review flag must be boolean')
    if not event['reviewRequired'] and not event.get('lastVerified'): raise ValueError('Reviewed event needs verification date')


def prepare(curated, previous, sources, queue, now, fetcher=None):
    checked, fetcher = now_iso(now), fetcher or Fetcher()
    previous_sources = {s['id']: s for s in previous.get('sources', [])}
    results, new_queue = [], {e['id']: copy.deepcopy(e) for e in queue if not excluded_listing(e)}
    # Re-read curated records on every run; they remain the authoritative editorial layer.
    published, keys = [], set()
    for event in curated:
        if excluded_listing(event): continue
        validate(event)
        if parse_time(event['end']) <= now: continue
        if event['reviewRequired'] or event.get('status') == 'cancelled': continue
        key = event_key(event)
        if key in keys: continue
        keys.add(key)
        event = copy.deepcopy(event)
        event['stale'] = (now - parse_time(event['lastVerified'])).total_seconds() > 30 * 86400
        published.append(event)
    successes, failures = 0, 0
    for source in sources:
        if excluded_listing(source): continue
        result = {**source, **{k: v for k, v in previous_sources.get(source['id'], {}).items() if k in ('lastSuccessfulCheck', 'contentHash')}}
        if not source.get('enabled') or source['mode'] == 'manual':
            result.update(status='manual-review', lastChecked=source.get('sourceCheckedAt'))
            results.append(result)
            continue
        result['lastAttempt'] = checked
        try:
            body = fetcher.get(source)
            digest = hashlib.sha256(clean(body, MAX_BYTES).encode()).hexdigest()
            changed = bool(result.get('contentHash')) and digest != result['contentHash']
            result.update(status='changed-review-needed' if changed else 'reachable', lastSuccessfulCheck=checked,
                          lastChecked=checked, contentHash=digest)
            result.pop('error', None)
            if changed:
                item_id = 'source-change-' + source['id']
                new_queue[item_id] = {'id': item_id, 'sourceUrl': source['url'], 'state': source['state'],
                                      'title': source['name'] + ': source changed', 'reviewRequired': True,
                                      'checkedAt': checked, 'reason': 'The source text changed. Re-check curated dates, admission, and accommodations; a change is not automatically a cancellation.'}
            if source['mode'] == 'jsonld':
                raw_events = extract_jsonld(body)
                for raw in raw_events[:500]:
                    try:
                        event = normalize(raw, source, checked)
                        if not event or parse_time(event['end']) <= now or event_key(event) in keys: continue
                        # No unattended publication until a live adapter has been validated and editorially approved.
                        new_queue[event['id']] = event
                    except (ValueError, TypeError, KeyError) as error:
                        result['parseWarning'] = str(error)[:200]
                result['structuredDataParsed'] = True
            successes += 1
        except (HTTPError, URLError, OSError, ValueError, KeyError, TypeError, socket.timeout) as error:
            failures += 1
            result.update(status='unavailable', error=str(error)[:200])
        results.append(result)
    # Preserve review flags; expire dated candidates only once their known day has ended.
    live_queue = []
    for item in new_queue.values():
        if item.get('end') and parse_time(item['end']) <= now: continue
        if item.get('date') and datetime.fromisoformat(item['date']).replace(tzinfo=ZoneInfo('America/New_York')) + timedelta(days=1) <= now: continue
        live_queue.append(item)
    refresh = {'mode': 'curated-with-source-checks', 'status': 'degraded' if failures else ('source-checks-complete' if successes else 'manual-review'),
               'lastAttempt': checked, 'lastSuccessfulRun': checked if successes and not failures else previous.get('refresh', {}).get('lastSuccessfulRun'),
               'liveFeedVerified': False, 'sourcesChecked': successes, 'sourcesFailed': failures,
               'note': 'Past listings are removed automatically. New structured listings are queued for review. Source reachability does not verify event details.'}
    output = {'schemaVersion': previous.get('schemaVersion', 2), 'generatedAt': checked, 'lastEditorialReview': previous.get('lastEditorialReview'),
              'timezone': 'America/New_York', 'coverage': previous.get('coverage', 'Selected New England events; not exhaustive.'),
              'refresh': refresh, 'sources': results, 'events': sorted(published, key=lambda e:(e['start'], e['id']))}
    for key in ('accessibilityStandard', 'venueProfiles', 'watchlist'):
        if key in previous:
            output[key] = copy.deepcopy(previous[key])
    if 'watchlist' in output:
        output['watchlist'] = [item for item in output['watchlist'] if not excluded_listing(item)]
    return output, live_queue


def write_atomic(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default='data')
    parser.add_argument('--now', help='UTC ISO timestamp for reproducible checks')
    parser.add_argument('--offline', action='store_true', help='Expire events and validate data without fetching sources')
    args = parser.parse_args()
    root = Path(args.data_dir)
    read = lambda name: json.loads((root / name).read_text(encoding='utf-8'))
    sources = read('event-sources.json')
    if args.offline:
        sources = [dict(s, enabled=False) for s in sources]
    now = parse_time(args.now or now_iso(datetime.now(UTC)))
    result, queue = prepare(read('curated-events.json'), read('events.json'), sources, read('event-review-queue.json'), now)
    if args.offline:
        result['refresh']['status'] = 'offline-maintenance'
        result['refresh']['note'] = 'Local expiry and validation only. Organizer sources were not contacted.'
    write_atomic(root / 'events.json', result)
    write_atomic(root / 'event-review-queue.json', queue)
    print(json.dumps({'events': len(result['events']), 'reviewQueue': len(queue), 'refresh': result['refresh']}))

if __name__ == '__main__': main()
