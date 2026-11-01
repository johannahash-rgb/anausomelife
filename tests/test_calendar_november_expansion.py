"""Classification and holiday navigation integrity for the expanded calendar."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class NovemberExpansion(unittest.TestCase):
 def test_holiday_tags_have_visible_filter_choices(self):
  page=(ROOT/'calendar.html').read_text();metadata=json.loads((ROOT/'data/event-filters.json').read_text())['events']
  for row in metadata.values():
   for tag in row['holidays']:self.assertIn('value="'+tag+'"',page,tag)
 def test_thanksgiving_supported_in_ui_and_search(self):
  self.assertIn('value="thanksgiving"',(ROOT/'calendar.html').read_text())
  self.assertIn("thanksgiving:'Thanksgiving'",(ROOT/'assets/events.js').read_text())
 def test_reader_data_contains_no_research_fields(self):
  data=json.loads((ROOT/'data/events.json').read_text())
  for e in data['events']:
   self.assertFalse(any(k.startswith('_') for k in e),e['id'])
if __name__=='__main__':unittest.main()
