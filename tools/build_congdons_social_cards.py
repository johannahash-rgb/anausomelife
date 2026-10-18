#!/usr/bin/env python3
"""Compose exact Congdon's resource graphics and a separate site link preview.

The two organic-sharing PNGs use approved original board art only. A separate
site-only preview includes the full authorized family photograph and has its own
publication scope. Vector-layout source PDFs stay under docs/. No new imagery
is generated, no family photo is cropped or retouched, and no logo asset is used.
"""

from functools import lru_cache
from io import BytesIO
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

from PIL import Image
from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets/congdons-choice-art"
OUTPUT = ROOT / "downloads"
SOURCE = ROOT / "docs/congdons-social-cards-source.pdf"
PROVENANCE = ROOT / "docs/congdons-social-card-provenance.json"
WIDTH = 1080
MARGIN = 64
COLORS = {
    "cream": HexColor("#f7f4ec"),
    "ink": HexColor("#173c4c"),
    "pine": HexColor("#2e513f"),
    "muted": HexColor("#4b5b61"),
    "line": HexColor("#8a9b8f"),
    "white": HexColor("#ffffff"),
}
FOODS = [
    ("Plain", "plain.webp"),
    ("Honey dip", "honey-dip.webp"),
    ("Chocolate raised", "chocolate-raised.webp"),
    ("Apple fritter", "apple-fritter.webp"),
]
APPROVED_HASHES = {
    "plain.webp": "d686d4b0329568608b47e8503c65a74c55c0a06985f28778cc099c75422a9819",
    "honey-dip.webp": "f2258253f21efab9dcc10e892320fc5d727b79aecb692a67fd90fd9f4eae5a05",
    "chocolate-raised.webp": "ab173b02c9039f376fe317177a9137fbfbb614b7f40a1aa78b6ac366adc10c1f",
    "apple-fritter.webp": "89adfc72c6c6c835ddf23a5219a4822744707921ea3d02189ab52b65976e18a1",
}
LAYOUTS = [
    {
        "key": "feed", "height": 1350,
        "eyebrow": 75, "title": 169, "title_size": 80,
        "subtitle": 235, "subtitle_size": 44,
        "grid_top": 277, "card_height": 300, "art_size": 218, "row_gap": 22,
        "words": 953, "cta": 1016, "url": [1076, 1118], "url_size": 32,
        "credit": 1183, "notice": [1243, 1277],
        "safe_top": 44, "safe_bottom": 44,
    },
    {
        "key": "story", "height": 1920,
        "eyebrow": 267, "title": 365, "title_size": 82,
        "subtitle": 438, "subtitle_size": 46,
        "grid_top": 486, "card_height": 330, "art_size": 248, "row_gap": 24,
        "words": 1235, "cta": 1306, "url": [1379, 1425], "url_size": 34,
        "credit": 1499, "notice": [1565, 1603],
        "safe_top": 220, "safe_bottom": 280,
    },
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    font_specs = {
        "SocialSans": ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
        "SocialSansBold": ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
        "SocialSerif": ("LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
    }
    chosen = {}
    for alias, (preferred, fallback) in font_specs.items():
        candidates = [
            Path("/usr/share/fonts/truetype/liberation2") / preferred,
            Path("/usr/share/fonts/truetype/liberation") / preferred,
            runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / preferred,
            Path("/usr/share/fonts/truetype/dejavu") / fallback,
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            raise RuntimeError(f"Missing embeddable font for {alias}")
        pdfmetrics.registerFont(TTFont(alias, str(path)))
        chosen[alias] = path.name
    return chosen


@lru_cache(maxsize=4)
def printable_art(path):
    im = Image.open(path).convert("RGB")
    # Preserve the entire source composition and its original proportions.
    encoded = BytesIO()
    im.save(encoded, format="JPEG", quality=94, optimize=True)
    encoded.seek(0)
    return ImageReader(encoded)


def text(c, spec, value, baseline, size, font="SocialSans", color="ink", x=WIDTH / 2,
         max_width=WIDTH - 2 * MARGIN, bounds=None):
    width = pdfmetrics.stringWidth(value, font, size)
    assert width <= max_width, (spec["key"], value, width, max_width)
    ascent, descent = pdfmetrics.getAscentDescent(font, size)
    box = [x - width / 2, baseline - ascent, x + width / 2, baseline - descent]
    assert box[0] >= MARGIN and box[2] <= WIDTH - MARGIN, (value, box)
    assert box[1] >= spec["safe_top"] and box[3] <= spec["height"] - spec["safe_bottom"], (value, box)
    c.setFont(font, size)
    c.setFillColor(COLORS[color])
    c.drawCentredString(x, spec["height"] - baseline, value)
    if bounds is not None:
        bounds.append({"type": "text", "text": value, "font_px": size,
                       "bounds": [round(v, 2) for v in box]})
    return box


def food_card(c, spec, label, filename, x, top, width, bounds):
    height = spec["card_height"]
    size = spec["art_size"]
    c.setLineWidth(1.6)
    c.setStrokeColor(COLORS["line"])
    c.setFillColor(COLORS["white"])
    c.roundRect(x, spec["height"] - top - height, width, height, 8, stroke=1, fill=1)
    art_x = x + (width - size) / 2
    art_top = top + 16
    source = ART / filename
    c.drawImage(printable_art(source), art_x, spec["height"] - art_top - size,
                width=size, height=size, preserveAspectRatio=True, anchor="c", mask="auto")
    bounds.append({"type": "illustration", "source": str(source.relative_to(ROOT)),
                   "bounds": [art_x, art_top, art_x + size, art_top + size],
                   "crop": None, "aspect_ratio": 1})
    label_box = text(c, spec, label, top + height - 25, 40,
                     font="SocialSansBold", x=x + width / 2, max_width=width - 24,
                     bounds=bounds)
    assert label_box[1] > art_top + size, (label, "Label intersects illustration")
    assert label_box[3] < top + height - 8, (label, "Label intersects card edge")


def build_page(c, spec):
    c.setPageSize((WIDTH, spec["height"]))
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, WIDTH, spec["height"], fill=1, stroke=0)
    bounds = []
    text(c, spec, "WELLS, MAINE", spec["eyebrow"], 26, "SocialSansBold", "pine", bounds=bounds)
    text(c, spec, "For a Congdon’s stop", spec["title"], spec["title_size"], "SocialSerif", bounds=bounds)
    text(c, spec, "A free picture choice board", spec["subtitle"], spec["subtitle_size"],
         "SocialSansBold", "pine", bounds=bounds)
    col_gap = 24
    card_width = (WIDTH - 2 * MARGIN - col_gap) / 2
    for index, (label, filename) in enumerate(FOODS):
        x = MARGIN + (index % 2) * (card_width + col_gap)
        top = spec["grid_top"] + (index // 2) * (spec["card_height"] + spec["row_gap"])
        food_card(c, spec, label, filename, x, top, card_width, bounds)
    text(c, spec, "Something else · Help · Break · All done", spec["words"], 32,
         "SocialSansBold", bounds=bounds)
    text(c, spec, "Save it. Print it. Take it along.", spec["cta"], 40,
         "SocialSansBold", "pine", bounds=bounds)
    text(c, spec, "anausomelife.com/", spec["url"][0], spec["url_size"], bounds=bounds)
    text(c, spec, "congdons-choice-board.html", spec["url"][1], spec["url_size"], bounds=bounds)
    c.linkURL("https://anausomelife.com/congdons-choice-board.html",
              (MARGIN, spec["height"] - spec["url"][1] - 10,
               WIDTH - MARGIN, spec["height"] - spec["url"][0] + 35), relative=0)
    text(c, spec, "An AUsome Life · @anausomelife", spec["credit"], 29,
         "SocialSansBold", bounds=bounds)
    text(c, spec, "Independent resource. Generic illustrations;", spec["notice"][0], 25,
         color="muted", bounds=bounds)
    text(c, spec, "check the day’s selection.", spec["notice"][1], 25,
         color="muted", bounds=bounds)
    c.showPage()
    return bounds


def create_source_pdf():
    fonts = register_fonts()
    for name, expected in APPROVED_HASHES.items():
        assert digest(ART / name) == expected, f"Approved source artwork changed: {name}"
        with Image.open(ART / name) as im:
            assert im.size == (1254, 1254), (name, im.size)
    c = canvas.Canvas(str(SOURCE), pagesize=(WIDTH, LAYOUTS[0]["height"]), pageCompression=1)
    c.setTitle("Congdon's free choice board - social resource graphics")
    c.setAuthor("An AUsome Life")
    c.setCreator("An AUsome Life")
    c.setSubject("Independent promotional graphics for a free picture communication board")
    geometry = {spec["key"]: build_page(c, spec) for spec in LAYOUTS}
    c.save()
    return fonts, geometry


def export_pngs():
    command = shutil.which("pdftoppm")
    if not command:
        raise RuntimeError("pdftoppm is required for exact PNG exports")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="congdons-social-") as temp:
        prefix = Path(temp) / "social"
        subprocess.run([command, "-r", "72", "-png", str(SOURCE), str(prefix)], check=True)
        for index, spec in enumerate(LAYOUTS, start=1):
            target = OUTPUT / f"congdons-social-{spec['key']}.png"
            shutil.copyfile(Path(temp) / f"social-{index}.png", target)
            with Image.open(target) as im:
                assert im.size == (WIDTH, spec["height"]), (target, im.size)


def verify_pdf_text():
    reader = PdfReader(SOURCE)
    assert len(reader.pages) == 2
    required = [
        "WELLS, MAINE", "For a Congdon’s stop", "A free picture choice board",
        "Plain", "Honey dip", "Chocolate raised", "Apple fritter",
        "Something else · Help · Break · All done", "Save it. Print it. Take it along.",
        "anausomelife.com/", "congdons-choice-board.html", "An AUsome Life · @anausomelife",
        "Independent resource. Generic illustrations;", "check the day’s selection.",
    ]
    for page, spec in zip(reader.pages, LAYOUTS):
        assert list(page.mediabox) == [0, 0, WIDTH, spec["height"]]
        page_text = page.extract_text()
        for phrase in required:
            assert phrase in page_text, (spec["key"], "Missing exact text", phrase)


def write_provenance(fonts, geometry):
    alt = (
        "An AUsome Life graphic for a Congdon’s stop in Wells, Maine, offering a free picture "
        "choice board. Four labeled generic doughnut illustrations: Plain, Honey dip, Chocolate "
        "raised, and Apple fritter. Supporting words: Something else, Help, Break, All done. "
        "Save it. Print it. Take it along. Download at anausomelife.com/congdons-choice-board.html. "
        "Credit: An AUsome Life, @anausomelife. Independent resource; illustrations are generic "
        "and the day’s selection should be checked."
    )
    record = {
        "title": "Congdon's social resource graphics - provenance and scoped sharing intent",
        "created": "2026-10-18",
        "publication": "An AUsome Life",
        "owner_direction": "Current-session direction to improve the reasons and practical means for brands to repost the publication's resource posts.",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "method": "Code-native informational layout: exact text, vector rules/card boundaries and embedded fonts in a source PDF; deterministic 72 dpi PNG exports at requested pixel dimensions.",
        "layout_reasoning": [
            "The destination and free picture-board benefit lead, so the sharing value is legible before reading a caption.",
            "Four familiar food subjects are labeled using the already verified board's exact communication labels.",
            "Warm cream, coastal navy and pine preserve the publication's visual identity; white card interiors retain familiar food colors.",
            "A readable destination, useful action, and embedded publication credit remain on the finished graphic when reposted.",
            "The Story composition reserves at least 220 pixels at the top and 280 pixels at the bottom for platform interface overlap; all essential content lies inside those bounds.",
            "The two assets advertise an independent resource, not an actual menu, same-day selection, official collaboration, sponsored endorsement, or representation of the venue's exact products.",
        ],
        "source_provenance": "docs/congdons-choice-board-provenance.json",
        "sources": [
            {"path": str((ART / filename).relative_to(ROOT)), "label": label,
             "sha256": digest(ART / filename), "dimensions": [1254, 1254],
             "origin": "Existing approved original AI-generated generic food illustration commissioned for the publication's Congdon's communication board.",
             "use": "Full original composition, natural colors and square proportions retained. Only proportional placement and export encoding applied."}
            for label, filename in FOODS
        ],
        "new_generation": False,
        "family_photographs_used_in_social_downloads": False,
        "venue_logos_used_in_social_downloads": False,
        "fonts_embedded_in_source": fonts,
        "public_notice": "Independent resource. Generic illustrations; check the day’s selection.",
        "scoped_organic_sharing_intent": {
            "assets_only": [f"downloads/congdons-social-{spec['key']}.png" for spec in LAYOUTS],
            "permitted_intended_use": "Organic reposting and sharing of these two finished publication-created promotional graphics by Congdon's and other relevant business or community accounts, preserving the embedded An AUsome Life / @anausomelife credit, resource destination, communication labels and independent/generic-illustration notice.",
            "scope_limits": "This scope is limited to these two finished promotional graphics. It does not authorize reuse of family photographs, other website imagery, third-party logos, paid advertising, merchandising, raw artwork redistribution, or presentation as an official partnership. It does not grant rights the publication does not control.",
            "authorization_basis": "Owner-directed brand repost improvements in the current session; original publication-owned composition using the specifically approved original food artwork.",
        },
        "outputs": [
            {"path": f"downloads/congdons-social-{spec['key']}.png", "dimensions": [WIDTH, spec["height"]],
             "bytes": (OUTPUT / f"congdons-social-{spec['key']}.png").stat().st_size,
             "sha256": digest(OUTPUT / f"congdons-social-{spec['key']}.png"), "alt_text": alt,
             "critical_safe_area": {"top_px": spec["safe_top"], "bottom_px": spec["safe_bottom"], "side_px": MARGIN}}
            for spec in LAYOUTS
        ],
        "source_document": {"path": str(SOURCE.relative_to(ROOT)), "pages": 2,
                            "bytes": SOURCE.stat().st_size, "sha256": digest(SOURCE),
                            "hosting": "Internal source under docs; not intended for the hosted public package."},
        "validation": {
            "automated": "Exact requested text and communication labels extracted from both source pages. Image dimensions and source hashes checked. Every text/image layout bound fits its assigned region; card labels do not overlap images or card edges. PNG dimensions verified.",
            "visual_review": "Pending final inspection of both rendered PNGs.",
        },
        "layout_bounds": geometry,
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def build_og_preview():
    """Site-only link preview; its family photo is outside the sharing package."""
    register_fonts()
    photo = ROOT / "assets/congdons-wells/family-by-the-sign.jpeg"
    expected_photo_hash = "d2c90a68001de44533ab0849dbc02b78399047074402d37ecfa3c456891d7624"
    assert digest(photo) == expected_photo_hash, "Approved original photograph changed"
    with Image.open(photo) as original:
        assert original.size == (1536, 1152)
        assert original.getexif().get(274) in (None, 1)
    og_pdf = ROOT / "docs/congdons-og-preview-source.pdf"
    target = ROOT / "assets/congdons-wells/social-preview-v2.png"
    page_width, page_height = 1200, 630
    photo_box = {"x": 480, "top": 60, "width": 680, "height": 510}
    assert photo_box["width"] / photo_box["height"] == 1536 / 1152
    c = canvas.Canvas(str(og_pdf), pagesize=(page_width, page_height), pageCompression=1)
    c.setTitle("Congdon's Wells, Maine - family visit and free picture choice board")
    c.setAuthor("An AUsome Life")
    c.setCreator("An AUsome Life")
    c.setSubject("Site-only article link preview using an authorized original family photograph")
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    # The original JPEG is embedded directly. No crop, mask, retouch or replacement.
    c.drawImage(str(photo), photo_box["x"], page_height - photo_box["top"] - photo_box["height"],
                width=photo_box["width"], height=photo_box["height"], preserveAspectRatio=True, anchor="c")
    text_bounds = []
    left = 52
    for value, baseline, size, font, color in [
        ("Congdon’s", 205, 68, "SocialSerif", "ink"),
        ("Wells, Maine", 253, 31, "SocialSansBold", "pine"),
        ("Family visit + free", 347, 31, "SocialSans", "ink"),
        ("picture choice board", 390, 31, "SocialSans", "ink"),
        ("An AUsome Life", 491, 24, "SocialSansBold", "pine"),
    ]:
        text_width = pdfmetrics.stringWidth(value, font, size)
        ascent, descent = pdfmetrics.getAscentDescent(font, size)
        box = [left, baseline - ascent, left + text_width, baseline - descent]
        assert box[0] >= 40 and box[2] <= photo_box["x"] - 28, (value, box)
        assert box[1] >= 60 and box[3] <= page_height - 60, (value, box)
        c.setFillColor(COLORS[color])
        c.setFont(font, size)
        c.drawString(left, page_height - baseline, value)
        text_bounds.append({"text": value, "font_px": size, "bounds": [round(v, 2) for v in box]})
    c.save()
    command = shutil.which("pdftoppm")
    if not command:
        raise RuntimeError("pdftoppm is required for the link-preview PNG")
    with tempfile.TemporaryDirectory(prefix="congdons-og-") as temp:
        prefix = Path(temp) / "preview"
        subprocess.run([command, "-r", "72", "-singlefile", "-png", str(og_pdf), str(prefix)], check=True)
        shutil.copyfile(Path(temp) / "preview.png", target)
    with Image.open(target) as im:
        assert im.size == (page_width, page_height)
    # Both frozen organic-download graphics remain outside this operation.
    record = json.loads(PROVENANCE.read_text())
    record.pop("family_photographs_used", None)
    record.pop("logos_used", None)
    record["family_photographs_used_in_social_downloads"] = False
    record["venue_logos_used_in_social_downloads"] = False
    record["generator_sha256"] = digest(Path(__file__))
    record["site_link_preview"] = {
        "path": str(target.relative_to(ROOT)),
        "dimensions": [page_width, page_height],
        "bytes": target.stat().st_size,
        "sha256": digest(target),
        "alt_text": "Congdon’s in Wells, Maine: Family visit + free picture choice board, from An AUsome Life. Beside the text is the full original photograph of two family members standing by the yellow Congdon’s Doughnuts sign.",
        "source_photo": {
            "path": str(photo.relative_to(ROOT)), "dimensions": [1536, 1152],
            "bytes": photo.stat().st_size, "sha256": digest(photo),
            "publication_basis": "Owner-supplied original family photograph already approved for the Congdon's article, with current-session direction to use the full image in this article's site link preview.",
        },
        "photo_placement": {**photo_box, "aspect_ratio": "4:3", "crop": None,
                            "retouch": False, "replacement_or_generation": False},
        "scope": "Only site-controlled Open Graph and article-link preview presentation for the An AUsome Life Congdon's article, including the preview displayed with a shared article URL. Excluded from the two-image organic repost download package and its sharing permission. No authorization for standalone family-photo/composite reposting, raw-photo redistribution, paid advertising, or unrelated reuse is granted by this record.",
        "layout_reasoning": "An exact 1200-by-630 information layout puts the entire original 4:3 photograph in a 680-by-510 area beside short reader-facing text. It supplies a landscape metadata canvas without cropping or modifying the article photograph.",
        "source_document": {"path": str(og_pdf.relative_to(ROOT)), "pages": 1,
                            "sha256": digest(og_pdf), "hosting": "Internal source under docs, not part of the public download package."},
        "text_bounds": text_bounds,
        "visual_review": "Pending inspection of the final rendered link-preview image.",
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"{target.relative_to(ROOT)} | {page_width} x {page_height} px | {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--og-only", action="store_true", help="Create only the site link preview; leave organic download graphics unchanged")
    args = parser.parse_args()
    if not args.og_only:
        fonts, geometry = create_source_pdf()
        verify_pdf_text()
        export_pngs()
        write_provenance(fonts, geometry)
        for spec in LAYOUTS:
            output = OUTPUT / f"congdons-social-{spec['key']}.png"
            print(f"{output.relative_to(ROOT)} | {WIDTH} x {spec['height']} px | {output.stat().st_size:,} bytes")
    build_og_preview()
