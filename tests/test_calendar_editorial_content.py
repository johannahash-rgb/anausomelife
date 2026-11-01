"""Reject scraped page chrome before calendar content can be published.

Titles must be actual concise event names, not page titles, breadcrumbs or
navigation. Fix the source/editorial data; never silently truncate the UI.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHROME = re.compile(r'skip to (?:main )?content|alert close search|event calendar\s*:|news\s*&\s*events\s*:|who we are mission|join our mailing list|portal login donate|just bookmark this page', re.I)

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)

class CalendarEditorialContent(unittest.TestCase):
    def test_all_event_titles_are_editorial_names(self):
        data = json.loads((ROOT / 'data/events.json').read_text())
        for event in data['events']:
            with self.subTest(event=event['id']):
                title = event['title']
                self.assertTrue(title.strip())
                self.assertLessEqual(len(title), 110, 'Review the actual event name; do not truncate mechanically')
                self.assertNotRegex(title, r'https?://|<[^>]+>|[\r\n]')
                for text in strings(event):
                    self.assertIsNone(CHROME.search(text), 'Scraped navigation or announcements in event data')

    def test_marc_pottery_title_is_only_the_event_name(self):
        data = json.loads((ROOT / 'data/events.json').read_text())
        event = next(e for e in data['events'] if e['id'] == 'marc-rec-2026-11-03')
        self.assertEqual(event['title'], 'Pottery Painting at Firestone Café')
        self.assertIn('supported recreation', event['summary'])

if __name__ == '__main__':
    unittest.main()
