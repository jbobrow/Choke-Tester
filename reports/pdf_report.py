"""
PDF report generation for choke-test results.

Produces a professional safety report with:
  - Header / title block with date and standard info
  - Summary statistics
  - Per-object results table with colour-coded pass/fail
  - Footer with disclaimer
"""

import datetime
from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from analyzer.choke_check import ChokeResult
from analyzer.standards import ChokeStandard


def generate_report(
    results: List[ChokeResult],
    output_path: str,
    standard: ChokeStandard,
) -> str:
    """
    Generate a PDF safety report.

    Parameters
    ----------
    results : list of ChokeResult
    output_path : str
        Where to write the PDF.
    standard : ChokeStandard
        The standard used for the analysis.

    Returns
    -------
    str  — the absolute path of the written PDF.
    """
    path = Path(output_path)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6 * mm,
        textColor=colors.HexColor("#212121"),
    )
    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
        textColor=colors.HexColor("#37474F"),
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=2 * mm,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#757575"),
    )

    story = []

    # ── Title ────────────────────────────────────────────────────────────
    story.append(Paragraph("Choke Test Safety Report", title_style))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(f"Generated: {now}", small_style))
    story.append(Spacer(1, 4 * mm))

    # ── Standard info ────────────────────────────────────────────────────
    story.append(Paragraph("Standard Used", heading_style))
    story.append(Paragraph(f"<b>{standard.name}</b>", body_style))
    story.append(
        Paragraph(
            f"Cylinder: \u00d8{standard.diameter_mm} mm \u00d7 "
            f"{standard.height_mm} mm height",
            body_style,
        )
    )
    story.append(Paragraph(standard.description, body_style))
    story.append(Spacer(1, 4 * mm))

    # ── Summary ──────────────────────────────────────────────────────────
    story.append(Paragraph("Summary", heading_style))
    total = len(results)
    fails = sum(1 for r in results if r.fits)
    passes = total - fails
    story.append(
        Paragraph(
            f"<b>{total}</b> objects analysed &mdash; "
            f"<font color='#B71C1C'><b>{fails}</b> choking hazard(s)</font>, "
            f"<font color='#1B5E20'><b>{passes}</b> safe</font>",
            body_style,
        )
    )
    story.append(Spacer(1, 4 * mm))

    # ── Results table ────────────────────────────────────────────────────
    story.append(Paragraph("Detailed Results", heading_style))

    header = ["Object", "Status", "Diameter (mm)", "Height (mm)"]
    data = [header]

    for r in results:
        status = "\u26a0 CHOKING HAZARD" if r.fits else "\u2714 SAFE"
        d_text = f"{r.diameter_mm:.1f}" if r.diameter_mm else "\u2014"
        h_text = f"{r.height_mm:.1f}" if r.height_mm else "\u2014"
        data.append([r.name, status, d_text, h_text])

    col_widths = [70 * mm, 40 * mm, 30 * mm, 30 * mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Colour rows by result
    table_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#37474F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDBDBD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    for i, r in enumerate(results, start=1):
        bg = colors.HexColor("#FFEBEE") if r.fits else colors.HexColor("#E8F5E9")
        fg = colors.HexColor("#B71C1C") if r.fits else colors.HexColor("#1B5E20")
        table_style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
        table_style_cmds.append(("TEXTCOLOR", (1, i), (1, i), fg))

    table.setStyle(TableStyle(table_style_cmds))
    story.append(table)
    story.append(Spacer(1, 8 * mm))

    # ── Disclaimer ───────────────────────────────────────────────────────
    disclaimer = (
        "<b>Disclaimer:</b> This report is generated by an automated tool "
        "and is provided for informational purposes only. It does not "
        "constitute formal safety certification. Always consult the "
        "relevant safety standard and, where required, submit parts for "
        "official testing by an accredited laboratory."
    )
    story.append(Paragraph(disclaimer, small_style))

    doc.build(story)
    return str(path.resolve())
