"""Report builder: severity ordering + HTML context + reportlab PDF."""

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from scanner.services import SEVERITY_RANK


def ordered_findings(scan) -> list:
    items = list(scan.findings.all())
    return sorted(
        items,
        key=lambda f: (
            -SEVERITY_RANK.get(f.severity, 0), f.name
        ),
    )


def severity_summary(findings: list) -> dict:
    """Counts per severity plus an overall rating (highest severity seen)."""
    counts = {"High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    overall = "No findings"
    for sev in ("High", "Medium", "Low", "Info"):
        if counts.get(sev):
            overall = sev
            break
    return {"counts": counts, "total": len(findings), "overall": overall}


def _summary_story(scan, findings, styles) -> list:
    summary = severity_summary(findings)
    story = [
        Paragraph("Executive summary", styles["Heading2"]),
        Paragraph(
            f"{summary['total']} finding(s) on {scan.target.url}. "
            f"Overall risk rating: <b>{summary['overall']}</b>.",
            styles["Normal"],
        ),
        Spacer(1, 3 * mm),
    ]
    rows = [["Severity", "Count"]]
    for sev in ("High", "Medium", "Low", "Info"):
        rows.append([sev, str(summary["counts"][sev])])
    table = Table(rows, colWidths=[40 * mm, 30 * mm])
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
    top = findings[:3]
    if top:
        story.append(Spacer(1, 3 * mm))
        story.append(
            Paragraph(
                "Top risks: "
                + "; ".join(f"{f.severity} — {f.name}" for f in top),
                styles["Normal"],
            )
        )
    story.append(Spacer(1, 6 * mm))
    return story


def build_pdf_bytes(scan) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm
    )
    styles = getSampleStyleSheet()
    findings = ordered_findings(scan)
    story = [
        Paragraph(f"SecureScan Report — Scan #{scan.pk}", styles["Title"]),
        Paragraph(
            f"Target: {scan.target.name} ({scan.target.url})",
            styles["Normal"],
        ),
        Paragraph(
            f"Type: {scan.config.scan_type} | "
            f"Depth: {scan.config.spider_depth} | "
            f"Status: {scan.status} | Cost: ${scan.cost_estimate}",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
    ]
    story.extend(_summary_story(scan, findings, styles))
    rows = [["Severity", "Finding", "URL"]]
    for f in findings:
        rows.append([f.severity, f.name, f.url[:60]])
    table = Table(
        rows, colWidths=[25 * mm, 70 * mm, 75 * mm]
    )
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
    for f in findings:
        story.append(
            Paragraph(
                f"<b>{f.severity} — {f.name}</b>",
                styles["Heading3"],
            )
        )
        if f.description:
            story.append(Paragraph(f.description, styles["Normal"]))
        if f.solution:
            story.append(
                Paragraph(
                    f"<i>Fix:</i> {f.solution}",
                    styles["Normal"],
                )
            )
    doc.build(story)
    return buf.getvalue()
