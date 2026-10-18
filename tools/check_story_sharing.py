#!/usr/bin/env python3
"""Validate authored sharing packages, including static copy and approved asset records.

Editorial judgment, account identity, rights evidence and a platform's actual rendering
still require review. Existing stories may keep the generic link-sharing fallback.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from lxml import html
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def check(root):
    errors = []
    packages = 0
    files = 0
    approvals = json.loads((ROOT / 'docs/story-sharing-approvals.json').read_text())['packages']
    found_packages = set()
    for path in root.rglob('*.html'):
        relative = path.relative_to(root)
        if any(part.startswith('.') or part in {'_site', 'docs', 'tests', 'node_modules'} for part in relative.parts):
            continue
        page = html.fromstring(path.read_text())
        blocks = page.xpath('//main//section[contains(concat(" ",normalize-space(@class)," ")," aal-story-share ")]')
        if not blocks:
            continue
        packages += len(blocks)
        name = relative.as_posix()
        found_packages.add(name)

        def require(condition, message):
            if not condition:
                errors.append(f'{name}: {message}')

        require(len(blocks) == 1, 'Expected one authored sharing package')
        record = approvals.get(name, {})
        require(bool(record), 'Authored package is missing its reviewed provenance registration')
        provenance = {}
        if record:
            provenance_path = (ROOT / record['provenance']).resolve()
            if provenance_path.is_relative_to(ROOT / 'docs') and provenance_path.is_file():
                provenance = json.loads(provenance_path.read_text())
            else:
                require(False, 'Provenance must be a present internal record under docs/')
        approved = set(provenance.get('scoped_organic_sharing_intent', {}).get('assets_only', []))
        outputs = {item['path']: item for item in provenance.get('outputs', [])}
        observed_downloads = set()
        canonical = page.xpath('//link[@rel="canonical"]/@href')
        require(len(canonical) == 1, 'Expected one canonical story URL')
        for block in blocks:
            caption = block.xpath('.//*[@data-share-caption]')
            require(len(caption) == 1, 'Expected one reviewed caption')
            if caption:
                copy = caption[0].text_content().strip()
                require(len(copy) > 100, 'Caption needs a specific reader benefit and credit')
                require('An AUsome Life' in copy and '@anausomelife' in copy, 'Caption is missing publication credit')
                require(bool(canonical) and canonical[0] in copy, 'Caption is missing the canonical article link')
            require(bool(block.get('data-share-summary', '').strip()), 'Missing short native-share summary')
            for expression, label in [
                ('.//button[@data-copy-link]', 'copy-link button'),
                ('.//button[@data-copy-caption]', 'copy-caption button'),
                ('.//*[@role="status"]', 'announced copy status'),
                ('.//*[@data-share-fallback]//textarea[@readonly]', 'manual-copy fallback'),
            ]:
                require(bool(block.xpath(expression)), 'Missing ' + label)
            for button in block.xpath('.//button'):
                require(button.get('type') == 'button', 'Sharing buttons must not submit forms')
                require(button.get('hidden') is not None, 'Script-only controls must start hidden')
                target = button.get('data-copy-share-text')
                if target:
                    found = block.xpath('.//*[@id=$target]', target=target)
                    require(len(found) == 1 and bool(found[0].text_content().strip()), f'Copy target is missing: {target}')
            for download in block.xpath('.//a[@download]'):
                href = download.get('href', '')
                url = urlsplit(href)
                asset = (root / url.path.lstrip('/')).resolve()
                safe = href.startswith('/') and not url.netloc and not url.query and not url.fragment and asset.is_relative_to(root.resolve())
                require(safe, 'Sharing downloads must be local reviewed files')
                if not safe:
                    continue
                require(asset.is_file(), f'Missing sharing download: {href}')
                if not asset.is_file():
                    continue
                files += 1
                key = asset.relative_to(root.resolve()).as_posix()
                observed_downloads.add(key)
                require(key in approved and key in outputs, f'Download lacks exact-file organic sharing approval: {href}')
                if key in outputs:
                    require(hashlib.sha256(asset.read_bytes()).hexdigest() == outputs[key]['sha256'], f'Download changed after review: {href}')
                preview = block.xpath('.//img[@src=$src]', src=href)
                require(len(preview) == 1 and bool(preview[0].get('alt', '').strip()), f'Missing visible asset preview and alt: {href}')
                with Image.open(asset) as image:
                    image.load()
                    require(image.format == 'PNG', f'Expected a PNG social graphic: {href}')
                    if key in outputs:
                        require([image.width, image.height] == outputs[key]['dimensions'], f'Dimensions differ from approved record: {href}')
                    if preview:
                        require((str(image.width), str(image.height)) == (preview[0].get('width'), preview[0].get('height')), f'Preview dimensions differ: {href}')
            if block.xpath('.//a[@download]'):
                permission = block.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," aal-share-permission ")]')
                require(bool(permission) and 'organic' in permission[0].text_content().lower(), 'Downloads need explicit organic-sharing scope')
        require(observed_downloads == approved, 'Published downloads differ from the approved set')
    for missing in approvals.keys() - found_packages:
        errors.append(f'{missing}: Registered sharing package is missing from its story')
    return {'packages': packages, 'downloads': files, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = check(args.root.resolve())
    print('STORY_SHARING_SUMMARY', json.dumps(result))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
