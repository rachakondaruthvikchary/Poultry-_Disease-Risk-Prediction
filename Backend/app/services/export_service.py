from io import StringIO, BytesIO
import csv
from datetime import datetime

from fpdf import FPDF


def to_csv(rows: list[dict]) -> str:
    """Generate clean CSV export with proper headers"""
    if not rows:
        return ""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def to_pdf(title: str, rows: list[dict]) -> bytes:
    """Generate professional PDF report with table formatting"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Generated timestamp
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(108, 117, 125)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    if not rows:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 10, "No data available", new_x="LMARGIN", new_y="NEXT", align="C")
    else:
        # Table header with background
        pdf.set_fill_color(52, 58, 64)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        
        headers = list(rows[0].keys())
        col_width = 190 / len(headers) if len(headers) > 0 else 40
        
        for header in headers:
            pdf.cell(col_width, 8, header.replace('_', ' ').title(), border=1, fill=True)
        pdf.ln()
        
        # Table rows with alternating colors
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(33, 37, 41)
        
        for idx, row in enumerate(rows):
            # Alternating row colors
            if idx % 2 == 0:
                pdf.set_fill_color(248, 249, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            for value in row.values():
                # Truncate long text
                text = str(value)
                if len(text) > 30:
                    text = text[:27] + "..."
                pdf.cell(col_width, 7, text, border=1, fill=True)
            pdf.ln()
        
        # Footer summary
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 6, f"Total Records: {len(rows)}", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())
