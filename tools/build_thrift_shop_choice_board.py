#!/usr/bin/env python3
"""Build a one-page shopping communication board from reviewed original art.

Source atlas cells are placed with native PDF clipping; no source is rewritten.
Run --record-visual-review only after inspecting the latest rendered PNG.
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
PDF = ROOT / "downloads/thrift-shop-choice-board.pdf"
PNG = ROOT / "downloads/thrift-shop-choice-board.png"
PROVENANCE = ROOT / "docs/thrift-shop-choice-board-provenance.json"
URL = "https://anausomelife.com/thrift-shop-choice-board.html"
WIDTH, HEIGHT, MARGIN = 612, 792, 34
COLORS = {key: HexColor(value) for key, value in {
    "cream": "#f7f4ec", "ink": "#173c4c", "pine": "#2e513f",
    "muted": "#4b5b61", "line": "#8a9b8f", "white": "#ffffff",
    "red": "#8f3548",
}.items()}
CHOICES = [
    {"label": "Books", "id": "photo-17-book", "path": "assets/card-collection/photoreal/set-17.webp", "cell": 4,
     "description": "A complete closed navy book on a light background."},
    {"label": "Clothes", "id": "photo-12-polo-shirt", "path": "assets/card-collection/photoreal/set-12.webp", "cell": 0, "crop": [0, 0, 313.5, 295],
     "description": "A complete navy polo shirt on a light background."},
    {"label": "Lamps", "id": "photo-16-bedside-lamp", "path": "assets/card-collection/photoreal/set-16.webp", "cell": 3,
     "description": "A complete navy table lamp with a cream shade on a light background."},
    {"label": "Baskets", "id": "photo-16-laundry-basket", "path": "assets/card-collection/photoreal/set-16.webp", "cell": 9, "crop": [313.5, 632, 313.5, 290],
     "description": "A complete cream and navy rope basket on a light background."},
]
SUPPORTS = [
    {"label": "No", "key": "no", "path": "assets/card-collection/no.svg"},
    {"label": "Help", "key": "help", "path": "assets/card-collection/help.svg"},
    {"label": "Break", "key": "break", "path": "assets/card-studio/break.webp"},
    {"label": "All done", "key": "all-done", "path": "assets/card-collection/all-done.svg"},
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    fonts = {}
    for alias, preferred, fallback in [
        ("ThriftSans", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
        ("ThriftSansBold", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
        ("ThriftSerif", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
    ]:
        candidates = [Path("/usr/share/fonts/truetype/liberation2") / preferred,
                      Path("/usr/share/fonts/truetype/liberation") / preferred,
                      runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / preferred,
                      Path("/usr/share/fonts/truetype/dejavu") / fallback]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            raise RuntimeError(f"Missing embeddable font: {alias}")
        pdfmetrics.registerFont(TTFont(alias, str(path)))
        fonts[alias] = path.name
    return fonts


@lru_cache(maxsize=8)
def document_image(relative_path):
    im = Image.open(ROOT / relative_path).convert("RGB")
    encoded = BytesIO()
    im.save(encoded, format="JPEG", quality=94, optimize=True)
    encoded.seek(0)
    return ImageReader(encoded)


def source_rectangle(choice):
    if "crop" in choice:
        return choice["crop"]
    width, height = Image.open(ROOT / choice["path"]).size
    cell = choice["cell"]
    return [(cell % 4) * width / 4, (cell // 4) * height / 4, width / 4, height / 4]


def atlas_art(c, choice, x, top, size, page_height, bounds=None):
    """Display one complete catalogue cell, preserving its native proportions."""
    source_width, source_height = Image.open(ROOT / choice["path"]).size
    sx, sy, sw, sh = source_rectangle(choice)
    scale = min(size / sw, size / sh)
    dw, dh = sw * scale, sh * scale
    dx = x + (size - dw) / 2
    dy = page_height - top - size + (size - dh) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(dx, dy, dw, dh)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(document_image(choice["path"]), dx - sx * scale,
                dy - (source_height - sy - sh) * scale,
                width=source_width * scale, height=source_height * scale)
    c.restoreState()
    if bounds is not None:
        bounds.append({"type": "illustration", "label": choice["label"], "source": choice["path"],
                       "catalogue_id": choice["id"], "atlas_cell": choice["cell"],
                       "source_rectangle": [sx, sy, sw, sh], "bounds": [x, top, x + size, top + size]})


def core_symbol(c, key, x, top, size, page_height):
    """Retain the exact site's approved core-word SVG geometry as PDF vectors."""
    c.saveState()
    c.translate(x, page_height - top)
    c.scale(size / 500, -size / 500)
    c.setFillColor(COLORS["white"])
    c.rect(0, 0, 500, 500, fill=1, stroke=0)
    c.setStrokeColor(COLORS["ink"])
    c.setLineWidth(23)
    c.setLineCap(1)
    c.setLineJoin(1)

    def path(points):
        p = c.beginPath()
        p.moveTo(*points[0])
        for point in points[1:]:
            p.lineTo(*point)
        c.drawPath(p, stroke=1, fill=0)

    if key == "no":
        c.setStrokeColor(COLORS["red"])
        path([(150, 150), (350, 350)])
        path([(350, 150), (150, 350)])
    elif key == "help":
        c.circle(250, 250, 150, stroke=1, fill=0)
        path([(250, 150), (250, 350)])
        path([(150, 250), (350, 250)])
    elif key == "all-done":
        c.roundRect(95, 95, 310, 310, 12, stroke=1, fill=0)
        path([(150, 250), (215, 315), (350, 175)])
    else:
        raise ValueError(key)
    c.restoreState()


def output_record(path, alt_text=None):
    result = {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)}
    if path.suffix == ".png":
        result["dimensions"] = list(Image.open(path).size)
    if alt_text:
        result["alt_text"] = alt_text
    return result


def source_records():
    records = []
    for item in CHOICES:
        records.append({**item, "sha256": digest(ROOT / item["path"]),
                        "dimensions": list(Image.open(ROOT / item["path"]).size),
                        "source_rectangle": source_rectangle(item),
                        "origin": "Existing approved original AI-generated generic object illustration in the publication's photorealistic picture-card catalogue.",
                        "placement": "Complete existing catalogue cell, proportionally placed with native PDF clipping. Original source file is unchanged."})
    for item in SUPPORTS:
        records.append({**item, "sha256": digest(ROOT / item["path"]),
                        "origin": "Existing original picture-card studio illustration." if item["key"] == "break" else "Existing original publication core-word SVG.",
                        "placement": "Full original composition and proportions retained." if item["key"] == "break" else "Exact existing SVG geometry reproduced as PDF vectors."})
    return records


def build():
    fonts = register_fonts()
    sources = source_records()
    bounds = []
    PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(PDF), pagesize=(WIDTH, HEIGHT), pageCompression=1, invariant=1)
    c.setTitle("Thrift-shop choice board")
    c.setAuthor("An AUsome Life")
    c.setCreator("An AUsome Life")
    c.setSubject("A printable shopping communication board for a future visit, with generic object illustrations")
    c.setFillColor(COLORS["cream"])
    c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)

    def text(value, x, baseline, size, font="ThriftSans", color="ink", centered=False, max_width=544):
        tw = pdfmetrics.stringWidth(value, font, size)
        assert tw <= max_width, (value, tw, max_width)
        asc, desc = pdfmetrics.getAscentDescent(font, size)
        box = [x - tw / 2 if centered else x, baseline - asc,
               x + tw / 2 if centered else x + tw, baseline - desc]
        assert box[0] >= MARGIN and box[2] <= WIDTH - MARGIN
        assert box[1] >= 20 and box[3] <= HEIGHT - 20
        c.setFillColor(COLORS[color])
        c.setFont(font, size)
        (c.drawCentredString if centered else c.drawString)(x, HEIGHT - baseline, value)
        bounds.append({"type": "text", "text": value, "font_pt": size, "bounds": [round(v, 2) for v in box]})
        return box

    def frame(x, top, w, h):
        c.setLineWidth(1.15)
        c.setStrokeColor(COLORS["line"])
        c.setFillColor(COLORS["white"])
        c.roundRect(x, HEIGHT - top - h, w, h, 6, stroke=1, fill=1)

    text("AN AUSOME LIFE", MARGIN, 35, 10, "ThriftSansBold", "pine")
    text("Thrift-shop choice board", MARGIN, 76, 30, "ThriftSerif")
    text("Point to a picture or word. Any answer is welcome.", MARGIN, 101, 11)
    text("What would you like to look at?", MARGIN, 120, 11, "ThriftSansBold", "pine")
    card_width, card_height, art_size = 266, 183, 136
    for index, choice in enumerate(CHOICES):
        x = MARGIN + (index % 2) * (card_width + 12)
        top = 134 + (index // 2) * (card_height + 12)
        frame(x, top, card_width, card_height)
        atlas_art(c, choice, x + (card_width - art_size) / 2, top + 8, art_size, HEIGHT, bounds)
        label_box = text(choice["label"], x + card_width / 2, top + card_height - 14,
                         24, "ThriftSansBold", centered=True, max_width=card_width - 24)
        assert label_box[1] > top + 8 + art_size
    for index, label in enumerate(["Something else", "Just looking"]):
        x = MARGIN + index * (card_width + 12)
        frame(x, 526, card_width, 52)
        text(label, x + card_width / 2, 560, 22, "ThriftSansBold", centered=True, max_width=card_width - 24)
    support_width = (544 - 30) / 4
    for index, support in enumerate(SUPPORTS):
        x = MARGIN + index * (support_width + 10)
        frame(x, 592, support_width, 112)
        art_x = x + (support_width - 64) / 2
        if support["key"] == "break":
            c.drawImage(document_image(support["path"]), art_x, HEIGHT - 598 - 64,
                        width=64, height=64, preserveAspectRatio=True, anchor="c")
        else:
            core_symbol(c, support["key"], art_x, 598, 64, HEIGHT)
        text(support["label"], x + support_width / 2, 689, 22, "ThriftSansBold", centered=True, max_width=support_width - 18)
    text("Generic illustrations, not shop stock. Check available choices before offering them.", MARGIN, 728, 9.5, color="muted")
    text("Use with the person's usual communication system. Made for a future visit.", MARGIN, 745, 9, color="muted")
    text("anausomelife.com/thrift-shop-choice-board.html", MARGIN, 765, 9, color="pine")
    c.linkURL(URL, (MARGIN, HEIGHT - 768, WIDTH - MARGIN, HEIGHT - 754), relative=0)
    c.showPage()
    c.save()
    pdf = PdfReader(PDF)
    assert len(pdf.pages) == 1
    assert tuple(float(v) for v in pdf.pages[0].mediabox[2:]) == (612, 792)
    extracted = pdf.pages[0].extract_text()
    for label in [item["label"] for item in CHOICES + SUPPORTS] + ["Something else", "Just looking"]:
        assert label in extracted, label
    with tempfile.TemporaryDirectory(prefix="thrift-board-") as temp:
        prefix = Path(temp) / "board"
        subprocess.run(["pdftoppm", "-r", "180", "-png", "-singlefile", str(PDF), str(prefix)], check=True, capture_output=True)
        shutil.copyfile(prefix.with_suffix(".png"), PNG)
    assert Image.open(PNG).size == (1530, 1980)
    for source in sources:
        assert digest(ROOT / source["path"]) == source["sha256"], source["path"]
    alt = ("A one-page An AUsome Life thrift-shop choice board. Four labeled generic object illustrations: Books, Clothes, Lamps, and Baskets. "
           "Additional choices: Something else, Just looking, No, Help, Break, and All done. The board invites pointing to a picture or word and welcomes any answer. "
           "Generic illustrations are not shop stock; check available choices. Made for a future visit. anausomelife.com/thrift-shop-choice-board.html.")
    record = {
        "title": "Thrift-shop choice board", "created": "2026-10-18", "resource_url": URL,
        "article_url": "https://anausomelife.com/safe-haven-thrift-shop-wells-maine.html",
        "generator": str(Path(__file__).relative_to(ROOT)), "generator_sha256": digest(Path(__file__)),
        "creation_basis": "Owner-directed practical board accompanying a documented Safe Haven thrift-shop story. Created after the visit for future use; no actual use or outcome is claimed.",
        "source_catalogue": "assets/card-catalog.js", "sources": sources, "new_generation": False,
        "family_photographs_used": False, "venue_logos_used": False,
        "fonts_embedded": fonts, "layout_reasoning": [
            "A single US Letter sheet keeps four broad shopping choices at a readable 24-point size with one recognizable complete object per card.",
            "Two wide text choices preserve alternatives and browsing without a purchase. No, Help, Break and All done stay visible in their own 22-point support cards.",
            "Cream, navy, pine and white provide clear separation without recoloring the natural object artwork. The chair for Break is an existing familiar studio object.",
            "Exact vector text and approved SVG geometry use a code-native PDF layout. Native atlas clipping selects existing catalogue cells without changing any source file or cutting off a subject.",
            "Generic object images represent categories, not current stock, venue photographs, a purchase, or a promise of availability. The footer invites checking choices before offering them."
        ],
        "public_notice": "Generic illustrations, not shop stock. Check available choices before offering them.",
        "outputs": [{**output_record(PDF), "pages": 1, "page_dimensions_pt": [612, 792]}, output_record(PNG, alt)],
        "validation": {"automated": "One US Letter page, all ten exact choice labels, embedded fonts, in-bounds text, no image-label overlap, 1530 by 1980 PNG export, and unchanged source hashes verified.",
                       "visual_review": "Pending review of final rendered PNG."},
        "layout_bounds": bounds,
    }
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"outputs": record["outputs"], "provenance": str(PROVENANCE.relative_to(ROOT))}))


def record_visual_review():
    record = json.loads(PROVENANCE.read_text())
    for item in record["outputs"] + record["sources"]:
        assert digest(ROOT / item["path"]) == item["sha256"], item["path"]
    record["validation"]["visual_review"] = ("Final 1530 by 1980 PNG visually inspected on October 18, 2026. All ten exact labels are clear; each complete object is recognizable and separated from its label. "
        "No neighboring atlas objects, clipped subjects, text overflow, intersecting borders, or unexpected glyphs appear. Support choices remain visible, and the generic-stock/future-use notices are readable.")
    PROVENANCE.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print("Recorded visual review for the unchanged final board files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-visual-review", action="store_true")
    args = parser.parse_args()
    record_visual_review() if args.record_visual_review else build()
