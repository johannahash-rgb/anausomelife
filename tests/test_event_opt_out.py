"""Organizer opt-outs stay out of calendar publication and import queues."""
import copy
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('refresh', ROOT / 'scripts/refresh_events.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class OrganizerOptOutTests(unittest.TestCase):
    def test_public_calendar_and_search_exclude_listings(self):
        data = json.loads((ROOT / 'data/events.json').read_text())
        for group in ('events', 'sources', 'freePrograms', 'watchlist'):
            self.assertFalse(any(refresh.excluded_listing(item) for item in data.get(group, [])), group)
        for path in ('calendar.html', 'data/site-index.json', 'data/site-search/chunk-00.json', 'data/site-search/chunk-28.json'):
            text = (ROOT / path).read_text().lower()
            self.assertNotIn('friends in action', text, path)
            self.assertNotIn('friendsinactionnh.org', text, path)
        for path in ('data/event-filters.json', 'data/event-illustrations.json'):
            self.assertFalse(any(key.startswith('fia-') for key in json.loads((ROOT / path).read_text())['events']))

    def test_old_source_cannot_be_fetched_or_requeued(self):
        source = {'id': 'friends-in-action', 'url': 'https://friendsinactionnh.org/calendar/', 'enabled': True, 'mode': 'jsonld'}
        event = {'id': 'old-fia-event', 'sourceId': 'friends-in-action'}
        queue = [{'id': 'old-candidate', 'sourceUrl': 'https://www.friendsinactionnh.org/programs/'}]
        previous = {'sources': [source], 'watchlist': copy.deepcopy(queue)}
        fetcher = Mock()
        output, pending = refresh.prepare([event], previous, [source], queue, datetime(2026, 10, 8, tzinfo=timezone.utc), fetcher)
        fetcher.get.assert_not_called()
        self.assertEqual(output['events'], [])
        self.assertEqual(output['sources'], [])
        self.assertEqual(output['watchlist'], [])
        self.assertEqual(pending, [])

    def test_normalizer_rejects_opted_out_organizer(self):
        self.assertIsNone(refresh.normalize({}, {'id': 'friends-in-action'}, '2026-10-08T00:00:00Z'))
        self.assertIsNone(refresh.normalize({'url': 'https://friendsinactionnh.org/event/new'}, {'id': 'another-feed'}, '2026-10-08T00:00:00Z'))

    def test_exclusion_is_scoped_to_exact_organizer(self):
        for url in ('https://another-organizer.org/', 'https://notfriendsinactionnh.org/', 'https://friendsinactionnh.org.example.com/'):
            self.assertFalse(refresh.excluded_listing({'url': url}), url)
        self.assertFalse(refresh.excluded_listing({'id': 'other-friends-program'}))


if __name__ == '__main__':
    unittest.main()
