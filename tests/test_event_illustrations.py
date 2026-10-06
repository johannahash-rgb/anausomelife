import json,unittest,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EventIllustrations(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((ROOT/'data/events.json').read_text());self.art=json.loads((ROOT/'data/event-illustrations.json').read_text())
 def test_every_dated_event_has_program_specific_art(self):
  for e in self.data['events']:self.assertIn(e['id'],self.art['events'],e['id'])
 def test_all_watchlist_entries_have_art(self):
  for e in self.data['watchlist']:self.assertIn(e['id'],self.art['watchlist'])
 def test_assets_exist_and_are_described(self):
  rows=list(self.art['events'].values())+list(self.art['watchlist'].values())
  for a in rows:
   self.assertRegex(a['src'],r'^/assets/event-sketches/[a-z0-9-]+\.webp$');self.assertTrue((ROOT/a['src'].lstrip('/')).exists(),a['src']);self.assertGreater(len(a['alt']),25);self.assertGreater(a['width'],0);self.assertGreater(a['height'],0)
 def test_native_labeled_calendar_controls(self):
  page=(ROOT/'calendar.html').read_text();self.assertIn('select name="month"',page);self.assertIn('Choose a month',page);self.assertIn('input name="from" type="date"',page);self.assertIn('data-sketch-icon="calendar"',page)
 def test_art_has_no_visible_process_labels(self):
  self.assertNotIn('AI ink-and-watercolor',(ROOT/'calendar.html').read_text());self.assertNotIn('AI sketch · inspired by this event',(ROOT/'assets/events.js').read_text());self.assertIn('AI-generated',self.art['disclosure'])
 def test_related_sessions_reuse_only_named_reviewed_studies(self):
  for row in list(self.art['events'].values())+list(self.art['watchlist'].values()):
   if 'reusedFromEvent' in row:self.assertEqual(row['src'],self.art['events'][row['reusedFromEvent']]['src'])
   if 'reusedFrom' in row:self.assertTrue((ROOT/row['reusedFrom'].lstrip('/')).exists())
 def test_watercolors_stay_outside_closed_details(self):
  js=(ROOT/'assets/events.js').read_text();self.assertIn("if(art){card.append(art);card.classList.add('has-sketch')}",js);self.assertNotIn('more.append(art)',js)
 def test_original_event_specific_art_is_preserved(self):
  preservation=json.loads((ROOT/'docs/event-watercolor-restoration-2026-10-06.json').read_text())['preservedOriginalMappings']
  for group,rows in preservation.items():
   for eid,src in rows.items():self.assertEqual(self.art[group][eid]['src'],src)
 def test_external_state_directory_selector(self):self.assertIn("stateBox=document.querySelector('[data-state-index]')",(ROOT/'assets/events.js').read_text())
 def test_event_map_hook_and_toggle(self):
  page=(ROOT/'calendar.html').read_text();self.assertIn('data-calendar-view="map"',page);self.assertIn('event-map-view',page);self.assertIn('AUsomeEventMap.render(mapBox,events,showEvent)',(ROOT/'assets/events.js').read_text())
 def test_month_filter_and_return_focus(self):
  js=(ROOT/'assets/events.js').read_text();self.assertIn("e.start.slice(0,7)===v.month",js);self.assertIn('focus({preventScroll:true})',js)
if __name__=='__main__':unittest.main()
