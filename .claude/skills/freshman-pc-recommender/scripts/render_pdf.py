#!/usr/bin/env python
"""Render a Markdown recommendation report to PDF.

Usage:
    python scripts/render_pdf.py input.md output.pdf

The script prefers ReportLab and falls back with a clear error if it is not
installed. It supports Chinese text when common CJK fonts are available on the
system.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def find_cjk_font() -> str | None:
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<link href="\2"><font color="blue">\1</font></link>', escaped)
    return re.sub(r"(?<!href=\")https?://[^\s<]+", r'<link href="\g<0>"><font color="blue">商品链接</font></link>', escaped)


def markdown_to_flowables(markdown: str, styles):
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    story = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue

        if line.startswith("# "):
            story.append(Paragraph(html.escape(line[2:].strip()), styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(html.escape(line[3:].strip()), styles["Heading1"]))
        elif line.startswith("### "):
            story.append(Paragraph(html.escape(line[4:].strip()), styles["Heading2"]))
        elif line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                row = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in row):
                    table_lines.append([Paragraph(inline_markup(cell), styles["Normal"]) for cell in row])
                i += 1
            if table_lines:
                table = Table(table_lines, repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, -1), styles["Normal"].fontName),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]))
                story.append(table)
                story.append(Spacer(1, 8))
            continue
        elif line.startswith("- "):
            story.append(Paragraph("• " + inline_markup(line[2:].strip()), styles["Normal"]))
        else:
            story.append(Paragraph(inline_markup(line), styles["Normal"]))
        i += 1
    return story


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/render_pdf.py input.md output.pdf", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    markdown = input_path.read_text(encoding="utf-8")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate
    except ImportError:
        print("Missing dependency: reportlab. Install it or generate the PDF with another available PDF tool.", file=sys.stderr)
        return 1

    font_name = "Helvetica"
    font_path = find_cjk_font()
    if font_path:
        font_name = "CJKFont"
        pdfmetrics.registerFont(TTFont(font_name, font_path))

    styles = getSampleStyleSheet()
    for style_name in styles.byName:
        styles[style_name].fontName = font_name
        if style_name == "Normal":
            styles[style_name].fontSize = 9
            styles[style_name].leading = 13

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    doc.build(markdown_to_flowables(markdown, styles))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())