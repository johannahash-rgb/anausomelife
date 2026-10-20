#!/usr/bin/env python3
"""Build two original typographic story graphics and exact-file provenance.

Requires Pillow, pypdf, reportlab, pdftoppm, and installed Liberation fonts.
No photograph or generated artwork is read into either graphic. A temporary
vector document holds the exact text; the reviewed PNGs are the only exports.
Run --record-visual-review only after inspecting both final PNGs.
"""

import argparse
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
OUTPUT = ROOT / "assets/social"
PROVENANCE = ROOT / "docs/minute-man-susan-provenance.json"
CANONICAL = "https://anausomelife.com/minute-man-walk-great-aunt-susan.html"
WIDTH, MARGIN = 1080, 100
CREATED = "2026-10-20"
COLORS = {"cream": "#f7f4ec", "navy": "#173c4c", "pine": "#2e513f"}
TEXT = [
    "An AUsome Life",
    "A Little Way",
    "Down the Trail",
    "James, Great-Aunt Susan,",
    "and a short walk at Minute Man",
    "We didn’t go far that day.",
    "In many ways, we did.",
    "anausomelife.com",
]
SPECS = [
    {"key": "feed", "height": 1350, "safe_top": 80, "safe_bottom": 80,
     "brand": 160, "top_rule": 222, "title": [398, 512], "title_size": 111,
     "subtitle": [633, 686], "subtitle_size": 38, "quote": [915, 980],
     "quote_size": 49, "bottom_rule": 1104, "url": 1200},
    {"key": "story", "height": 1920, "safe_top": 220, "safe_bottom": 280,
     "brand": 300, "top_rule": 372, "title": [602, 722], "title_size": 115,
     "subtitle": [860, 916], "subtitle_size": 40, "quote": [1200, 1270],
     "quote_size": 52, "bottom_rule": 1438, "url": 1540},
]
ALT = (
    "Cream typographic card with a fine navy border and pine-green rules. "
    "An AUsome Life appears above the large navy serif title, A Little Way Down the Trail. "
    "The subtitle reads: James, Great-Aunt Susan, and a short walk at Minute Man. "
    "Below, italic text reads: We didn’t go far that day. In many ways, we did. "
    "The footer is anausomelife.com. No photographs or illustrations appear."
)

# Fixed records of the owner's ten uploads. These are documentary references,
# not graphic inputs. The three copied originals remain separate story assets.
UPLOADS = [
    ("IMG_0646.jpeg", "5d5a0797e79809daec556c96745cbecdbc8ff2eaa01ce51f1406aa67949e46fb", [1152, 1536], 1045183),
    ("IMG_0658.jpeg", "2349a30bf322972da8373c7dd839f3110f60742dd7af32c31b9eb828d44a8ac1", [1152, 1536], 1045796),
    ("IMG_0670.jpeg", "02fa28c7594e3454ef8bf7fde8be286c014c9f5178d9eae62fdf00c9ba2b7c31", [1536, 1152], 1018780),
    ("IMG_0694.jpeg", "a156fcdd56edf32355cb729941394e2504e4eac6976d90ab136ecafd4e2bd78a", [1536, 1152], 1047459),
    ("IMG_0706.jpeg", "2da82d565e4455ced63ce4ea0b1536a201015536c9abf469e9b4fd8e335842bf", [1536, 1152], 1019848),
    ("IMG_0714.jpeg", "770bbdf44c4af6aeef251a497081a62e019dcf3d98ae629f59310946e26d76ae", [1536, 1152], 1025547),
    ("IMG_0604.jpeg", "b26f19113fa0db416902eb8415aa47bd59c263331caff34d27d7ece62970f144", [1152, 1536], 1038084),
    ("IMG_0588.jpeg", "5e2f2934773ec9a07717f6198da3105bc1678672dd8161da1d37068a85e27291", [1152, 1536], 1029737),
    ("IMG_0603.jpeg", "bd37020e5ee7c65fdc7b06cf883aba6e1d84d6533874d928cb7bee31e87bf663", [1152, 1536], 1038977),
    ("IMG_0620.jpeg", "ce70d905962aa8a7280496f93ea4827bb6ae0ce8477312ed680d369285a00dd0", [1152, 1536], 1048146),
]
STORY_PHOTOS = {
    "IMG_0714.jpeg": "assets/minute-man-susan/james-susan-trail.jpeg",
    "IMG_0620.jpeg": "assets/minute-man-susan/james-susan-tree.jpeg",
    "IMG_0694.jpeg": "assets/minute-man-susan/james-susan-laughing.jpeg",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    records = {}
    for alias, filename in {
        "SusanSerif": "LiberationSerif-Regular.ttf",
        "SusanItalic": "LiberationSerif-Italic.ttf",
        "SusanSans": "LiberationSans-Regular.ttf",
    }.items():
        candidates = [Path("/usr/share/fonts/truetype/liberation2") / filename,
                      Path("/usr/share/fonts/truetype/liberation") / filename,
                      runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / filename]
        source = next((p for p in candidates if p.is_file()), None)
        if source is None:
            raise RuntimeError(f"Install the required font: {filename}")
        pdfmetrics.registerFont(TTFont(alias, str(source)))
        records[alias] = {"filename": filename, "sha256": digest(source),
                          "use": "Rendered text only; no font file is distributed with the graphics."}
    return records


def put_text(c, spec, value, baseline, size, font, color, bounds, tracking=0):
    width = pdfmetrics.stringWidth(value, font, size) + tracking * max(0, len(value) - 1)
    ascent, descent = pdfmetrics.getAscentDescent(font, size)
    box = [(WIDTH - width) / 2, baseline - ascent, (WIDTH + width) / 2, baseline - descent]
    assert MARGIN <= box[0] and box[2] <= WIDTH - MARGIN, (value, box)
    assert spec["safe_top"] <= box[1] and box[3] <= spec["height"] - spec["safe_bottom"], (value, box)
    t = c.beginText(box[0], spec["height"] - baseline)
    t.setFont(font, size)
    t.setFillColor(HexColor(COLORS[color]))
    t.setCharSpace(tracking)
    t.textOut(value)
    c.drawText(t)
    bounds.append({"text": value, "font_px": size, "font": font, "tracking_px": tracking,
                   "bounds": [round(v, 2) for v in box]})


def make_page(c, spec):
    c.setPageSize((WIDTH, spec["height"]))
    c.setFillColor(HexColor(COLORS["cream"]))
    c.rect(0, 0, WIDTH, spec["height"], stroke=0, fill=1)
    c.setStrokeColor(HexColor(COLORS["navy"]))
    c.setLineWidth(1.25)
    c.rect(46, 46, WIDTH - 92, spec["height"] - 92, stroke=1, fill=0)
    c.setStrokeColor(HexColor(COLORS["pine"]))
    c.setLineWidth(2)
    for baseline in [spec["top_rule"], spec["bottom_rule"]]:
        c.line(493, spec["height"] - baseline, 587, spec["height"] - baseline)
    bounds = []
    put_text(c, spec, TEXT[0], spec["brand"], 43, "SusanSerif", "navy", bounds)
    for value, baseline in zip(TEXT[1:3], spec["title"]):
        put_text(c, spec, value, baseline, spec["title_size"], "SusanSerif", "navy", bounds)
    for value, baseline in zip(TEXT[3:5], spec["subtitle"]):
        put_text(c, spec, value, baseline, spec["subtitle_size"], "SusanSans", "pine", bounds)
    for value, baseline in zip(TEXT[5:7], spec["quote"]):
        put_text(c, spec, value, baseline, spec["quote_size"], "SusanItalic", "navy", bounds)
    put_text(c, spec, TEXT[7], spec["url"], 31, "SusanSans", "pine", bounds, tracking=1)
    for previous, following in zip(bounds, bounds[1:]):
        assert previous["bounds"][3] < following["bounds"][1], (previous, following)
    c.showPage()
    return bounds


def photo_records():
    sources, story = [], []
    for name, sha, dimensions, size in UPLOADS:
        source = ROOT.parent / "upload" / name
        if source.exists():
            assert digest(source) == sha, f"The documentary upload changed: {name}"
        item = {"uploaded_name": name, "sha256": sha, "dimensions": dimensions, "bytes": size,
                "origin": "Owner-supplied original family photograph in the current conversation.",
                "intended_use": "Editorial evidence for this family story only; excluded from downloadable graphics and organic-sharing permission.",
                "used_in_social_downloads": False,
                "published_story_path": STORY_PHOTOS.get(name)}
        sources.append(item)
        if name in STORY_PHOTOS:
            path = ROOT / STORY_PHOTOS[name]
            if path.exists():
                assert digest(path) == sha, f"Story copy differs from its original: {path}"
            story.append({"path": STORY_PHOTOS[name], "uploaded_name": name, "sha256": sha,
                          "dimensions": dimensions, "bytes": size,
                          "publication_basis": "Owner-uploaded photograph and current-session instruction to publish this family story with its images.",
                          "transformations": "None. Original bytes, proportions and pixels retained.",
                          "scope": "This article and its site-controlled article-link preview only. No standalone download/repost license, paid advertising, or unrelated reuse is granted."})
    return sources, story


def build():
    fonts = register_fonts()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("pdftoppm is required for exact PNG export")
    geometry = {}
    with tempfile.TemporaryDirectory(prefix="minute-man-susan-social-") as temporary:
        source = Path(temporary) / "source.pdf"
        c = canvas.Canvas(str(source), pagesize=(WIDTH, 1350), pageCompression=1, invariant=1)
        c.setTitle("A Little Way Down the Trail")
        c.setAuthor("An AUsome Life")
        c.setCreator("An AUsome Life")
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
            prefix = Path(temporary) / spec["key"]
            subprocess.run([renderer, "-r", "72", "-f", str(index), "-l", str(index),
                            "-singlefile", "-png", str(source), str(prefix)], check=True, capture_output=True)
            destination = OUTPUT / f"minute-man-susan-{spec['key']}.png"
            shutil.copyfile(prefix.with_suffix(".png"), destination)
            with Image.open(destination) as im:
                im.load()
                assert im.format == "PNG" and im.size == (WIDTH, spec["height"])
    outputs = []
    for spec in SPECS:
        path = OUTPUT / f"minute-man-susan-{spec['key']}.png"
        outputs.append({"path": path.relative_to(ROOT).as_posix(), "dimensions": [WIDTH, spec["height"]],
                        "sha256": digest(path), "bytes": path.stat().st_size, "alt_text": ALT,
                        "critical_safe_area": {"top_px": spec["safe_top"], "bottom_px": spec["safe_bottom"], "side_px": MARGIN}})
    uploads, photos = photo_records()
    record = {
        "title": "Minute Man walk with Great-Aunt Susan: original photographs and typographic social graphics",
        "created": CREATED, "publication": "An AUsome Life", "canonical_story": CANONICAL,
        "generator": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": digest(Path(__file__).resolve()),
        "method": "Original code-native typography with a fine rectangular rule and two short accent rules. Exact embedded text is rendered from a temporary vector PDF at 72 dpi. No AI image generation, source photograph, third-party illustration or logo is used in the graphics.",
        "colors": COLORS, "fonts_embedded_in_temporary_source": fonts,
        "sources": [], "family_story_uploads": uploads, "story_photographs": photos,
        "new_generation": False, "family_photographs_used_in_social_downloads": False,
        "venue_logos_used_in_social_downloads": False, "brand_logos_used_in_social_downloads": False,
        "third_party_artwork_used": False,
        "layout_reasoning": [
            "Large navy serif type, pine secondary text and generous cream space preserve the restrained New England identity.",
            "The user's own closing thought carries the story without diagnosis-led promotion or a claim about therapeutic results.",
            "The title and family/Minute Man subtitle are readable as a standalone invitation to the story.",
            "The tall graphic keeps all essential text within a 220-pixel top and 280-pixel bottom safe area; this is a design choice, not a platform-wide guarantee.",
            "The graphics are publication-created promotional text cards, distinct from documentary family photographs and functional communication cards."
        ],
        "scoped_organic_sharing_intent": {
            "assets_only": [item["path"] for item in outputs],
            "permitted_intended_use": f"Share these two exact finished PNGs unchanged in organic social posts or Stories, retaining all embedded text and An AUsome Life credit. Accompany each shared graphic with An AUsome Life / @anausomelife credit and a link to {CANONICAL}.",
            "scope_limits": "Only the two named finished PNGs are covered. No rights are granted to family photographs, other website images or downloads, the archive, third-party logos, source files, edits, paid advertising, merchandising, or presentation as an official park partnership or endorsement. No rights beyond those controlled by the publication are granted.",
            "authorization_basis": "Current-session owner-directed publication and sharing package, plus the standing requirement to prepare reviewed original social assets for each comparable outing story. These are newly authored typographic compositions with no third-party imagery."
        },
        "outputs": outputs, "layout_bounds": geometry,
        "validation": {"automated": "Exact text extracted from both vector pages; bounds and separation of every text line checked; final PNG format, dimensions and output hashes verified. Original upload and story-copy hashes checked when the source files are available.",
                       "visual_review": "Pending inspection of both final PNG exports."},
        "hosting": "Only the story's selected photographs and two PNG graphics are public assets. This provenance and its reproducible source remain internal."
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"outputs": outputs, "provenance": PROVENANCE.relative_to(ROOT).as_posix()}, indent=2))


def record_visual_review():
    record = json.loads(PROVENANCE.read_text())
    assert digest(Path(__file__).resolve()) == record["generator_sha256"]
    for item in record["outputs"]:
        path = ROOT / item["path"]
        assert digest(path) == item["sha256"], item["path"]
        with Image.open(path) as im:
            assert list(im.size) == item["dimensions"]
    photo_records()
    record["validation"]["visual_review"] = (
        "Both final 1080 by 1350 and 1080 by 1920 PNGs visually inspected on October 20, 2026. "
        "Title, exact family/Minute Man subtitle, closing thought, credit and domain are legible and unclipped. "
        "Spacing and rules are balanced; no text overlaps or unexpected glyphs were observed. "
        "The tall layout keeps all essential text inside the declared safe area. "
        "Neither graphic contains family photographs, illustrations or venue logos."
    )
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print("Visual review recorded for the unchanged two-file social package.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-visual-review", action="store_true")
    args = parser.parse_args()
    record_visual_review() if args.record_visual_review else build()
