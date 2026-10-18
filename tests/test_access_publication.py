"""Publication integration checks; these do not measure rendered browser layout."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('edition', ROOT / '.github/scripts/prepare_curated_edition.py')
edition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edition)

class Publication(unittest.TestCase):
    def test_heading_breaks_remain_readable_without_line_break_layout(self):
        source='<h1>Wandering is<br>the activity.</h1><h2>Something<br><em>worth sharing.</em></h2>'
        result=edition.readable_heading_breaks(source)
        self.assertIn('is<br> the activity.',result)
        self.assertIn('Something<br> <em>worth',result)
        self.assertEqual(edition.readable_heading_breaks(result),result)

    def test_complete_pages_get_tools_once_and_redirects_and_fragments_stay_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            full = '<!doctype html><html><head><title>Page</title></head><body><main><h1>Page</h1></main></body></html>'
            # This generic nested-page fixture must not impersonate the media
            # template, whose required editorial anchors are tested separately.
            documents = {'index.html':full, 'nested/index.html':full,
                         'redirect.html':'<html><head><meta http-equiv="refresh" content="0;url=/"></head></html>',
                         'content/fragment.html':'<main>A reusable fragment</main>', 'docs/private.html':full}
            for path, content in documents.items():
                p = root / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
            edition.prepare(root)
            for path in ('index.html', 'nested/index.html'):
                result = (root / path).read_text()
                self.assertEqual(result.count('/assets/access-tools.js'), 1)
                self.assertEqual(result.count('/assets/access-tools.css'), 1)
                self.assertIn(' defer></script>', result)
                self.assertIn('<main><h1>Page</h1></main>', result)
            for path in ('redirect.html', 'content/fragment.html', 'docs/private.html'):
                self.assertEqual((root / path).read_text(), documents[path])
            first = (root / 'index.html').read_text()
            edition.prepare(root)
            self.assertEqual(first, (root / 'index.html').read_text())

    def test_real_media_template_keeps_tools_and_inquiry_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'media/index.html'
            page.parent.mkdir(parents=True)
            page.write_text((ROOT / 'media/index.html').read_text(encoding='utf-8'), encoding='utf-8')
            edition.prepare(root)
            first = page.read_text(encoding='utf-8')
            for asset in ('access-tools.js', 'access-tools.css', 'growth-readiness.css', 'inquiry-builder.js'):
                self.assertEqual(first.count('/assets/' + asset), 1, asset)
            for identifier in ('products', 'testing', 'press-desk', 'contact', 'editorial-inquiry'):
                self.assertEqual(first.count('id="' + identifier + '"'), 1, identifier)
            self.assertIn('data-brand-banner', first)
            edition.prepare(root)
            self.assertEqual(first, page.read_text(encoding='utf-8'))

    def test_incomplete_media_template_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'media/index.html'
            page.parent.mkdir(parents=True)
            page.write_text('<html><head><title>Media</title></head><body><main><h1>Media</h1></main></body></html>')
            with self.assertRaisesRegex(ValueError, 'Cannot find insertion anchor for products'):
                edition.prepare(root)

    def test_existing_asset_versions_refresh_without_duplicate_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / 'index.html'
            p.write_text('<html><head><link rel="stylesheet" href="/assets/access-tools.css?v=old"></head><body><main>Page</main><script src="/assets/access-tools.js?v=old" defer></script></body></html>')
            edition.prepare(root)
            text = p.read_text()
            self.assertNotIn('?v=old', text)
            self.assertEqual(text.count('/assets/access-tools.js'), 1)
            self.assertEqual(text.count('/assets/access-tools.css'), 1)

    def test_help_and_privacy_have_targets_and_zoom_is_not_restricted(self):
        for path, target in [('accessibility.html', 'reading-tools'), ('privacy.html', 'reading-preferences')]:
            page = (ROOT / path).read_text()
            self.assertIn('id="'+target+'"', page)
            self.assertNotIn('user-scalable=no', page)
            self.assertNotIn('maximum-scale=1', page)
        self.assertIn('data-aal-open-access', (ROOT / 'accessibility.html').read_text())

if __name__ == '__main__':
    unittest.main()
