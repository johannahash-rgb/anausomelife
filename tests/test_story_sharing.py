"""Release checks catch lost share packages and unreviewed downloadable images."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sharing', ROOT / 'tools/check_story_sharing.py')
sharing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sharing)
STORY = 'congdons-doughnuts-wells-maine.html'


class StorySharingTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        packages = json.loads((ROOT / 'docs/story-sharing-approvals.json').read_text())['packages']
        self.package_count = len(packages)
        files = set(packages)
        self.download_count = 0
        for record in packages.values():
            provenance = json.loads((ROOT / record['provenance']).read_text())
            assets = provenance['scoped_organic_sharing_intent']['assets_only']
            files.update(assets)
            self.download_count += len(assets)
        for relative in files:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def tearDown(self):
        self.folder.cleanup()

    def test_reviewed_static_package_is_complete(self):
        result = sharing.check(self.root)
        self.assertEqual(result, {'packages': self.package_count, 'downloads': self.download_count, 'errors': []})

    def test_regeneration_cannot_silently_drop_the_package(self):
        (self.root / STORY).write_text('<html><main><h1>Story remains</h1></main></html>')
        self.assertTrue(any('missing from its story' in error for error in sharing.check(self.root)['errors']))

    def test_modified_download_needs_another_review(self):
        path = self.root / 'downloads/congdons-social-feed.png'
        # Appending bytes leaves a decodable PNG: the release gate must compare
        # reviewed bytes as well as image dimensions and its readable header.
        path.write_bytes(path.read_bytes() + b'changed after approval')
        self.assertTrue(any('changed after review' in error for error in sharing.check(self.root)['errors']))

    def test_broken_copy_target_and_missing_credit_fail(self):
        path = self.root / STORY
        source = path.read_text().replace('data-copy-share-text="congdons-story-caption"', 'data-copy-share-text="missing-caption"')
        source = source.replace('From An AUsome Life · @anausomelife', 'Credit removed')
        path.write_text(source)
        errors = sharing.check(self.root)['errors']
        self.assertTrue(any('Copy target is missing' in error for error in errors))
        self.assertTrue(any('missing publication credit' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
