from flask import render_template
from weasyprint import HTML
from io import BytesIO

def create_report_pdf(report_content: str, worker_name: str) -> BytesIO:
    """
    Renders an HTML template with the report content and converts it to a PDF.
    Returns the PDF content as a BytesIO stream.
    """
    # Render the HTML template with the AI-generated content
    rendered_html = render_template(
        'report_template.html.j2', 
        report_content=report_content,
        worker_name=worker_name
    )
    
    # Create a PDF file in memory
    pdf_file = BytesIO()
    HTML(string=rendered_html).write_pdf(pdf_file)
    pdf_file.seek(0) # Move the cursor to the beginning of the stream
    
    return pdf_file