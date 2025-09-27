from flask import render_template
from weasyprint import HTML
from io import BytesIO
import time
import random
from datetime import date

def create_report_pdf(report_content: str, worker_name: str) -> BytesIO:
    """
    Renders an HTML template with the report content and converts it to a PDF.
    Returns the PDF content as a BytesIO stream.
    """
    date_str = time.strftime("%Y%m%d")
    rand = random.randint(1000, 9999)

    rendered_html = render_template(
        'report_template.html.j2',
        report_content=report_content,
        worker_name=worker_name,
        report_date=date.today(),
        report_id=f"RPT-{date_str}-{rand}"
    )

    # Create a PDF file in memory
    pdf_file = BytesIO()
    HTML(string=rendered_html).write_pdf(pdf_file)
    pdf_file.seek(0)  
    return pdf_file