"""Report builder: severity ordering + HTML context + reportlab PDF."""

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from scanner.services import SEVERITY_RANK


def ordered_findings(scan) -> list:
    items = list(scan.findings.all())
    return sorted(items, key=lambda f: (-SEVERITY_RANK.get(f.severity, 0), f.name))


def build_pdf_bytes(scan) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"SecureScan Report — Scan #{scan.pk}", styles["Title"]),
        Paragraph(f"Target: {scan.target.name} ({scan.target.url})", styles["Normal"]),
        Paragraph(
            f"Type: {scan.config.scan_type} | Depth: {scan.config.spider_depth} | "
            f"Status: {scan.status} | Cost: ${scan.cost_estimate}",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
    ]
    rows = [["Severity", "Finding", "URL"]]
    for f in ordered_findings(scan):
        rows.append([f.severity, f.name, f.url[:60]])
    table = Table(rows, colWidths=[25 * mm, 70 * mm, 75 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 6 * mm))
    for f in ordered_findings(scan):
        story.append(Paragraph(f"<b>{f.severity} — {f.name}</b>", styles["Heading3"]))
        if f.description:
            story.append(Paragraph(f.description, styles["Normal"]))
        if f.solution:
            story.append(Paragraph(f"<i>Fix:</i> {f.solution}", styles["Normal"]))
    doc.build(story)
    return buf.getvalue()
