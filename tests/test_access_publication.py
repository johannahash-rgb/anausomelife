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
    def test_complete_pages_get_tools_once_and_redirects_and_fragments_stay_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            full = '<!doctype html><html><head><title>Page</title></head><body><main><h1>Page</h1></main></body></html>'
            documents = {'index.html':full, 'media/index.html':full,
                         'redirect.html':'<html><head><meta http-equiv="refresh" content="0;url=/"></head></html>',
                         'content/fragment.html':'<main>A reusable fragment</main>', 'docs/private.html':full}
            for path, content in documents.items():
                p = root / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
            edition.prepare(root)
            for path in ('index.html', 'media/index.html'):
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
