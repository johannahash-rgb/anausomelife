import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Filters(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/events.json').read_text());cls.meta=json.loads((ROOT/'data/event-filters.json').read_text())['events'];cls.events={e['id']:e for e in cls.data['events']}
 def test_all_event_ids_have_metadata(self):self.assertEqual(set(self.events),set(self.meta))
 def test_every_positive_tag_has_https_evidence(self):
  for eid,m in self.meta.items():
   for tagkey,proofkey in [('ageGroups','ageEvidence'),('accessFeatures','accessEvidence')]:
    for tag in m[tagkey]:self.assertTrue(m[proofkey][tag]['url'].startswith('https://'),(eid,tag))
 def test_no_invalid_tags(self):
  ages={'all-ages','children','teens','adults','families'};access={'sensory-friendly','wheelchair-step-free','adaptive-activities','caregiver-support','vision-support','hearing-support'}
  for m in self.meta.values():self.assertTrue(set(m['ageGroups'])<=ages);self.assertTrue(set(m['accessFeatures'])<=access)
 def test_westport_children_not_universal_adult(self):
  for eid,m in self.meta.items():
   if eid.startswith('westport-'):self.assertIn('children',m['ageGroups']);self.assertNotIn('all-ages',m['ageGroups']);self.assertNotIn('adults',m['ageGroups']);self.assertIn('children of all ages',self.events[eid]['ages'])
 def test_unconfirmed_workouts_hidden(self):
  for eid in ['some-workout-2026-10-06','some-workout-2026-11-03']:self.assertTrue(self.events[eid]['reviewRequired']);self.assertEqual(self.events[eid]['status'],'review')
 def test_shelburne_terrain_not_blanket_access(self):
  for eid,m in self.meta.items():
   if eid.startswith('shelburne-'):self.assertNotIn('wheelchair-step-free',m['accessFeatures']);self.assertTrue(any('slopes' in n for n in self.events[eid]['notes']))
 def test_virtual_events_have_no_travel_pin_assumption(self):
  s=(ROOT/'assets/event-map.js').read_text();self.assertIn("if(!g.virtual)actions.append",s);self.assertIn("event.format==='Virtual'?null",s)
 def test_filters_are_native_and_labeled(self):
  s=(ROOT/'calendar.html').read_text()
  for name in ['age','access','format']:self.assertIn('select name="'+name+'"',s)
  self.assertIn('id="event-filter-help"',s)
 def test_discovery_calendar_is_not_new_event(self):
  x=[s for s in self.data['sources'] if s['id']=='sped-child-mass'];self.assertEqual(len(x),1);self.assertIn('discovery',x[0]['type'].lower())
if __name__=='__main__':unittest.main()
