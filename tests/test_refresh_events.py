import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('refresh', ROOT/'scripts/refresh_events.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
NOW=datetime(2026,10,3,2,31,tzinfo=timezone.utc)
S={'id':'test','name':'Official Museum','url':'https://example.org/calendar/','allowedHosts':['example.org'],'state':'VT','city':'Norwich','venue':'Museum','address':'1 Main St','timezone':'America/New_York','enabled':True,'mode':'jsonld'}
RAW={'@type':'Event','name':'Sensory-friendly hour','description':'<p>Reduced sound.</p>','startDate':'2026-11-21T09:00:00-05:00','endDate':'2026-11-21T10:00:00-05:00','url':'https://example.org/event/1'}
class FakeFetcher:
 def __init__(self,body=None,error=None): self.body=body; self.error=error
 def get(self,source):
  if self.error: raise self.error
  return self.body
class RefreshTests(unittest.TestCase):
 def event(self):
  e=m.normalize(RAW,S,m.now_iso(NOW)); e['reviewRequired']=False; e['lastVerified']='2026-10-03T01:00:00Z'; return e
 def previous(self): return {'sources':[], 'refresh':{'lastSuccessfulRun':'2026-10-02T00:00:00Z'}}
 def test_seed_valid(self):
  seed=json.loads((ROOT/'data/curated-events.json').read_text()); self.assertEqual(len(seed),15)
  for e in seed: m.validate(e)
 def test_dst_summer(self): self.assertEqual(m.parse_time('2026-10-17T09:00:00').utcoffset().total_seconds(),-14400)
 def test_dst_winter(self): self.assertEqual(m.parse_time('2026-11-21T09:00:00').utcoffset().total_seconds(),-18000)
 def test_ambiguous_dst_rejected(self):
  with self.assertRaises(ValueError): m.parse_time('2026-11-01T01:30:00')
 def test_missing_dst_hour_rejected(self):
  with self.assertRaises(ValueError): m.parse_time('2026-03-08T02:30:00')
 def test_date_only_rejected(self):
  with self.assertRaises(ValueError): m.parse_time('2026-10-17')
 def test_external_content_not_executed(self):
  self.assertEqual(m.clean('<script>steal()</script><b>Welcome</b>'), 'Welcome')
 def test_urls(self):
  for value in ('javascript:alert(1)','http://example.org/a','https://example.org@evil.test/','https://evil.test/'):
   self.assertIsNone(m.safe_url(value,S['allowedHosts']))
 def test_safe_redirect_denied(self):
  with self.assertRaises(ValueError): m.RestrictedRedirect(['example.org']).redirect_request(None,None,302,'',{},'https://evil.test/')
 def test_jsonld_graph(self):
  body='<script type="application/ld+json">'+json.dumps({'@graph':[RAW]})+'</script>'
  self.assertEqual(m.extract_jsonld(body)[0]['name'],RAW['name'])
 def test_not_all_quiet_events_accessible(self):
  raw=dict(RAW,name='Quiet sketching',description='A calm activity.'); self.assertIsNone(m.normalize(raw,S,'2026-10-03T01:00:00Z'))
 def test_bad_region(self):
  raw=dict(RAW,location={'address':{'addressRegion':'NY'}})
  with self.assertRaises(ValueError): m.normalize(raw,S,'2026-10-03T01:00:00Z')
 def test_missing_end(self):
  raw=dict(RAW); raw.pop('endDate')
  with self.assertRaises(ValueError): m.normalize(raw,S,'2026-10-03T01:00:00Z')
 def test_failure_preserves_events_and_timestamp(self):
  original=self.event(); output,q=m.prepare([original],self.previous(),[S],[],NOW,FakeFetcher(error=OSError('unreachable')))
  self.assertEqual(len(output['events']),1); self.assertEqual(output['events'][0]['lastVerified'],original['lastVerified'])
  self.assertEqual(output['refresh']['status'],'degraded'); self.assertEqual(output['refresh']['lastSuccessfulRun'],'2026-10-02T00:00:00Z')
 def test_expiry_and_dedupe(self):
  original=self.event(); past=dict(original,id='old',start='2026-09-01T09:00:00-04:00',end='2026-09-01T10:00:00-04:00')
  output,q=m.prepare([original,original,past],self.previous(),[],[],NOW,FakeFetcher())
  self.assertEqual(len(output['events']),1)
 def test_review_flag_preserved_and_not_published(self):
  original=self.event(); original['reviewRequired']=True
  output,q=m.prepare([original],self.previous(),[],[],NOW,FakeFetcher())
  self.assertEqual(output['events'],[]); self.assertTrue(original['reviewRequired'])
 def test_new_feed_event_queued_never_published(self):
  body='<script type="application/ld+json">'+json.dumps(RAW)+'</script>'
  output,q=m.prepare([],self.previous(),[S],[],NOW,FakeFetcher(body))
  self.assertEqual(output['events'],[]); self.assertEqual(len(q),1); self.assertTrue(q[0]['reviewRequired']); self.assertIsNone(q[0]['lastVerified'])
  self.assertFalse(output['refresh']['liveFeedVerified'])
 def test_stale_marker(self):
  e=self.event(); e['lastVerified']='2026-08-01T01:00:00Z'
  output,q=m.prepare([e],self.previous(),[],[],NOW,FakeFetcher()); self.assertTrue(output['events'][0]['stale'])
 def test_cancelled_not_listed(self):
  e=self.event(); e['status']='cancelled'
  output,q=m.prepare([e],self.previous(),[],[],NOW,FakeFetcher()); self.assertEqual(output['events'],[])
 def test_source_changed_queue(self):
  s=dict(S,mode='check'); previous=self.previous(); previous['sources']=[dict(S,contentHash='old')]
  output,q=m.prepare([self.event()],previous,[s],[],NOW,FakeFetcher('<p>New text</p>'))
  self.assertEqual(output['sources'][0]['status'],'changed-review-needed'); self.assertTrue(q[0]['reviewRequired'])
 def test_robots_denial_no_page_fetch(self):
  f=m.Fetcher()
  with patch.object(f,'_get',return_value='User-agent: *\nDisallow: /') as get:
   with self.assertRaises(ValueError): f.get(S)
   self.assertEqual(get.call_count,1)
 def test_robots_unavailable_fails_closed(self):
  f=m.Fetcher()
  with patch.object(f,'_get',side_effect=OSError('unavailable')) as get:
   with self.assertRaises(OSError): f.get(S)
   self.assertEqual(get.call_count,1)
if __name__=='__main__': unittest.main()
