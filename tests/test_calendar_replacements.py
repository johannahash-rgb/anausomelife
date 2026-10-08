"""Verified replacement events keep attendance requirements and scoped access tags."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    'raisingharts-sensory-play-2026-10-11',
    'bci-worcester-halloween-2026-10-17',
    'bci-fitchburg-halloween-2026-10-27',
    'bci-lowell-halloween-2026-10-29',
}


class CalendarReplacementTests(unittest.TestCase):
    def test_additions_are_complete_and_discoverable(self):
        data = json.loads((ROOT / 'data/events.json').read_text())
        metadata = json.loads((ROOT / 'data/event-filters.json').read_text())['events']
        art = json.loads((ROOT / 'data/event-illustrations.json').read_text())['events']
        search = json.loads((ROOT / 'data/site-search/replacement-events-20261008.json').read_text())
        by_id = {event['id']: event for event in data['events']}
        self.assertEqual({row['url'] for row in search}, {'/calendar.html#event-' + key for key in IDS})
        self.assertTrue(any('replacement-events-20261008.json' in path for path in json.loads((ROOT / 'data/site-index-manifest.json').read_text())))
        for key in IDS:
            event = by_id[key]
            self.assertFalse(event['reviewRequired'])
            self.assertIn(event['sourceId'], {source['id'] for source in data['sources']})
            self.assertIn(key, art)
            self.assertEqual(metadata[key]['ageGroups'], ['children', 'families'])
            self.assertNotIn('wheelchair-step-free', metadata[key]['accessFeatures'])
            if key.startswith('bci-'):
                self.assertEqual(event['costCategory'], 'free')
                self.assertIn('Drop in', event['registration'])
            else:
                self.assertEqual(event['costCategory'], 'paid')
                self.assertIn('waiver', event['registration'])
        self.assertFalse(any(key.startswith('springfield-museums-sensory-') for key in by_id))


if __name__ == '__main__':
    unittest.main()
