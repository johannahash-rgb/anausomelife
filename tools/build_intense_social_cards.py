#!/usr/bin/env python3
"""Build original, type-only INTENSE story graphics with exact-file provenance.

The temporary vector PDF uses exact text and embedded fonts, then exports at
72 dpi to the requested PNG sizes. No photographs, logos, resource artwork or
generated food imagery are included. Reruns require a fresh visual review.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image
from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/family-notes"
PROVENANCE = ROOT / "docs/intense-social-card-provenance.json"
CANONICAL = "https://anausomelife.com/little-things-that-help.html"
WIDTH = 1080
MARGIN = 88
COLORS = {
    "cream": HexColor("#f7f4ec"),
    "navy": HexColor("#173c4c"),
    "pine": HexColor("#2e513f"),
    "pink": HexColor("#c88691"),
}
SPECS = [
    {"key": "feed", "height": 1350, "safe_top": 80, "safe_bottom": 80,
     "brand": 216, "accent": 278, "headline": [468, 597], "cta": [827, 885],
     "credit": 1083, "url": 1130, "notice": 1230},
    {"key": "story", "height": 1920, "safe_top": 220, "safe_bottom": 280,
     "brand": 398, "accent": 470, "headline": [702, 839], "cta": [1114, 1172],
     "credit": 1395, "url": 1442, "notice": 1570},
]
TEXT = [
    "INTENSE STRAWBERRY MILK",
    "A familiar drink.",
    "A preferred straw.",
    "Read the kitchen story",
    "+ get free picture cards",
    "An AUsome Life",
    "@anausomelife · anausomelife.com",
    "Independent family note · Milk purchased by us.",
]
ALT = (
    "Cream typographic graphic with navy serif text: A familiar drink. A preferred straw. "
    "A small heading identifies INTENSE STRAWBERRY MILK, above a restrained pink rule. "
    "Pine-green text invites readers to read the kitchen story and get free picture cards. "
    "Credit: An AUsome Life, @anausomelife, anausomelife.com. "
    "Disclosure: Independent family note. Milk purchased by us."
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    selected = {}
    for alias, filename in {
        "IntenseSerif": "LiberationSerif-Regular.ttf",
        "IntenseSans": "LiberationSans-Regular.ttf",
        "IntenseSansBold": "LiberationSans-Bold.ttf",
    }.items():
        locations = [Path("/usr/share/fonts/truetype/liberation2") / filename,
                     Path("/usr/share/fonts/truetype/liberation") / filename,
                     runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / filename]
        source = next((p for p in locations if p.is_file()), None)
        if source is None:
            raise RuntimeError(f"Missing font: {filename}")
        pdfmetrics.registerFont(TTFont(alias, str(source)))
        selected[alias] = {"filename": filename, "sha256": digest(source)}
    return selected


def put_text(c, spec, value, baseline, size, font, color, bounds, tracking=0):
    width = pdfmetrics.stringWidth(value, font, size) + tracking * max(0, len(value) - 1)
    ascent, descent = pdfmetrics.getAscentDescent(font, size)
    box = [(WIDTH - width) / 2, baseline - ascent, (WIDTH + width) / 2, baseline - descent]
    assert MARGIN <= box[0] and box[2] <= WIDTH - MARGIN, (value, box)
    assert spec["safe_top"] <= box[1] and box[3] <= spec["height"] - spec["safe_bottom"], (value, box)
    t = c.beginText(box[0], spec["height"] - baseline)
    t.setFont(font, size)
    t.setFillColor(COLORS[color])
    t.setCharSpace(tracking)
    t.textOut(value)
    c.drawText(t)
    bounds.append({"text": value, "font_px": size, "tracking_px": tracking,
                   "bounds": [round(v, 2) for v in box]})


def make_page(c, spec):
    c.setPageSize((WIDTH, spec["height"]))
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, WIDTH, spec["height"], stroke=0, fill=1)
    bounds = []
    put_text(c, spec, TEXT[0], spec["brand"], 27, "IntenseSansBold", "pine", bounds, tracking=3)
    c.setFillColor(COLORS["pink"])
    c.rect((WIDTH - 116) / 2, spec["height"] - spec["accent"], 116, 5, stroke=0, fill=1)
    for value, baseline in zip(TEXT[1:3], spec["headline"]):
        put_text(c, spec, value, baseline, 112, "IntenseSerif", "navy", bounds)
    for value, baseline in zip(TEXT[3:5], spec["cta"]):
        put_text(c, spec, value, baseline, 42, "IntenseSans", "pine", bounds)
    put_text(c, spec, TEXT[5], spec["credit"], 41, "IntenseSerif", "navy", bounds)
    put_text(c, spec, TEXT[6], spec["url"], 27, "IntenseSans", "pine", bounds)
    put_text(c, spec, TEXT[7], spec["notice"], 26, "IntenseSans", "navy", bounds)
    for previous, following in zip(bounds, bounds[1:]):
        assert previous["bounds"][3] < following["bounds"][1], (previous, following)
    c.showPage()
    return bounds


def main():
    fonts = register_fonts()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    geometry = {}
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("pdftoppm is required for exact PNG export")
    with tempfile.TemporaryDirectory(prefix="intense-social-") as temporary:
        source = Path(temporary) / "intense-social-cards.pdf"
        c = canvas.Canvas(str(source), pagesize=(WIDTH, 1350), pageCompression=1, invariant=1)
        c.setAuthor("An AUsome Life")
        c.setCreator("An AUsome Life")
        c.setTitle("INTENSE strawberry milk: independent kitchen story and free picture cards")
        for spec in SPECS:
            geometry[spec["key"]] = make_page(c, spec)
        c.save()
        pdf = PdfReader(source)
        assert len(pdf.pages) == len(SPECS)
        for index, (page, spec) in enumerate(zip(pdf.pages, SPECS), start=1):
            assert list(page.mediabox) == [0, 0, WIDTH, spec["height"]]
            extracted = page.extract_text()
            for value in TEXT:
                assert value in extracted, (spec["key"], "missing text", value)
            destination = OUTPUT / f"intense-strawberry-share-{spec['key']}.png"
            prefix = Path(temporary) / spec["key"]
            subprocess.run([renderer, "-r", "72", "-f", str(index), "-l", str(index),
                            "-singlefile", "-png", str(source), str(prefix)], check=True)
            shutil.copyfile(prefix.with_suffix(".png"), destination)
            with Image.open(destination) as im:
                im.load()
                assert im.format == "PNG" and im.size == (WIDTH, spec["height"])
    outputs = []
    for spec in SPECS:
        path = OUTPUT / f"intense-strawberry-share-{spec['key']}.png"
        outputs.append({"path": path.relative_to(ROOT).as_posix(),
                        "dimensions": [WIDTH, spec["height"]], "bytes": path.stat().st_size,
                        "sha256": digest(path), "alt_text": ALT,
                        "critical_safe_area": {"top_px": spec["safe_top"], "bottom_px": spec["safe_bottom"], "side_px": MARGIN}})
    record = {
        "title": "INTENSE strawberry milk story graphics: provenance and scoped sharing intent",
        "created": "2026-10-18",
        "publication": "An AUsome Life",
        "canonical_story": CANONICAL,
        "owner_direction": "Current-session instruction to edit the INTENSE strawberry story, remove repetition, strengthen sharing and send it to the brand's PR team with encouragement to share.",
        "generator": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": digest(Path(__file__).resolve()),
        "method": "Original code-native typography and one vector accent rule. Exact text and embedded fonts rendered from a temporary vector PDF at 72 dpi to the requested PNG sizes. Reproducible source is the generator; the intermediate PDF is not hosted.",
        "layout_reasoning": [
            "The small ordinary-text product name supplies brand recognition without reproducing the brand's logo or trade dress.",
            "A large two-line serif headline preserves an ordinary family moment without asserting a medical benefit or a demonstrated result.",
            "The reader benefit is explicit: a kitchen story and free picture cards. These graphics promote the resource; they are not communication cards themselves.",
            "Cream, coastal navy, pine and a narrow strawberry-pink rule retain the publication's restrained New England identity.",
            "Generous whitespace and the tall layout's reserved top and bottom regions keep essential text clear of common interface overlays; this is a design choice, not a guarantee about every platform.",
            "The graphic carries independent publication credit and the actual purchase disclosure. It contains no demonstration, depiction or recommendation to modify a bottle cap.",
        ],
        "sources": [],
        "new_generation": False,
        "family_photographs_used_in_social_downloads": False,
        "venue_logos_used_in_social_downloads": False,
        "brand_logos_used_in_social_downloads": False,
        "third_party_artwork_used": False,
        "fonts_embedded_in_source": fonts,
        "public_notice": TEXT[7],
        "scoped_organic_sharing_intent": {
            "assets_only": [item["path"] for item in outputs],
            "permitted_intended_use": "Share these two finished PNG graphics unchanged in organic social posts or Stories, with An AUsome Life / @anausomelife credit and a link to https://anausomelife.com/little-things-that-help.html. Preserve all embedded text, credit and the independent purchase disclosure.",
            "scope_limits": "Applies only to the two exact finished PNG files recorded here. No rights are granted to family photographs, other website or archive content, brand logos, source files, paid advertising, merchandising, edits or other reuse. This is not permission to present an official brand partnership or endorsement, and grants no rights the publication does not control.",
            "authorization_basis": "Owner-directed current-session sharing package and PR outreach, using an original publication-created typographic composition and ordinary-text editorial product identification.",
        },
        "outputs": outputs,
        "validation": {
            "automated": "Exact text extracted from both vector pages; all text bounds checked against safe areas and neighboring text; final PNG format, dimensions and output hashes verified.",
            "visual_review": "Pending final inspection of both rendered PNGs."
        },
        "layout_bounds": geometry,
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    for item in outputs:
        print(f"{item['path']} | {item['dimensions']} | {item['bytes']:,} bytes")


if __name__ == "__main__":
    main()
