from __future__ import annotations

from datetime import date, datetime
from textwrap import wrap


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT_MARGIN = 48
TOP_MARGIN = 760
BOTTOM_MARGIN = 52
LINE_HEIGHT = 16
MAX_TEXT_WIDTH = 92


def build_weekly_report_pdf(report: dict, *, patient_label: str, end_date: date) -> bytes:
    lines = _build_report_lines(report, patient_label=patient_label, end_date=end_date)
    pages = _paginate_lines(lines)
    return _render_pdf_document(pages)


def _build_report_lines(report: dict, *, patient_label: str, end_date: date) -> list[tuple[str, str]]:
    ai_report = report.get("ai_health_report") or {}
    lifestyle = report.get("lifestyle_summary") or {}
    dataset = report.get("dataset_assessment") or {}
    lines: list[tuple[str, str]] = [
        ("title", "MedoAir 7-Day AI Health Report"),
        ("meta", f"Patient: {patient_label}"),
        ("meta", f"Report end date: {end_date.isoformat()}"),
        ("meta", f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        ("blank", ""),
        ("heading", "Overview"),
        ("body", f"Days logged: {report.get('days_logged', '--')} of 7"),
        ("body", f"Week ready: {'Yes' if report.get('is_week_ready') else 'No'}"),
        ("body", f"Sleep average: {lifestyle.get('sleep_avg_hours', '--')} hours"),
        ("body", f"Symptom days: {lifestyle.get('symptom_days', '--')}"),
        ("body", f"Junk food count: {lifestyle.get('junk_food_count', '--')}"),
        ("body", f"Outside food count: {lifestyle.get('outside_food_count', '--')}"),
        ("blank", ""),
        ("heading", "Dataset Assessment"),
        ("body", f"Possible issue: {dataset.get('possible_issue') or 'Not enough data yet'}"),
        ("body", f"Risk probability: {dataset.get('risk_probability', '--')}%"),
        ("body", f"Status: {dataset.get('status', '--')}"),
        ("body", dataset.get("message") or "No dataset assessment message available."),
        ("blank", ""),
        ("heading", "AI Health Summary"),
        ("body", f"Current status: {ai_report.get('current_status') or 'No summary available yet.'}"),
        ("body", f"Attention level: {ai_report.get('attention_level') or '--'}"),
        ("body", ai_report.get("summary") or "Complete 7 days of data for a richer summary."),
        ("blank", ""),
    ]

    _append_list_section(lines, "What Is Going Well", ai_report.get("what_is_good") or [])
    _append_list_section(lines, "What Needs Attention", ai_report.get("what_needs_attention") or [])
    _append_list_section(lines, "Important Observations", ai_report.get("important_observations") or [])
    _append_list_section(lines, "What May Happen Next", ai_report.get("what_may_happen_next") or [])
    _append_list_section(lines, "Issues Detected", report.get("issues_detected") or [])
    _append_list_section(lines, "Recommended Actions", report.get("recommended_actions") or [])
    _append_list_section(lines, "Matched Weekly Symptoms", dataset.get("matched_symptoms") or [])
    _append_list_section(lines, "Care Guidance", dataset.get("care_guidance") or [])
    _append_list_section(lines, "Warning Signs", dataset.get("warning_signs") or [])
    _append_list_section(lines, "Medicine Guidance", dataset.get("medicine_guidance") or [])

    lines.append(("heading", "Medicine Compliance"))
    compliance = report.get("medicine_compliance") or []
    if compliance:
        for item in compliance:
            lines.append(
                (
                    "body",
                    f"{item.get('medicine', 'Medicine')}: taken {item.get('taken_doses', 0)}, "
                    f"missed {item.get('missed_doses', 0)}, compliance {item.get('compliance_percent', 0)}%",
                )
            )
    else:
        lines.append(("body", "No medicine compliance records yet."))
    lines.append(("blank", ""))

    lines.append(("heading", "Weekly Trends"))
    trends = report.get("weekly_trends") or []
    if trends:
        for item in trends:
            lines.append(
                (
                    "body",
                    f"{item.get('label', 'Trend')}: health score {item.get('health_score', '--')}, "
                    f"symptom days {item.get('symptom_days', '--')}, junk food {item.get('junk_food_count', '--')}",
                )
            )
    else:
        lines.append(("body", "No weekly trend data available."))
    lines.append(("blank", ""))

    lines.append(("heading", "Report Metric Trends"))
    metric_trends = report.get("report_metric_trends") or []
    if metric_trends:
        for item in metric_trends:
            values = ", ".join(
                f"{point.get('report_date')}: {point.get('value')}{(' ' + point.get('unit')) if point.get('unit') else ''}"
                for point in item.get("values") or []
            )
            lines.append(("body", f"{item.get('parameter', 'Parameter')} ({item.get('trend', 'stable')}): {values or 'No values'}"))
    else:
        lines.append(("body", "No report metric trends available."))
    lines.append(("blank", ""))

    lines.append(("heading", "Uploaded Report Summary"))
    report_summary = report.get("report_summary") or []
    if report_summary:
        for item in report_summary:
            metrics = ", ".join(
                f"{metric.get('parameter')}: {metric.get('value')}{(' ' + metric.get('unit')) if metric.get('unit') else ''} ({metric.get('status')})"
                for metric in item.get("metrics") or []
            )
            lines.append(("body", f"{item.get('title', 'Report')} - {item.get('uploaded_at', '--')}"))
            lines.append(("body", metrics or "No structured metrics found."))
    else:
        lines.append(("body", "No uploaded reports yet."))
    return lines


def _append_list_section(lines: list[tuple[str, str]], heading: str, items: list[str]) -> None:
    lines.append(("heading", heading))
    if items:
        for item in items:
            lines.append(("bullet", item))
    else:
        lines.append(("body", "No data available."))
    lines.append(("blank", ""))


def _paginate_lines(lines: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    pages: list[list[tuple[str, str]]] = [[]]
    available_height = TOP_MARGIN - BOTTOM_MARGIN
    max_lines_per_page = max(1, available_height // LINE_HEIGHT)

    current_page = pages[0]
    current_count = 0
    for style, text in lines:
        wrapped_lines = _wrap_text(style, text)
        needed = len(wrapped_lines)
        if current_count + needed > max_lines_per_page and current_page:
            current_page = []
            pages.append(current_page)
            current_count = 0
        current_page.extend(wrapped_lines)
        current_count += needed
    return pages


def _wrap_text(style: str, text: str) -> list[tuple[str, str]]:
    if style == "blank":
        return [("blank", "")]

    prefix = ""
    width = MAX_TEXT_WIDTH
    if style == "bullet":
        prefix = "- "
        width = MAX_TEXT_WIDTH - len(prefix)

    wrapped = wrap(text or "", width=width, break_long_words=False, break_on_hyphens=False) or [""]
    lines = []
    for index, chunk in enumerate(wrapped):
        if style == "bullet":
            lines.append(("body", f"{prefix if index == 0 else '  '}{chunk}"))
        else:
            lines.append((style, chunk))
    return lines


def _render_pdf_document(pages: list[list[tuple[str, str]]]) -> bytes:
    objects: list[bytes] = []
    font_object_number = 3

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids_refs = " ".join(f"{4 + index * 2} 0 R" for index in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids_refs}] /Count {len(pages)} >>".encode("latin-1"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for index, page_lines in enumerate(pages):
        page_object_number = 4 + index * 2
        content_object_number = page_object_number + 1
        content_stream = _build_content_stream(page_lines, index + 1, len(pages))
        page_object = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_object_number} 0 R >> >> /Contents {content_object_number} 0 R >>"
        ).encode("latin-1")
        stream_object = (
            f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1")
            + content_stream
            + b"\nendstream"
        )
        objects.append(page_object)
        objects.append(stream_object)

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("latin-1")
    pdf.extend(trailer)
    return bytes(pdf)


def _build_content_stream(page_lines: list[tuple[str, str]], page_number: int, total_pages: int) -> bytes:
    y = TOP_MARGIN
    commands = ["BT", "/F1 12 Tf"]
    for style, text in page_lines:
        if style == "title":
            commands.append("/F1 18 Tf")
        elif style == "heading":
            commands.append("/F1 14 Tf")
        elif style == "meta":
            commands.append("/F1 11 Tf")
        else:
            commands.append("/F1 12 Tf")
        commands.append(f"1 0 0 1 {LEFT_MARGIN} {y} Tm")
        commands.append(f"({_escape_pdf_text(text)}) Tj")
        y -= LINE_HEIGHT

    commands.append("/F1 10 Tf")
    commands.append(f"1 0 0 1 {LEFT_MARGIN} 28 Tm")
    commands.append(f"(Page {page_number} of {total_pages}) Tj")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1", errors="replace")


def _escape_pdf_text(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )
