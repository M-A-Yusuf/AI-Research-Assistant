from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

import tempfile


def generate_pdf(title, abstract, sections, references):
    """
    Create a professional IEEE-style SINGLE COLUMN PDF.
    Returns path to the generated PDF file.
    """

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = temp_file.name
    temp_file.close()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=55,
        leftMargin=55,
        topMargin=60,
        bottomMargin=60,
    )

    story = []
    styles = getSampleStyleSheet()

    # Title Style
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    # Heading Style
    heading_style = ParagraphStyle(
        name="Heading",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )

    # Normal body text
    normal_style = ParagraphStyle(
        name="NormalText",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY
    )

    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))

    # Abstract
    story.append(Paragraph("<b>Abstract</b>", heading_style))
    story.append(Paragraph(abstract, normal_style))
    story.append(Spacer(1, 12))

    # Sections
    for heading, content in sections:
        story.append(Paragraph(f"<b>{heading}</b>", heading_style))
        story.append(Paragraph(content, normal_style))
        story.append(Spacer(1, 8))

    # References
    story.append(Paragraph("<b>References</b>", heading_style))
    story.append(Paragraph(references, normal_style))

    # Build PDF
    doc.build(story)

    return pdf_path
