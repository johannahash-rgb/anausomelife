#!/usr/bin/env python3
"""Build precise Safe Haven resource graphics and a separate site link preview.

Only the two social resource PNGs have scoped organic sharing intent. The link
preview uses the whole authorized documentary photograph and is site-only.
Run --record-visual-review only after inspecting all three final PNGs.
"""

from pathlib import Path
import argparse
import json
import shutil
import subprocess
import tempfile

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from build_thrift_shop_choice_board import (
    ROOT, COLORS, CHOICES, URL, atlas_art, digest, output_record, register_fonts, source_records,
)


WIDTH, MARGIN = 1080, 64
SOURCE = ROOT / "docs/safe-haven-social-cards-source.pdf"
PROVENANCE = ROOT / "docs/safe-haven-social-card-provenance.json"
OG_SOURCE = ROOT / "docs/safe-haven-social-preview-source.pdf"
OG_PNG = ROOT / "assets/safe-haven-wells/social-preview.png"
PHOTO = ROOT / "assets/safe-haven-wells/family-at-the-shop.jpeg"
PHOTO_HASH = "efb3582aff86f3db2ed0d7523abc21f09b66033592ed87bf7e516a962e60b9e5"
LAYOUTS = [
    {"key": "feed", "height": 1350, "safe_top": 38, "safe_bottom": 44,
     "eyebrow": 64, "title": 149, "title_size": 80, "detail": 207, "subtitle": 269,
     "grid_top": 307, "card_height": 264, "art_size": 194, "row_gap": 22,
     "words": 919, "cta": 982, "url": [1042, 1084], "credit": 1150, "notice": [1210, 1246, 1282]},
    {"key": "story", "height": 1920, "safe_top": 220, "safe_bottom": 280,
     "eyebrow": 265, "title": 363, "title_size": 86, "detail": 426, "subtitle": 496,
     "grid_top": 539, "card_height": 300, "art_size": 226, "row_gap": 24,
     "words": 1226, "cta": 1296, "url": [1361, 1407], "credit": 1476, "notice": [1533, 1569, 1605]},
]


def text(c, spec, value, baseline, size, font="ThriftSans", color="ink", x=WIDTH / 2,
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
        bounds.append({"type": "text", "text": value, "font_px": size, "bounds": [round(v, 2) for v in box]})
    return box


def build_page(c, spec):
    c.setPageSize((WIDTH, spec["height"]))
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, WIDTH, spec["height"], fill=1, stroke=0)
    bounds = []
    text(c, spec, "WELLS, MAINE", spec["eyebrow"], 26, "ThriftSansBold", "pine", bounds=bounds)
    text(c, spec, "Safe Haven", spec["title"], spec["title_size"], "ThriftSerif", bounds=bounds)
    text(c, spec, "A thrift stop for the cats", spec["detail"], 39, "ThriftSans", bounds=bounds)
    text(c, spec, "Free shopping choice board", spec["subtitle"], 44,
         "ThriftSansBold", "pine", bounds=bounds)
    gap = 24
    card_width = (WIDTH - 2 * MARGIN - gap) / 2
    for index, choice in enumerate(CHOICES):
        x = MARGIN + (index % 2) * (card_width + gap)
        top = spec["grid_top"] + (index // 2) * (spec["card_height"] + spec["row_gap"])
        c.setLineWidth(1.6)
        c.setStrokeColor(COLORS["line"])
        c.setFillColor(COLORS["white"])
        c.roundRect(x, spec["height"] - top - spec["card_height"], card_width, spec["card_height"], 8, stroke=1, fill=1)
        art_top = top + 10
        atlas_art(c, choice, x + (card_width - spec["art_size"]) / 2, art_top, spec["art_size"], spec["height"], bounds)
        label_box = text(c, spec, choice["label"], top + spec["card_height"] - 18, 39,
                         "ThriftSansBold", x=x + card_width / 2, max_width=card_width - 24, bounds=bounds)
        assert label_box[1] > art_top + spec["art_size"], (choice["label"], "Image-label overlap")
        assert label_box[3] < top + spec["card_height"] - 6
    text(c, spec, "Just looking · Something else · Help · All done", spec["words"], 30,
         "ThriftSansBold", bounds=bounds)
    text(c, spec, "Save for your next browse", spec["cta"], 40,
         "ThriftSansBold", "pine", bounds=bounds)
    text(c, spec, "anausomelife.com/", spec["url"][0], 32, bounds=bounds)
    text(c, spec, "thrift-shop-choice-board.html", spec["url"][1], 32, bounds=bounds)
    c.linkURL(URL, (MARGIN, spec["height"] - spec["url"][1] - 10,
                   WIDTH - MARGIN, spec["height"] - spec["url"][0] + 32), relative=0)
    text(c, spec, "An AUsome Life · @anausomelife", spec["credit"], 29, "ThriftSansBold", bounds=bounds)
    text(c, spec, "Independent resource. Generic illustrations;", spec["notice"][0], 25, color="muted", bounds=bounds)
    text(c, spec, "not current shop stock.", spec["notice"][1], 25, color="muted", bounds=bounds)
    text(c, spec, "Created for a future visit.", spec["notice"][2], 25, color="muted", bounds=bounds)
    c.showPage()
    return bounds


def build_social():
    c = canvas.Canvas(str(SOURCE), pagesize=(WIDTH, LAYOUTS[0]["height"]), pageCompression=1, invariant=1)
    c.setTitle("Safe Haven - free shopping choice board social resource graphics")
    c.setAuthor("An AUsome Life")
    c.setCreator("An AUsome Life")
    c.setSubject("Independent original resource graphics for organic sharing, with generic object illustrations")
    bounds = {spec["key"]: build_page(c, spec) for spec in LAYOUTS}
    c.save()
    pdf = PdfReader(SOURCE)
    assert len(pdf.pages) == 2
    required = ["WELLS, MAINE", "Safe Haven", "A thrift stop for the cats", "Free shopping choice board",
                "Save for your next browse", "An AUsome Life", "@anausomelife", "thrift-shop-choice-board.html",
                "Independent resource.", "Generic illustrations", "Created for a future visit."] + [item["label"] for item in CHOICES]
    outputs = []
    alt = ("An AUsome Life graphic for Safe Haven in Wells, Maine: A thrift stop for the cats. Free shopping choice board. "
           "Four labeled generic object illustrations show Books, Clothes, Lamps, and Baskets. Additional words: Just looking, Something else, Help, All done. "
           "Save for your next browse at anausomelife.com/thrift-shop-choice-board.html. Credit: An AUsome Life, @anausomelife. "
           "Independent resource; generic illustrations are not current shop stock. Created for a future visit.")
    with tempfile.TemporaryDirectory(prefix="safe-haven-social-") as temp:
        for index, spec in enumerate(LAYOUTS):
            page_text = pdf.pages[index].extract_text()
            for value in required:
                assert value in page_text, (spec["key"], value)
            assert tuple(float(v) for v in pdf.pages[index].mediabox[2:]) == (WIDTH, spec["height"])
            prefix = Path(temp) / spec["key"]
            subprocess.run(["pdftoppm", "-r", "72", "-f", str(index + 1), "-l", str(index + 1),
                            "-singlefile", "-png", str(SOURCE), str(prefix)], check=True, capture_output=True)
            output = ROOT / f"downloads/safe-haven-social-{spec['key']}.png"
            shutil.copyfile(prefix.with_suffix(".png"), output)
            assert Image.open(output).size == (WIDTH, spec["height"])
            outputs.append({**output_record(output, alt), "critical_safe_area": {
                "top_px": spec["safe_top"], "bottom_px": spec["safe_bottom"], "side_px": MARGIN}})
    return outputs, bounds


def build_preview():
    assert digest(PHOTO) == PHOTO_HASH, "The authorized full photograph changed; review it before rebuilding."
    original_dimensions = Image.open(PHOTO).size
    assert original_dimensions == (1152, 1536)
    width, height = 1200, 630
    photo_x, photo_top, photo_width, photo_height = 720, 43, 408, 544
    assert photo_width / photo_height == original_dimensions[0] / original_dimensions[1]
    c = canvas.Canvas(str(OG_SOURCE), pagesize=(width, height), pageCompression=1, invariant=1)
    c.setTitle("Safe Haven - Wells, Maine - site link preview")
    c.setAuthor("An AUsome Life")
    c.setCreator("An AUsome Life")
    c.setSubject("Site-only article link preview with the whole authorized original family photograph")
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.drawImage(str(PHOTO), photo_x, height - photo_top - photo_height,
                width=photo_width, height=photo_height, preserveAspectRatio=True, anchor="c")
    bounds = []

    def line(value, baseline, size, font="ThriftSans", color="ink"):
        tw = pdfmetrics.stringWidth(value, font, size)
        asc, desc = pdfmetrics.getAscentDescent(font, size)
        box = [62, baseline - asc, 62 + tw, baseline - desc]
        assert box[2] < photo_x - 35 and box[1] > 43 and box[3] < 587, (value, box)
        c.setFillColor(COLORS[color])
        c.setFont(font, size)
        c.drawString(62, height - baseline, value)
        bounds.append({"text": value, "font_px": size, "bounds": [round(v, 2) for v in box]})

    line("Safe Haven", 209, 82, "ThriftSerif")
    line("Wells, Maine", 263, 34, "ThriftSans", "pine")
    line("Thrift-shop visit + free", 360, 34, "ThriftSansBold")
    line("shopping choice board", 408, 34, "ThriftSansBold")
    line("An AUsome Life", 495, 26, "ThriftSansBold", "pine")
    c.showPage()
    c.save()
    with tempfile.TemporaryDirectory(prefix="safe-haven-preview-") as temp:
        prefix = Path(temp) / "preview"
        subprocess.run(["pdftoppm", "-r", "72", "-singlefile", "-png", str(OG_SOURCE), str(prefix)], check=True, capture_output=True)
        shutil.copyfile(prefix.with_suffix(".png"), OG_PNG)
    assert Image.open(OG_PNG).size == (1200, 630)
    assert digest(PHOTO) == PHOTO_HASH
    return {
        **output_record(OG_PNG, "Safe Haven in Wells, Maine: Thrift-shop visit + free shopping choice board, from An AUsome Life. Beside the text is the complete original portrait photograph of two family members approaching the yellow thrift-shop building, with autumn flowers outside."),
        "source_photo": {"path": str(PHOTO.relative_to(ROOT)), "dimensions": list(original_dimensions),
                         "bytes": PHOTO.stat().st_size, "sha256": PHOTO_HASH,
                         "publication_basis": "Owner-supplied original visit photograph approved for the Safe Haven story and, in the current session, specifically directed for this story's site link preview.",
                         "existing_provenance": "docs/safe-haven-wells-photo-provenance.json"},
        "photo_placement": {"x": photo_x, "top": photo_top, "width": photo_width, "height": photo_height,
                            "aspect_ratio": "3:4", "crop": None, "retouch": False, "replacement_or_generation": False},
        "scope": "Site-controlled Open Graph and article-link preview presentation for the Safe Haven story only, including the preview displayed when its article URL is shared. Excluded from the two-image organic sharing package and permission. No standalone family-photo/composite download or repost license, raw-photo redistribution, paid advertising or unrelated reuse is granted.",
        "layout_reasoning": "Exact 1200 by 630 document layout places the whole portrait photograph at 408 by 544 beside short useful typography. No photo crop, retouch, mask, or synthetic substitute is used.",
        "source_document": {**output_record(OG_SOURCE), "pages": 1, "hosting": "Internal source under docs; not part of the public download package."},
        "text_bounds": bounds, "visual_review": "Pending inspection of the final PNG.",
    }


def build():
    fonts = register_fonts()
    sources = [item for item in source_records() if "cell" in item]
    outputs, bounds = build_social()
    preview = build_preview()
    for source in sources:
        assert digest(ROOT / source["path"]) == source["sha256"]
    record = {
        "title": "Safe Haven shopping choice board social resource graphics", "created": "2026-10-18",
        "generator": str(Path(__file__).relative_to(ROOT)), "generator_sha256": digest(Path(__file__)),
        "shared_art_generator": "tools/build_thrift_shop_choice_board.py",
        "shared_art_generator_sha256": digest(ROOT / "tools/build_thrift_shop_choice_board.py"),
        "resource_url": URL, "article_url": "https://anausomelife.com/safe-haven-thrift-shop-wells-maine.html",
        "source_provenance": "docs/thrift-shop-choice-board-provenance.json", "sources": sources,
        "new_generation": False, "fonts_embedded_in_source": fonts,
        "family_photographs_used_in_social_downloads": False, "venue_logos_used_in_social_downloads": False,
        "code_native_layout_reasoning": [
            "An exact vector/text document composition keeps all resource labels, destination text, credit and qualifications editable and verifiable before raster export.",
            "Four generic approved catalogue objects preview the useful shopping board in a restrained cream, navy and pine composition with white card interiors and natural object colors.",
            "The final Story reserves at least 220 pixels at the top and 280 pixels at the bottom for platform interface overlap; all essential content fits inside those boundaries.",
            "The source PNGs are resource promotions, not shop inventories, official collaborations, advertisements, or evidence the board was used during the photographed visit.",
            "The full original documentary photograph appears only in a separate site link preview, never in either downloadable social resource graphic."
        ],
        "public_notice": "Independent resource. Generic illustrations; not current shop stock. Created for a future visit.",
        "scoped_organic_sharing_intent": {
            "assets_only": ["downloads/safe-haven-social-feed.png", "downloads/safe-haven-social-story.png"],
            "permitted_intended_use": "Organic sharing of these two unchanged finished publication-created promotional PNGs by Safe Haven and other relevant business or community accounts, retaining embedded An AUsome Life / @anausomelife credit, the board destination, exact communication labels and independent/generic/future-visit notice. Accompany the shared graphic with credit and a link to the free board.",
            "scope_limits": "Permission is limited to these exact two finished resource graphics. It does not authorize family-photograph reuse, site-link-preview redistribution as a standalone graphic, other website images or downloads, the archive, third-party logos, raw artwork, edits, paid advertising, merchandising, or presentation as an official partnership. It does not grant rights the publication does not control.",
            "authorization_basis": "Owner direction to make the comparable Safe Haven story and a complete practical sharing package under the current session's brand-repost improvements; original publication-created compositions using reviewed existing generic object artwork."
        },
        "outputs": outputs,
        "source_document": {**output_record(SOURCE), "pages": 2, "hosting": "Internal source under docs; not intended for hosted public downloads."},
        "validation": {"automated": "Both exact canvas sizes, requested text, four category labels, embedded fonts, text bounds and safe areas, absence of image-label overlap, original source hashes, and final PNG dimensions verified.",
                       "visual_review": "Pending final PNG inspection."},
        "layout_bounds": bounds, "site_link_preview": preview,
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"outputs": outputs, "site_link_preview": output_record(OG_PNG), "provenance": str(PROVENANCE.relative_to(ROOT))}))


def record_visual_review():
    record = json.loads(PROVENANCE.read_text())
    for item in record["outputs"] + record["sources"] + [record["site_link_preview"], record["site_link_preview"]["source_photo"]]:
        assert digest(ROOT / item["path"]) == item["sha256"], item["path"]
    record["validation"]["visual_review"] = ("Final 1080 by 1350 and 1080 by 1920 PNGs visually inspected on October 18, 2026. "
        "All four labels, large place/resource headings, legible board destination, credit and independent/generic/future-visit notice confirmed. "
        "Complete objects are clear with no neighboring atlas slivers, subject clipping, text overlap, or unexpected glyphs. Story text and pictures remain inside the declared safe area. Neither social download contains family photographs or a venue logo.")
    record["site_link_preview"]["visual_review"] = ("Final 1200 by 630 PNG visually inspected on October 18, 2026. The full native 3:4 photograph is retained at 408 by 544, with no crop, retouch, mask, or replacement. "
        "Adjacent Safe Haven, location, resource and publication text is clear with no overlap. Original JPEG hash unchanged. This preview remains outside the two-file social sharing permission.")
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print("Recorded visual review for the unchanged social graphics and separate site preview.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-visual-review", action="store_true")
    args = parser.parse_args()
    record_visual_review() if args.record_visual_review else build()
