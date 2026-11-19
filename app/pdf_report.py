"""
PDF Maintenance Report Generator using ReportLab.
Produces a formal, professional industrial maintenance analysis report
suitable for submission to plant managers and higher officials.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas

from app.dataset_loader import BASE_DIR

REPORTS_DIR = BASE_DIR / "reports"


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' in the footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_footer(num_pages)
            super().showPage()
        super().save()

    def draw_page_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer divider rule
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 36, letter[0] - 40, 36)

        # Footer text
        left_text = "Industrial Failure Prediction System | Confidential Maintenance Report"
        right_text = f"Page {self._pageNumber} of {page_count}"
        self.drawString(40, 24, left_text)
        self.drawRightString(letter[0] - 40, 24, right_text)
        self.restoreState()


def generate_maintenance_pdf(report_data: Dict[str, Any]) -> Path:
    """
    Generates a professional PDF maintenance analysis report and saves it in reports/.
    Returns the absolute Path of the created PDF file.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_id = report_data.get("report_id") or f"MWR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    filename = f"{report_id}.pdf"
    pdf_path = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2563eb"),
        textTransform="uppercase",
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )

    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        textTransform="uppercase",
    )

    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#475569"),
    )

    elements = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("INDUSTRIAL EQUIPMENT MAINTENANCE ANALYSIS REPORT", title_style),
            Paragraph(f"<b>REPORT ID:</b><br/>{report_id}", ParagraphStyle("RightMeta", parent=body_style, alignment=2, fontSize=9, textColor=colors.HexColor("#1e293b"))),
        ],
        [
            Paragraph("Explainable NLP-Based Failure Prediction & Decision Support System", subtitle_style),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle("RightDate", parent=body_style, alignment=2, fontSize=8, textColor=colors.HexColor("#64748b"))),
        ]
    ]

    header_table = Table(header_data, colWidths=[380, 152])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10, spaceBefore=4))

    # 2. Metadata Information Block (2x4 table)
    meta_data = [
        [
            Paragraph("Machine ID", meta_label),
            Paragraph("Machine Name", meta_label),
            Paragraph("Equipment Type", meta_label),
            Paragraph("Inspection Date", meta_label),
        ],
        [
            Paragraph(report_data.get("machine_id", "MCH-UNKNOWN"), meta_val),
            Paragraph(report_data.get("machine_name", "Primary Operating Unit"), meta_val),
            Paragraph(report_data.get("equipment_type", "Standard Machinery"), meta_val),
            Paragraph(report_data.get("inspection_date", datetime.now().strftime("%Y-%m-%d")), meta_val),
        ],
        [
            Paragraph("Technician / Inspector", meta_label),
            Paragraph("NLP Prediction Model", meta_label),
            Paragraph("Training Benchmark", meta_label),
            Paragraph("Analysis Status", meta_label),
        ],
        [
            Paragraph(report_data.get("technician_name", "Plant Technician"), meta_val),
            Paragraph("TF-IDF + Balanced Logistic Regression", meta_val),
            Paragraph("FMC-MWO2KG Work Orders", meta_val),
            Paragraph("Verified Automated Diagnostic", meta_val),
        ]
    ]

    meta_table = Table(meta_data, colWidths=[133, 133, 133, 133])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # 3. Section: Original Technician Observation
    elements.append(Paragraph("1. TECHNICIAN INSPECTION OBSERVATION", section_heading))
    obs_text = report_data.get("original_text", "")
    obs_box = [
        [Paragraph(f'"{obs_text}"', ParagraphStyle("ObsItalic", parent=body_style, fontName="Helvetica-Oblique", fontSize=9.5, leading=14))]
    ]
    obs_table = Table(obs_box, colWidths=[532])
    obs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(obs_table)
    elements.append(Spacer(1, 8))

    # 4. Section: Extracted Symptoms
    elements.append(Paragraph("2. EXTRACTED DIAGNOSTIC SYMPTOMS", section_heading))
    symptoms = report_data.get("detected_symptoms", [])
    if symptoms:
        sym_rows = [
            [Paragraph("Symptom Category", meta_label), Paragraph("Identified Observation Keywords", meta_label)]
        ]
        for s in symptoms:
            cat_name = s.get("symptom_category", "")
            terms = ", ".join(s.get("matched_terms", []))
            sym_rows.append([
                Paragraph(cat_name, body_bold),
                Paragraph(terms, body_style),
            ])
        sym_table = Table(sym_rows, colWidths=[200, 332])
        sym_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(sym_table)
    else:
        elements.append(Paragraph("No standard categorical symptom keywords were isolated; classification performed via global textual n-grams.", body_style))
    elements.append(Spacer(1, 8))

    # 5. Section: Diagnostic Assessment (Predicted Category & Confidence)
    elements.append(Paragraph("3. MACHINE LEARNING DIAGNOSTIC PREDICTION", section_heading))
    pred_category = report_data.get("predicted_category", "Unknown")
    confidence_pct = report_data.get("confidence_percentage", 0.0)
    is_low_conf = report_data.get("is_low_confidence", False)

    pred_box_data = [
        [
            Paragraph("PREDICTED FAILURE CATEGORY", meta_label),
            Paragraph("MODEL CONFIDENCE", meta_label),
            Paragraph("SUGGESTED PRIORITY", meta_label),
        ],
        [
            Paragraph(f"<font size=12><b>{pred_category}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#2563eb'><b>{confidence_pct:.1f}%</b></font>", body_style),
            Paragraph(f"<b>{report_data.get('maintenance_recommendations', {}).get('suggested_priority', 'Standard')}</b>", body_style),
        ]
    ]

    pred_table = Table(pred_box_data, colWidths=[260, 136, 136])
    pred_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2563eb")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(pred_table)

    if is_low_conf:
        warn_msg = report_data.get("low_confidence_warning", "Prediction exhibits close alternative categories.")
        warn_table = Table([[Paragraph(f"<b>Warning:</b> {warn_msg}", ParagraphStyle("Warn", parent=body_style, textColor=colors.HexColor("#b45309")))]], colWidths=[532])
        warn_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fde68a")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(Spacer(1, 4))
        elements.append(warn_table)

    # Alternative categories
    alts = report_data.get("alternative_categories", [])
    if alts:
        alt_str = ", ".join([f"{a['category']} ({a['percentage']}%)" for a in alts[:2]])
        elements.append(Spacer(1, 3))
        elements.append(Paragraph(f"<b>Secondary Probable Categories:</b> {alt_str}", ParagraphStyle("AltText", parent=body_style, fontSize=8.5, textColor=colors.HexColor("#475569"))))

    elements.append(Spacer(1, 8))

    # 6. Section: Explainable NLP Feature Attribution
    elements.append(Paragraph("4. EXPLAINABLE NLP FEATURE ATTRIBUTION", section_heading))
    explain_data = report_data.get("explainability", {})
    top_words = explain_data.get("top_words", [])

    if top_words:
        exp_table_data = [
            [
                Paragraph("Word / N-Gram", meta_label),
                Paragraph("TF-IDF Weight", meta_label),
                Paragraph("Model Weight (Coef)", meta_label),
                Paragraph("Contribution Score", meta_label),
                Paragraph("Direction", meta_label),
            ]
        ]
        for w in top_words[:5]:
            dir_color = "#dc2626" if w.get("is_positive") else "#2563eb"
            dir_text = "Supports" if w.get("is_positive") else "Reduces"
            exp_table_data.append([
                Paragraph(f"<b>{w['term']}</b>", body_style),
                Paragraph(f"{w['tfidf_weight']:.3f}", body_style),
                Paragraph(f"{w['coefficient']:+.3f}", body_style),
                Paragraph(f"<b>{w['contribution']:+.3f}</b>", body_style),
                Paragraph(f"<font color='{dir_color}'><b>{dir_text}</b></font>", body_style),
            ])

        exp_table = Table(exp_table_data, colWidths=[160, 85, 95, 95, 97])
        exp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(exp_table)

    narrative = explain_data.get("narrative_explanation", "")
    if narrative:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(narrative, ParagraphStyle("NarrativeText", parent=body_style, fontSize=8.5, leading=11.5, textColor=colors.HexColor("#334155"))))

    elements.append(Spacer(1, 8))

    # 7. Section: Maintenance Guidance
    elements.append(Paragraph("5. SUGGESTED MAINTENANCE INSPECTION ACTIONS", section_heading))
    recs = report_data.get("maintenance_recommendations", {})
    subsystem = recs.get("targeted_subsystem", "General Assembly")
    suggestions = recs.get("suggestions", [])

    elements.append(Paragraph(f"<b>Targeted Subsystem:</b> {subsystem}", ParagraphStyle("Subsystem", parent=body_style, fontSize=9, leading=12, textColor=colors.HexColor("#1e3a8a"))))
    elements.append(Spacer(1, 3))

    action_items = []
    for s in suggestions:
        action_items.append([
            Paragraph("&bull;", ParagraphStyle("Bullet", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#2563eb"))),
            Paragraph(s, body_style),
        ])

    actions_table = Table(action_items, colWidths=[15, 517])
    actions_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(actions_table)
    elements.append(Spacer(1, 10))

    # 8. Section: Official Disclaimer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6, spaceBefore=4))
    elements.append(Paragraph("<b>OFFICIAL ENGINEERING DISCLAIMER:</b>", ParagraphStyle("DiscHead", parent=disclaimer_style, fontName="Helvetica-Bold", fontSize=8)))
    elements.append(Paragraph(
        "This report is generated using a Machine Learning model based on the technician's written observations. "
        "The prediction is intended to support maintenance decisions and does not replace physical inspection "
        "or professional engineering judgment.",
        disclaimer_style,
    ))

    # Build PDF with two-pass canvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    return pdf_path
