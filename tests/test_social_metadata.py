"""Regression checks for static previews and deployment's explicit image selection."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('social', ROOT / '.github/scripts/enrich_social_meta.py')
social = importlib.util.module_from_spec(spec); spec.loader.exec_module(social)
SELECTIONS = json.loads((ROOT / 'docs/social-preview-selections.json').read_text())

class SocialMetadataTests(unittest.TestCase):
    def setUp(self):
        self.choice = copy.deepcopy(SELECTIONS['pages']['blog.html'])
        self.source = '''<!doctype html><html><head><title>Autumn &amp; the lake</title>
<link href="https://anausomelife.com/example.html" rel="canonical">
<meta content="A family day &amp; a good pause." name="description">
<meta content="" property="og:image"><meta name="og:image" content="old.jpg">
<meta name="twitter:card" content="summary"><meta property="twitter:card" content="old">
<meta name="twitter:image:src" content="obsolete.jpg">
<meta name="theme-color" content="#163b4b"></head><body><h1>Autumn</h1></body></html>'''

    def test_replaces_duplicate_empty_and_outdated_tags_and_escapes_text(self):
        self.choice['alt'] = 'A boat & a sign reading "Lake".'
        result = social.render(self.source, self.choice)
        self.assertEqual(social.check_metadata(result, self.choice), [])
        self.assertIn('A boat &amp; a sign reading &quot;Lake&quot;.', result)
        self.assertIn('name="theme-color"', result)
        self.assertNotIn('obsolete.jpg', result)
        self.assertEqual(result.split('</head>')[1], self.source.split('</head>')[1])
        self.assertEqual(social.render(result, self.choice), result)

    def test_rejects_redirect_noindex_and_foreign_canonical(self):
        for addition in ['<meta http-equiv="refresh" content="0; url=/">',
                         '<meta name="robots" content="noindex,follow">']:
            with self.assertRaises(ValueError):
                social.render(self.source.replace('</head>', addition + '</head>'), self.choice)
        with self.assertRaises(ValueError):
            social.render(self.source.replace('https://anausomelife.com/example.html', 'https://other.example/page'), self.choice)

    def test_missing_asset_wrong_dimensions_mime_and_changed_bytes_fail(self):
        for key, value in [('image','/assets/does-not-exist.jpg'), ('width',1),
                           ('mime','image/png'), ('sha256','0' * 64), ('alt','')]:
            changed = dict(self.choice); changed[key] = value
            with self.assertRaises((ValueError, OSError)):
                social.validate_asset(ROOT, changed)
        with self.assertRaises(ValueError): social.local_file(ROOT, '/../outside.jpg')

    def test_corrupt_image_fails_full_decode(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / self.choice['image'].lstrip('/')
            path.parent.mkdir(parents=True)
            original = (ROOT / self.choice['image'].lstrip('/')).read_bytes()
            path.write_bytes(original[:len(original)//2])
            with self.assertRaises((OSError, ValueError)):
                social.validate_asset(root, self.choice)

    def test_unknown_pages_never_receive_a_guessed_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root/'unselected.html'; path.write_text(self.source)
            result = social.apply(root, {'pages': {}})
            self.assertEqual(result['changed'], 0)
            self.assertEqual(path.read_text(), self.source)

    def test_all_selected_static_pages_and_images_are_valid(self):
        result = social.apply(ROOT, SELECTIONS, check=True)
        self.assertEqual(result['errors'], [])
        for relative, choice in SELECTIONS['pages'].items():
            source = (ROOT / relative).read_text()
            self.assertEqual(social.render(source, choice), source, relative)
            _, _, values = social.desired_metadata(source, choice)
            self.assertLessEqual(len(values['twitter:title']), 70)
            self.assertLessEqual(len(values['twitter:description']), 200)
            self.assertNotRegex(' '.join(values.values()).lower(), r'johannah|jo hannah|johannahash')
        self.assertGreater(len({v['image'] for v in SELECTIONS['pages'].values()}), 50)

if __name__ == '__main__': unittest.main()
