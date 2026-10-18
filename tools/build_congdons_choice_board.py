#!/usr/bin/env python3
"""Build the two-page, US Letter Congdon's communication board and PNG exports.

Artwork is generic and independent; menu names do not assert current availability.
Run from any directory. Requires reportlab, Pillow, and Poppler's pdftoppm.
"""

from pathlib import Path
from functools import lru_cache
from io import BytesIO
import os
import shutil
import subprocess
import tempfile

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/congdons-choice-art"
OUTPUT = ROOT / "downloads"
PDF = OUTPUT / "congdons-choice-board.pdf"
INK = HexColor("#173c4c")
PINE = HexColor("#2e513f")
CREAM = HexColor("#f7f4ec")
MUTED = HexColor("#4b5b61")
LINE = HexColor("#a2b2a8")
WHITE = HexColor("#ffffff")
RED = HexColor("#8f3548")
W, H = 612, 792
MARGIN = 34
CONTENT = W - 2 * MARGIN
FONT_NAMES = {"Helvetica": "BoardSans", "Helvetica-Bold": "BoardSansBold", "Times-Roman": "BoardSerif"}


def register_fonts():
    runtime = Path(os.environ.get("CODEX_PRIMARY_RUNTIME_ROOT", "/opt/codex/runtimes/codex-primary-runtime"))
    font_specs = {
        "BoardSans": ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
        "BoardSansBold": ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
        "BoardSerif": ("LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
    }
    for alias, (preferred, fallback) in font_specs.items():
        candidates = [
            Path("/usr/share/fonts/truetype/liberation2") / preferred,
            Path("/usr/share/fonts/truetype/liberation") / preferred,
            runtime / "dependencies/native/libreoffice-headless/libreoffice/share/fonts/truetype" / preferred,
            Path("/usr/share/fonts/truetype/dejavu") / fallback,
        ]
        path = next((path for path in candidates if path.exists()), None)
        if not path:
            raise RuntimeError(f"An embeddable font is required for {alias}")
        pdfmetrics.registerFont(TTFont(alias, str(path)))


def line(c, text, x, y, size=11, font="Helvetica", color=INK):
    c.setFillColor(color)
    c.setFont(FONT_NAMES.get(font, font), size)
    c.drawString(x, y, text)


def center(c, text, x, y, size=22, font="Helvetica-Bold", color=INK):
    c.setFillColor(color)
    c.setFont(FONT_NAMES.get(font, font), size)
    c.drawCentredString(x, y, text)


@lru_cache(maxsize=12)
def printable_image(path):
    # Retain the full composition; use a compact, high-resolution print encoding.
    im = Image.open(path).convert("RGB")
    im.thumbnail((900, 900), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    im.save(buffer, format="JPEG", quality=89, optimize=True)
    buffer.seek(0)
    return ImageReader(buffer)


def image(c, path, x, y, size):
    c.drawImage(printable_image(path), x, y, width=size, height=size,
                preserveAspectRatio=True, anchor="c", mask="auto")


def poly(c, points, fill=False, close=False):
    p = c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    if close:
        p.close()
    c.drawPath(p, stroke=1, fill=int(fill))


def symbol(c, name, x, y, size):
    """Reproduce the site's original simple core-word SVG geometry as vectors."""
    c.saveState()
    c.translate(x, y + size)
    c.scale(size / 500, -size / 500)
    c.setFillColor(WHITE)
    c.rect(0, 0, 500, 500, stroke=0, fill=1)
    c.setLineWidth(23)
    c.setLineCap(1)
    c.setLineJoin(1)
    c.setStrokeColor(INK)
    if name == "yes":
        c.setStrokeColor(PINE)
        poly(c, [(120, 250), (210, 340), (395, 150)])
    elif name == "no":
        c.setStrokeColor(RED)
        poly(c, [(150, 150), (350, 350)])
        poly(c, [(350, 150), (150, 350)])
    elif name == "more":
        poly(c, [(250, 110), (250, 390)])
        poly(c, [(110, 250), (390, 250)])
    elif name == "help":
        c.circle(250, 250, 150, stroke=1, fill=0)
        poly(c, [(250, 150), (250, 350)])
        poly(c, [(150, 250), (350, 250)])
    elif name == "all-done":
        c.roundRect(95, 95, 310, 310, 12, stroke=1, fill=0)
        poly(c, [(150, 250), (215, 315), (350, 175)])
    elif name == "go-home":
        c.setLineWidth(19)
        poly(c, [(85, 230), (250, 95), (415, 230)])
        c.setFillColor(CREAM)
        poly(c, [(120, 220), (120, 410), (380, 410), (380, 220)], fill=True)
        c.setFillColor(PINE)
        poly(c, [(218, 410), (218, 290), (282, 290), (282, 410)], fill=True)
        c.setLineWidth(12)
        c.setFillColor(WHITE)
        c.rect(161, 256, 37, 43, stroke=1, fill=1)
        c.rect(302, 256, 37, 43, stroke=1, fill=1)
    else:
        raise ValueError(name)
    c.restoreState()


def frame(c, x, y, width, height):
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(1.3)
    c.roundRect(x, y, width, height, 6, stroke=1, fill=1)


def header(c, title, subtitle, page):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    line(c, "AN AUSOME LIFE", MARGIN, 757, 9, "Helvetica-Bold", PINE)
    c.setFont(FONT_NAMES["Helvetica"], 9)
    c.drawRightString(W - MARGIN, 757, f"{page} / 2")
    line(c, title, MARGIN, 718, 30, "Times-Roman")
    line(c, subtitle, MARGIN, 697, 11)


def footer(c, page):
    c.setStrokeColor(LINE)
    c.setLineWidth(.6)
    c.line(MARGIN, 57, W - MARGIN, 57)
    if page == 1:
        line(c, "Menu names: congdons.com/flavors/ | Checked October 18, 2026", MARGIN, 43, 8, color=MUTED)
        line(c, "Generic illustrations, not product photos. Appearance and availability vary.", MARGIN, 30, 8, color=MUTED)
        c.linkURL("https://congdons.com/flavors/", (MARGIN, 39, W-MARGIN, 53), relative=0)
    else:
        line(c, "Use this alongside the person's usual communication system.", MARGIN, 43, 8, color=MUTED)
        line(c, "anausomelife.com/congdons-choice-board.html", MARGIN, 30, 8, color=MUTED)
        c.linkURL("https://anausomelife.com/congdons-choice-board.html", (MARGIN, 26, W-MARGIN, 37), relative=0)


def create_pdf():
    register_fonts()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
    c.setTitle("Congdon's choice board - food and communication words")
    c.setAuthor("An AUsome Life")
    c.setSubject("Two printable communication boards for a Congdon's visit in Wells, Maine")
    c.setCreator("An AUsome Life")

    header(c, "Congdon's choice board", "Point to a picture or word. Any answer is welcome.", 1)
    line(c, "Generic food illustrations; check today's case before offering a choice.", MARGIN, 678, 9, color=MUTED)
    foods = [("Plain", "plain"), ("Honey dip", "honey-dip"),
             ("Chocolate raised", "chocolate-raised"), ("Apple fritter", "apple-fritter")]
    card_width = (CONTENT - 12) / 2
    card_height = 214
    for i, (label, filename) in enumerate(foods):
        x = MARGIN + (i % 2) * (card_width + 12)
        y = 662 - card_height - (i // 2) * (card_height + 12)
        frame(c, x, y, card_width, card_height)
        image(c, ASSETS / f"{filename}.webp", x + (card_width - 172) / 2, y + 37, 172)
        center(c, label, x + card_width / 2, y + 14, 22 if len(label) < 14 else 21)

    frame(c, MARGIN, 170, CONTENT, 42)
    center(c, "SOMETHING ELSE", W / 2, 182, 20)
    support_width = (CONTENT - 20) / 3
    for i, (key, label) in enumerate([("no", "NO"), ("help", "HELP"), ("all-done", "ALL DONE")]):
        x = MARGIN + i * (support_width + 10)
        frame(c, x, 82, support_width, 78)
        symbol(c, key, x + 9, 94, 52)
        center(c, label, x + 61 + (support_width - 70) / 2, 111, 18 if key == "all-done" else 20)
    line(c, "More communication words on page 2.", MARGIN, 67, 8, color=MUTED)
    footer(c, 1)
    c.showPage()

    header(c, "I have something to say.", "Point to a word or picture. Listen, pause, and honor the choice.", 2)
    line(c, "For your Congdon's stop - and whatever comes next.", MARGIN, 678, 9, color=MUTED)
    words = [
        ("yes", "YES", None), ("no", "NO", None), ("more", "MORE", None),
        ("help", "HELP", None), ("break", "BREAK", ROOT / "assets/card-studio/break.webp"),
        ("drink", "DRINK", ROOT / "assets/card-studio/water.webp"),
        ("bathroom", "BATHROOM", ROOT / "assets/card-studio/toilet.webp"),
        ("all-done", "ALL DONE", None), ("go-home", "GO HOME", None),
    ]
    word_width = (CONTENT - 24) / 3
    word_height = 181
    for i, (key, label, asset) in enumerate(words):
        x = MARGIN + (i % 3) * (word_width + 12)
        y = 662 - word_height - (i // 3) * (word_height + 12)
        frame(c, x, y, word_width, word_height)
        left = x + (word_width - 125) / 2
        if asset:
            image(c, asset, left, y + 45, 125)
        else:
            symbol(c, key, left, y + 45, 125)
        center(c, label, x + word_width / 2, y + 18, 20 if key == "bathroom" else 22)
    footer(c, 2)
    c.save()


def export_pngs():
    command = shutil.which("pdftoppm")
    if not command:
        raise RuntimeError("pdftoppm is required to export the printable PNG pages")
    with tempfile.TemporaryDirectory(prefix="congdons-board-") as directory:
        prefix = Path(directory) / "board"
        subprocess.run([command, "-r", "180", "-png", str(PDF), str(prefix)], check=True)
        shutil.copyfile(Path(directory) / "board-1.png", OUTPUT / "congdons-choice-board.png")
        shutil.copyfile(Path(directory) / "board-2.png", ASSETS / "congdons-support-board.png")


if __name__ == "__main__":
    create_pdf()
    export_pngs()
    for path in [PDF, OUTPUT / "congdons-choice-board.png", ASSETS / "congdons-support-board.png"]:
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size:,} bytes")
