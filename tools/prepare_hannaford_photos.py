#!/usr/bin/env python3
"""Stage the two selected original breakfast photographs without altering pixels."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SELECTIONS = {
    'IMG_9258.jpeg': 'breakfast-at-checkout.jpeg',
    'IMG_9256.jpeg': 'checkout-total.jpeg',
}

def remove_private_metadata(data):
    if data[:2] != b'\xff\xd8':
        raise ValueError('Expected an original JPEG')
    kept = [data[:2]]
    pos = 2
    while pos < len(data):
        start = pos
        if data[pos] != 0xff:
            raise ValueError('Invalid JPEG marker')
        while data[pos] == 0xff:
            pos += 1
        marker = data[pos]
        pos += 1
        if marker in (0xda, 0xd9):
            kept.append(data[start:])
            break
        length = int.from_bytes(data[pos:pos + 2], 'big')
        end = pos + length
        if length < 2 or end > len(data):
            raise ValueError('Invalid JPEG segment')
        if marker not in (0xe1, 0xed, 0xfe):
            kept.append(data[start:end])
        pos = end
    return b''.join(kept)

def prepare(source):
    assets = []
    destination = ROOT / 'assets/hannaford-maine-breakfast'
    destination.mkdir(parents=True, exist_ok=True)
    for name, output in SELECTIONS.items():
        original = (source / name).read_bytes()
        with Image.open(io.BytesIO(original)) as before:
            before.load()
            if before.getexif().get(274, 1) != 1:
                raise ValueError('Review orientation before removing metadata')
            cleaned = remove_private_metadata(original)
            with Image.open(io.BytesIO(cleaned)) as after:
                after.load()
                assert before.size == after.size and before.mode == after.mode
                assert before.tobytes() == after.tobytes(), 'Photographic pixels changed'
                assert before.info.get('icc_profile') == after.info.get('icc_profile')
                dimensions = list(after.size)
        target = destination / output
        target.write_bytes(cleaned)
        assets.append({
            'source_upload': name,
            'asset': '/' + target.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(original).hexdigest(),
            'published_sha256': hashlib.sha256(cleaned).hexdigest(),
            'dimensions': dimensions,
            'basis': 'Owner supplied the original photograph for the ongoing family-story publication task.',
            'changes': 'Removed EXIF, XMP, IPTC and comment metadata without recompression. Decoded photographic pixels, dimensions, proportions and ICC color profile verified unchanged.',
        })
    record = {
        'article': '/hannaford-maine-breakfast-picnic.html',
        'recorded': '2026-10-18',
        'assets': assets,
        'excluded_uploads': {'IMG_9257.jpeg': 'Near-duplicate breakfast photograph; used to read the Oakhurst cap, not repeated in the article. Original upload remains unchanged.'},
        'sharing_scope': 'Editorial article and site promotion only. Separate text-graphic permission does not grant reuse rights to these photographs.',
        'owner_visit_context': {
            'visit': 'A quick Saturday morning breakfast stop at Hannaford in Maine; no specific branch, picnic table or calendar visit date asserted.',
            'picnic': 'The family found a waterside picnic table and brought their own plates and glasses.',
            'drinks': 'Adults mixed eggnog and cold brew; James had eggnog without coffee.',
            'connection': 'The owner lived in Vermont for a long time and has loved Hannaford for years.',
            'bakery': 'The owner\'s favorite butter rum muffins were sold out; the family still enjoyed breakfast.',
            'james': 'James loves grocery shopping. Other shoppers commented on his enjoyment, and the family proudly shared that he often leads his classroom grocery trips.',
        },
        'photo_evidence': ['Four-pack of assorted muffins, chocolate-frosted donuts, bottled cold brew and eggnog.', 'Oakhurst cap URL and OAK EGG NOG QRT checkout abbreviation.', 'Checkout total $16.73 including displayed $0.92 tax and $0.05 bottle deposit.'],
        'facts_checked': [
            'https://www.oakhurstdairy.com/about-us/',
            'https://www.oakhurstdairy.com/our_products/eggnog/eggnog-3/',
        ],
        'scope_limits': ['No precise store or picnic address inferred.', 'No universal accessibility, noise, service or product-availability claim.', 'No sponsorship, brand endorsement, repost or audience outcome asserted.'],
    }
    (ROOT / 'docs/hannaford-breakfast-photo-provenance.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    print('Prepared two original photographs; decoded pixels and color profiles unchanged.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    prepare(parser.parse_args().source)
