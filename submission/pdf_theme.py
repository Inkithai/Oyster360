"""Shared theme and drawing primitives for the Oyster360 submission PDFs."""
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph

INK = HexColor("#16232E")
TEAL = HexColor("#0F766E")
TEAL_DARK = HexColor("#0B5D57")
CREAM = HexColor("#FAF7F1")
AMBER = HexColor("#D97706")
GREY = HexColor("#5B6B79")
LINE = HexColor("#E3DccB")

W, H = landscape(letter)  # 792 x 612


def style(name, **kw):
    base = dict(fontName="Helvetica", fontSize=13, leading=19, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


H1 = style("h1", fontName="Helvetica-Bold", fontSize=27, leading=33)
H2 = style("h2", fontName="Helvetica-Bold", fontSize=19, leading=25, textColor=TEAL_DARK)
BODY = style("body", fontSize=13.5, leading=21, textColor=INK)
BULLET = style("bullet", fontSize=13.5, leading=20.5, textColor=INK, leftIndent=14)
SMALL = style("small", fontSize=11, leading=16, textColor=GREY)
WHITE = style("white", fontSize=13.5, leading=20, textColor=white)
KPI_NUM = style("kpi", fontName="Helvetica-Bold", fontSize=30, leading=36, textColor=TEAL)
KPI_LBL = style("kpilbl", fontSize=11.5, leading=15, textColor=GREY)


def footer(c, page, total):
    c.setFont("Helvetica", 9)
    c.setFillColor(GREY)
    c.drawString(0.75 * inch, 0.42 * inch, "Oyster360 — AI-powered farm management for commercial oyster mushroom cultivation")
    c.drawRightString(W - 0.75 * inch, 0.42 * inch, f"{page} / {total}")


def content_slide(c, title, kicker=None):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.rect(0.75 * inch, H - 1.05 * inch, 0.16 * inch, 0.42 * inch, stroke=0, fill=1)
    if kicker:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(AMBER)
        c.drawString(1.02 * inch, H - 0.78 * inch, kicker.upper())
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 25)
        c.drawString(1.02 * inch, H - 1.12 * inch, title)
    else:
        c.setFont("Helvetica-Bold", 27)
        c.setFillColor(INK)
        c.drawString(1.02 * inch, H - 1.08 * inch, title)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(0.75 * inch, H - 1.32 * inch, W - 0.75 * inch, H - 1.32 * inch)


def bullets(c, x, y, items, width=6.9 * inch, gap=8, st=BULLET):
    y0 = y
    for it in items:
        p = Paragraph("<bullet>&bull;</bullet> " + it, st)
        w, h = p.wrap(width, 1000)
        p.drawOn(c, x, y0 - h)
        y0 -= h + gap
    return y0


def kpi_row(c, x, y, items, bw=2.28 * inch, gap=0.16 * inch):
    for i, (num, lbl) in enumerate(items):
        bx = x + i * (bw + gap)
        c.setFillColor(white)
        c.roundRect(bx, y - 1.35 * inch, bw, 1.35 * inch, 8, stroke=0, fill=1)
        c.setStrokeColor(LINE)
        c.roundRect(bx, y - 1.35 * inch, bw, 1.35 * inch, 8, stroke=1, fill=0)
        p = Paragraph(num, KPI_NUM)
        w, h = p.wrap(bw - 20, 200)
        p.drawOn(c, bx + 12, y - 0.32 * inch - h + 12)
        q = Paragraph(lbl, KPI_LBL)
        w2, h2 = q.wrap(bw - 24, 200)
        q.drawOn(c, bx + 12, y - 1.35 * inch + 8)
