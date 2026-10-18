#!/usr/bin/env python3
"""Build the original, text-only Safe Haven story brief for editors and curators."""

from pathlib import Path
import hashlib
import json

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

from build_thrift_shop_choice_board import register_fonts


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "downloads/safe-haven-press-brief.pdf"
RECORD = ROOT / "docs/safe-haven-press-brief-provenance.json"
STORY = "https://anausomelife.com/safe-haven-thrift-shop-wells-maine.html"
BOARD = "https://anausomelife.com/thrift-shop-choice-board.html"
SHARE = STORY + "#share-this-story"
INK = HexColor("#173c4c")
PINE = HexColor("#2e513f")
CREAM = HexColor("#f7f4ec")
MUTED = HexColor("#4b5b61")


def build():
    fonts = register_fonts()
    body = ParagraphStyle("body", fontName="ThriftSans", fontSize=11, leading=15.2,
                          textColor=INK, spaceAfter=9)
    styles = {
        "body": body,
        "brand": ParagraphStyle("brand", parent=body, fontName="ThriftSansBold", fontSize=10,
                                leading=13, textColor=PINE, spaceAfter=0),
        "meta": ParagraphStyle("meta", parent=body, fontSize=9, leading=12,
                               textColor=MUTED, spaceAfter=0),
        "title": ParagraphStyle("title", parent=body, fontName="ThriftSerif", fontSize=27,
                                leading=29, spaceAfter=13),
        "heading": ParagraphStyle("heading", parent=body, fontName="ThriftSansBold", fontSize=12,
                                  leading=16, spaceBefore=6, spaceAfter=6),
        "small": ParagraphStyle("small", parent=body, fontSize=9.3, leading=12.8, spaceAfter=7),
        "source": ParagraphStyle("source", parent=body, fontSize=8.7, leading=12, textColor=MUTED),
    }

    def p(text, style="body"):
        return Paragraph(text, styles[style])

    def link(url, label):
        return f'<a href="{url}" color="#2e513f"><u>{label}</u></a>'

    story = [
        p("AN AUSOME LIFE  /  WELLS, MAINE", "brand"),
        Spacer(1, 5),
        p("STORY BRIEF  /  18 OCTOBER 2026", "meta"),
        Spacer(1, 16),
        p("A $1 L.L.Bean find.<br/>A school-dance shirt.<br/>A thrift stop for the cats.", "title"),
        p("Our favorite find at Safe Haven in Wells was <b>L.L.Bean for $1</b>. A lovely, inveterate thrifter also recommended a <b>vintage Tommy Jeans velour shirt for James's upcoming school dance</b>. Retro cool was the idea."),
        p("The same shopper called Safe Haven the absolute best store he visits and pointed us to the <b>$1 clearance walls along the side and back</b>. Our published family field note includes original photographs and practical visit notes. Individual prices and stock change."),
        HRFlowable(width="100%", thickness=0.7, color=HexColor("#a7b2aa"), spaceBefore=3, spaceAfter=9),
        p("The place", "heading"),
        p("<b>Safe Haven Humane Society Vintage/Thrift/Antique Shop at Cattail Farm</b><br/>1784 Post Road, Wells, Maine 04090. Safe Haven says shop proceeds support its all-volunteer cat rescue, rehabilitation, adoption and care work in York County. Check current hours and entrance arrangements with the shop.", "small"),
        p("A free board for a future browse", "heading"),
        p("We made the shopping choice board <b>after this visit</b>. It offers Books, Clothes, Lamps and Baskets, plus Something else, Just looking, No, Help, Break and All done. Use the screen or one-page printable PDF, alongside the person's usual communication. Its generic illustrations make it useful for other thrift shops, too.", "small"),
        Spacer(1, 4),
    ]
    links = Table([
        [p("READ &amp; SHARE", "brand")],
        [p(link(STORY, "Read the family story") + "  |  " + link(BOARD, "Open the free board"), "body")],
        [p(link(SHARE, "Get the two social graphics, captions and permissions"), "body")],
        [p("Contact: " + link("mailto:hello@anausomelife.com", "hello@anausomelife.com"), "small")],
    ], colWidths=[524])
    links.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#edf0e8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 13),
        ("TOPPADDING", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
        ("TOPPADDING", (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 1),
    ]))
    story += [links, Spacer(1, 12),
        p("<b>Image sharing.</b> The two linked Safe Haven feed and Story PNGs may be reposted unchanged in organic social posts or Stories, with An AUsome Life / @anausomelife credit and a link to the free board. For family photographs, image edits, paid advertising or other image publication, contact us about the specific files and use.", "small"),
        p("Sources: the family's visit account; " + link("https://www.safehavenhumanesociety.org/shop/", "Safe Haven's shop page") + "; " + link("https://www.safehavenhumanesociety.org/about-safe-haven/", "Safe Haven's mission") + ". Shop facts checked 18 October 2026.", "source"),
    ]

    def page(c, doc):
        c.saveState()
        c.setFillColor(CREAM)
        c.rect(0, 0, 612, 792, fill=1, stroke=0)
        c.setFillColor(PINE)
        c.rect(0, 780, 612, 12, fill=1, stroke=0)
        c.setFont("ThriftSans", 8.5)
        c.setFillColor(MUTED)
        c.drawString(44, 24, "Independent family field notes and practical resources")
        c.drawRightString(568, 24, "anausomelife.com")
        c.linkURL("https://anausomelife.com", (488, 21, 568, 34), relative=0, thickness=0)
        c.restoreState()

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=(612, 792), rightMargin=44, leftMargin=44,
                            topMargin=35, bottomMargin=42, title="Safe Haven in Wells - story brief",
                            author="An AUsome Life", subject="A family thrift story and a free shopping choice board",
                            creator="An AUsome Life", pageCompression=1)
    doc.build(story, onFirstPage=page, onLaterPages=page)
    pdf = PdfReader(OUTPUT)
    assert len(pdf.pages) == 1, f"Expected one page, got {len(pdf.pages)}"
    extracted = pdf.pages[0].extract_text()
    for phrase in ["L.L.Bean", "$1", "Tommy Jeans velour shirt", "after this visit", "hello@anausomelife.com"]:
        assert phrase in extracted, phrase
    assert len(pdf.pages[0].get("/Annots", [])) >= 7
    record = {
        "title": "Safe Haven in Wells: story brief",
        "created": "2026-10-18",
        "author": "An AUsome Life",
        "basis": "Original publication-written typography and text; no photographs, external graphics or source artwork embedded.",
        "owner_facts": [
            "L.L.Bean for $1 was the family's favorite find; item type unspecified.",
            "The same inveterate thrifter recommended a vintage Tommy Jeans velour shirt for James's upcoming school dance.",
            "That shopper described Safe Haven as his best store and pointed out the $1 clearance walls at the side and back.",
        ],
        "sources": ["https://www.safehavenhumanesociety.org/shop/", "https://www.safehavenhumanesociety.org/about-safe-haven/"],
        "fonts": fonts,
        "output": {"path": str(OUTPUT.relative_to(ROOT)), "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                   "bytes": OUTPUT.stat().st_size, "pages": 1, "page_dimensions_pt": [612, 792]},
        "review": {"text_extraction": "passed", "hyperlinks": len(pdf.pages[0].get("/Annots", [])),
                   "visual": "pending"},
        "sharing_scope": "The existing two social PNGs retain their exact-file organic-social permission. This PDF does not extend family-photo or other image rights.",
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record["output"]))


if __name__ == "__main__":
    build()
