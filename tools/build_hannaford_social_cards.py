#!/usr/bin/env python3
"""Render original typography for the Hannaford breakfast story.

All drawing is exact text and vector rules in an intermediate PDF. Poppler
renders the requested PNG sizes; no photograph or raster image is edited.
The reproducible source is this file. Every regeneration requires a fresh
visual review of all exported graphics before publication.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "docs/hannaford-social-card-provenance.json"
CANONICAL = "https://anausomelife.com/hannaford-maine-breakfast-picnic.html"
COLORS = {
    "cream": HexColor("#f7f4ec"),
    "navy": HexColor("#173c4c"),
    "pine": HexColor("#2e513f"),
    "rule": HexColor("#9caa98"),
}
SPECS = [
    {
        "key": "feed",
        "path": "downloads/hannaford-breakfast-social-feed.png",
        "width": 1080,
        "height": 1350,
        "side": 88,
        "safe_top": 80,
        "safe_bottom": 48,
        "brand": 175,
        "headline": [338, 450, 562],
        "headline_size": 104,
        "accent": 637,
        "plan": [747, 805, 863],
        "plan_size": 40,
        "eggnog": [961, 1005],
        "eggnog_size": 31,
        "credit": 1126,
        "handle": 1171,
        "url": 1229,
        "notice": 1285,
    },
    {
        "key": "story",
        "path": "downloads/hannaford-breakfast-social-story.png",
        "width": 1080,
        "height": 1920,
        "side": 88,
        "safe_top": 220,
        "safe_bottom": 260,
        "brand": 325,
        "headline": [504, 617, 730],
        "headline_size": 104,
        "accent": 821,
        "plan": [934, 996, 1058],
        "plan_size": 40,
        "eggnog": [1175, 1223],
        "eggnog_size": 33,
        "credit": 1405,
        "handle": 1452,
        "url": 1512,
        "notice": 1598,
    },
    {
        "key": "og",
        "path": "assets/hannaford-maine-breakfast/hannaford-maine-breakfast-og.png",
        "width": 1200,
        "height": 630,
        "side": 64,
        "safe_top": 40,
        "safe_bottom": 30,
    },
]

HEADLINE = ["A grocery run,", "then breakfast", "by the water."]
PLAN = ["Pack your own plates & glasses.", "Pick up breakfast.", "Find a picnic table."]
EGGNOG = ["Eggnog cold brew for us.", "Eggnog for James."]
NOTICE = "Independent family story · October 2026"
SOCIAL_ALT = (
    "Cream typographic graphic with navy serif text reading: A grocery run, then "
    "breakfast by the water. A pine-green heading identifies Hannaford, Maine. "
    "The breakfast idea reads: Pack your own plates & glasses. Pick up breakfast. "
    "Find a picnic table. A note says: Eggnog cold brew for us. Eggnog for James. "
    "Credit: An AUsome Life, @anausomelife. Read the story: anausomelife.com/hannaford/. "
    "Independent family story, October 2026. No photographs or logos appear."
)
OG_ALT = (
    "Cream landscape graphic headed Hannaford, Maine. A navy serif headline reads: "
    "A grocery run, then breakfast by the water. Pine-green text at right reads: "
    "Pack your own plates & glasses. Pick up breakfast. Find a picnic table. "
    "Below it: Eggnog cold brew for us. Eggnog for James. "
    "The footer credits An AUsome Life and @anausomelife and reads: "
    "Read the story: anausomelife.com/hannaford/. No photographs or logos appear."
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    selected = {}
    for alias, filename in {
        "HannafordSerif": "LiberationSerif-Regular.ttf",
        "HannafordSans": "LiberationSans-Regular.ttf",
        "HannafordSansBold": "LiberationSans-Bold.ttf",
    }.items():
        candidates = [
            Path("/usr/share/fonts/truetype/liberation2") / filename,
            Path("/usr/share/fonts/truetype/liberation") / filename,
            runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / filename,
        ]
        source = next((p for p in candidates if p.is_file()), None)
        if source is None:
            raise RuntimeError(f"Missing required font: {filename}")
        pdfmetrics.registerFont(TTFont(alias, str(source)))
        selected[alias] = {"filename": filename, "sha256": digest(source)}
    return selected


def text(c, spec, value, x, baseline, size, font, color, bounds, tracking=0):
    width = pdfmetrics.stringWidth(value, font, size) + tracking * max(0, len(value) - 1)
    ascent, descent = pdfmetrics.getAscentDescent(font, size)
    box = [x, baseline - ascent, x + width, baseline - descent]
    assert spec["side"] <= box[0] and box[2] <= spec["width"] - spec["side"], (value, box)
    assert spec["safe_top"] <= box[1] and box[3] <= spec["height"] - spec["safe_bottom"], (value, box)
    t = c.beginText(x, spec["height"] - baseline)
    t.setFont(font, size)
    t.setFillColor(COLORS[color])
    t.setCharSpace(tracking)
    t.textOut(value)
    c.drawText(t)
    bounds.append({
        "text": value,
        "font_px": size,
        "tracking_px": tracking,
        "bounds": [round(v, 2) for v in box],
    })


def rule(c, spec, x, y, width, thickness=2, color="rule"):
    c.setFillColor(COLORS[color])
    c.rect(x, spec["height"] - y - thickness, width, thickness, stroke=0, fill=1)


def check_text_overlap(bounds):
    for index, item in enumerate(bounds):
        left, top, right, bottom = item["bounds"]
        for other in bounds[index + 1:]:
            a, b, d, e = other["bounds"]
            assert not (left < d and right > a and top < e and bottom > b), (item, other)


def social_page(c, spec):
    bounds = []
    x = spec["side"]
    rule(c, spec, x, spec["brand"] - 78, 904)
    text(c, spec, "Hannaford • Maine", x, spec["brand"], 31, "HannafordSansBold", "pine", bounds, tracking=1.2)
    for value, y in zip(HEADLINE, spec["headline"]):
        text(c, spec, value, x, y, spec["headline_size"], "HannafordSerif", "navy", bounds)
    rule(c, spec, x, spec["accent"], 100, thickness=5, color="pine")
    for value, y in zip(PLAN, spec["plan"]):
        text(c, spec, value, x, y, spec["plan_size"], "HannafordSans", "pine", bounds)
    for value, y in zip(EGGNOG, spec["eggnog"]):
        text(c, spec, value, x, y, spec["eggnog_size"], "HannafordSans", "navy", bounds)
    text(c, spec, "An AUsome Life", x, spec["credit"], 40, "HannafordSerif", "navy", bounds)
    text(c, spec, "@anausomelife", x, spec["handle"], 27, "HannafordSans", "pine", bounds)
    text(c, spec, "Read the story: anausomelife.com/hannaford/", x, spec["url"], 29, "HannafordSans", "navy", bounds)
    text(c, spec, NOTICE, x, spec["notice"], 23, "HannafordSans", "pine", bounds)
    check_text_overlap(bounds)
    return bounds


def og_page(c, spec):
    bounds = []
    x = 72
    text(c, spec, "Hannaford • Maine", x, 90, 25, "HannafordSansBold", "pine", bounds, tracking=1)
    for value, y in zip(HEADLINE, [204, 289, 374]):
        text(c, spec, value, x, y, 77, "HannafordSerif", "navy", bounds)
    c.setFillColor(COLORS["rule"])
    c.rect(698, 170, 2, 317, stroke=0, fill=1)
    for value, y in zip(
        ["Pack your own", "plates & glasses.", "Pick up breakfast.", "Find a picnic table."],
        [179, 220, 286, 342],
    ):
        text(c, spec, value, 757, y, 29, "HannafordSans", "pine", bounds)
    for value, y in zip(EGGNOG, [419, 454]):
        text(c, spec, value, 757, y, 23, "HannafordSans", "navy", bounds)
    rule(c, spec, x, 499, 1056)
    text(c, spec, "An AUsome Life", x, 550, 34, "HannafordSerif", "navy", bounds)
    text(c, spec, "@anausomelife", 901, 548, 24, "HannafordSans", "pine", bounds)
    text(c, spec, "Read the story: anausomelife.com/hannaford/", x, 589, 24, "HannafordSans", "navy", bounds)
    check_text_overlap(bounds)
    return bounds


def png_dimensions(path):
    with path.open("rb") as f:
        header = f.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    return list(struct.unpack(">II", header[16:24]))


def main():
    fonts = register_fonts()
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("pdftoppm is required")
    geometry = {}
    with tempfile.TemporaryDirectory(prefix="hannaford-social-") as tmp:
        temporary = Path(tmp)
        source = temporary / "hannaford-social-cards.pdf"
        c = canvas.Canvas(str(source), pagesize=(1080, 1350), pageCompression=1, invariant=1)
        c.setAuthor("An AUsome Life")
        c.setCreator("An AUsome Life")
        c.setTitle("Hannaford in Maine: breakfast by the water")
        for spec in SPECS:
            c.setPageSize((spec["width"], spec["height"]))
            c.setFillColor(COLORS["cream"])
            c.rect(0, 0, spec["width"], spec["height"], stroke=0, fill=1)
            geometry[spec["key"]] = og_page(c, spec) if spec["key"] == "og" else social_page(c, spec)
            c.showPage()
        c.save()
        pdf = PdfReader(source)
        assert len(pdf.pages) == len(SPECS)
        for index, (page, spec) in enumerate(zip(pdf.pages, SPECS), start=1):
            assert list(page.mediabox) == [0, 0, spec["width"], spec["height"]]
            extracted = page.extract_text()
            for item in geometry[spec["key"]]:
                assert item["text"] in extracted, (spec["key"], "missing exact text", item["text"])
            destination = ROOT / spec["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            prefix = temporary / spec["key"]
            subprocess.run([
                renderer, "-r", "72", "-f", str(index), "-l", str(index),
                "-singlefile", "-png", str(source), str(prefix),
            ], check=True)
            shutil.copyfile(prefix.with_suffix(".png"), destination)
            assert png_dimensions(destination) == [spec["width"], spec["height"]]

    outputs = []
    for spec in SPECS:
        path = ROOT / spec["path"]
        outputs.append({
            "path": spec["path"],
            "role": "open_graph_preview" if spec["key"] == "og" else "organic_social_download",
            "dimensions": png_dimensions(path),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            "alt_text": OG_ALT if spec["key"] == "og" else SOCIAL_ALT,
            "critical_safe_area": {
                "top_px": spec["safe_top"],
                "bottom_px": spec["safe_bottom"],
                "side_px": spec["side"],
            },
        })
    social_paths = [spec["path"] for spec in SPECS if spec["key"] != "og"]
    record = {
        "title": "Hannaford Maine breakfast story graphics: provenance and exact-file sharing scope",
        "created": "2026-10-18",
        "publication": "An AUsome Life",
        "canonical_story": CANONICAL,
        "owner_direction": "Current-session firsthand story about Hannaford breakfast shopping in Maine, a waterside picnic table, plates and glasses brought from home, and eggnog cold brew for the adults with eggnog for James. Standing owner direction requires a reviewed sharing package for a comparable place story.",
        "generator": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": digest(Path(__file__).resolve()),
        "method": "Original code-native exact typography and vector rules, drawn to a temporary PDF with embedded fonts and rendered to PNG using Poppler at 72 dpi. No bitmap editing. The reproducible source is the Python generator; the temporary PDF is not hosted.",
        "sources": [],
        "new_generation": False,
        "family_photographs_used_in_social_downloads": False,
        "brand_logos_used_in_social_downloads": False,
        "venue_logos_used_in_social_downloads": False,
        "third_party_artwork_used": False,
        "fonts_embedded_in_source": fonts,
        "public_notice": NOTICE,
        "layout_reasoning": [
            "A plainly typeset Hannaford, Maine line identifies the subject without copying a logo or suggesting official brand materials.",
            "The oversized serif headline preserves an ordinary family pleasure; the practical takeaway is stated in three short instructions.",
            "The eggnog note describes only the owner's reported drinks and makes no unverified local-manufacturer claim.",
            "Cream, coastal navy, pine and restrained rules preserve the publication's refined New England visual direction without inventing a waterfront image.",
            "The tall export reserves generous top and bottom regions for common interface overlays; this is a design choice, not a guarantee for every platform.",
            "All three graphics include independent publication credit, its handle and the direct short story address anausomelife.com/hannaford/. The social downloads also carry the visit month; the canonical destination is specified in the article's accompanying captions and reuse terms.",
            "The landscape image is a website link-preview asset only. It is not one of the approved organic social downloads and is excluded from the exact-file sharing permission below.",
            "The original documentary photograph remains the article hero; these graphics contain no family or venue depiction.",
        ],
        "scoped_organic_sharing_intent": {
            "assets_only": social_paths,
            "permitted_intended_use": "Share these two finished PNG graphics unchanged in organic social posts or Stories, with An AUsome Life / @anausomelife credit and a link to https://anausomelife.com/hannaford-maine-breakfast-picnic.html. Preserve all embedded text and credit.",
            "scope_limits": "Applies only to downloads/hannaford-breakfast-social-feed.png and downloads/hannaford-breakfast-social-story.png as recorded by their hashes here. No rights are granted to the Open Graph preview, family photographs, other website or archive content, brand logos, source files, paid advertising, merchandising, edits or other reuse. This is not permission to imply a brand partnership or endorsement and grants no rights the publication does not control.",
            "authorization_basis": "Owner-directed current-session firsthand story and standing direction to prepare story-specific sharing materials, using original publication-created typography and ordinary-text editorial brand identification.",
        },
        "outputs": outputs,
        "validation": {
            "automated": "Exact text extracted from all three vector pages; text bounds checked against declared safe regions and pairwise overlap; PNG signatures, dimensions, file sizes and final hashes checked.",
            "visual_review": "Pending inspection of all three final PNG exports.",
        },
        "layout_bounds": geometry,
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    for item in outputs:
        print(f"{item['path']} | {item['dimensions']} | {item['bytes']:,} bytes | {item['sha256']}")


if __name__ == "__main__":
    main()
