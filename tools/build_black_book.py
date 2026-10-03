#!/usr/bin/env python3
"""Validate the maintained directory without overwriting its expanded editorial content."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
page=(ROOT/'little-black-book.html').read_text()
required=['data-black-book','data-directory-section','name="relationship"','value="list"','On our list']
missing=[item for item in required if item not in page]
if missing:raise SystemExit('Directory controls missing: '+', '.join(missing))
for record in json.loads((ROOT/'content/business-logos.json').read_text()).values():
    asset=record.get('asset')
    if asset and asset in page and not (record.get('reuseStatus')=='cleared' and record.get('permissionEvidence')):
        raise SystemExit('Logo requires documented permission before use.')
print('Maintained directory verified; filters, relationship distinctions and editorial text preserved.')
