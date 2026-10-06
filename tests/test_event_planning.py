"""Calendar integrity and specific sensory/seasonal risk cases."""
import json,unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
class Planning(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/events.json').read_text());cls.meta=json.loads((ROOT/'data/event-filters.json').read_text())['events'];cls.events={e['id']:e for e in cls.data['events']}
 def test_distinct_dated_records_and_eastern_offsets(self):
  self.assertEqual(len(self.events),len(self.data['events']))
  seen=set()
  for e in self.events.values():
   start,end=map(datetime.fromisoformat,[e['start'],e['end']]);self.assertLess(start,end)
   self.assertEqual(start.utcoffset(),start.astimezone(ZoneInfo('America/New_York')).utcoffset(),e['id'])
   key=(e['title'],e['start'],e['venue']);self.assertNotIn(key,seen);seen.add(key)
 def test_classifications_explain_basis(self):
  for eid,m in self.meta.items():
   self.assertIn(m['sensory']['level'],{'low','moderate','high','variable','unknown'})
   self.assertTrue(m['sensory']['note']);self.assertTrue(m['sensory']['sourceUrl'].startswith('https://'))
   for tag in m['holidays']:self.assertTrue(m['holidayEvidence'][tag]['url'].startswith('https://'))
 def test_sensory_friendly_does_not_mean_low(self):
  self.assertEqual(self.meta['longhill-sensory-2026-10-23']['sensory']['level'],'variable')
  self.assertEqual(self.meta['northshore-santa-2026-12-06']['sensory']['level'],'unknown')
  self.assertEqual(self.meta['boston-ballet-2026-12-04']['sensory']['level'],'moderate')
  self.assertEqual(self.meta['shelburne-2026-12-14']['sensory']['level'],'variable')
 def test_only_published_sensory_windows(self):
  self.assertTrue(self.events['breakers-halloween-2026-10-23']['end'].startswith('2026-10-23T18:00'))
  self.assertTrue(self.events['castlehill-christmas-2026-12-12']['end'].startswith('2026-12-12T11:30'))
  self.assertTrue(self.events['raisingharts-tricks-2026-10-18']['end'].startswith('2026-10-18T17:00'))
  self.assertTrue(self.events['toyshop-sensory-2026-12-05']['endApproximate'])
 def test_conflicts_are_not_dated(self):
  for name in ['canton-santa','ucp-pumpkins']:
   self.assertFalse(any(k.startswith(name) for k in self.events))
   self.assertTrue(any(e['id'].startswith(name) for e in self.data['watchlist']))
 def test_christmas_covered_by_winter_filter(self):
  for m in self.meta.values():
   if 'christmas' in m['holidays']:self.assertIn('winter-holidays',m['holidays'])
if __name__=='__main__':unittest.main()
