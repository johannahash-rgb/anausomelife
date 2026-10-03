import json,unittest,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EventIllustrations(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((ROOT/'data/events.json').read_text());self.art=json.loads((ROOT/'data/event-illustrations.json').read_text())
 def test_every_dated_event_has_program_specific_art(self):
  for e in self.data['events']:
   self.assertIn(e['title']+'|'+e['venue'],self.art['programs'],e['id'])
 def test_all_watchlist_entries_have_art(self):
  for e in self.data['watchlist']:self.assertIn(e['id'],self.art['watchlist'])
 def test_assets_exist_and_are_distinct(self):
  rows=list(self.art['programs'].values())+list(self.art['watchlist'].values());hashes=[]
  for a in rows:
   self.assertRegex(a['src'],r'^/assets/event-sketches/[a-z0-9-]+\.webp$');p=ROOT/a['src'].lstrip('/');self.assertTrue(p.exists());self.assertGreater(len(a['alt']),25);hashes.append(hashlib.sha256(p.read_bytes()).hexdigest())
  self.assertEqual(len(hashes),len(set(hashes)))
 def test_native_labeled_calendar_controls(self):
  page=(ROOT/'calendar.html').read_text();self.assertIn('select name="month"',page);self.assertIn('Choose a month',page);self.assertIn('input name="from" type="date"',page);self.assertIn('data-sketch-icon="calendar"',page)
 def test_art_disclosure(self):
  self.assertIn('not venue photographs',(ROOT/'calendar.html').read_text());self.assertIn('AI sketch · inspired by this event',(ROOT/'assets/events.js').read_text())
 def test_external_state_directory_selector(self):self.assertIn("stateBox=document.querySelector('[data-state-index]')",(ROOT/'assets/events.js').read_text())
 def test_month_filter_and_return_focus(self):
  js=(ROOT/'assets/events.js').read_text();self.assertIn("e.start.slice(0,7)===month",js);self.assertIn('focus({preventScroll:true})',js)
if __name__=='__main__':unittest.main()
