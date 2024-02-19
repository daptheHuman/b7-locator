
from datetime import date
from typing import List

from fpdf import FPDF

from schemas import schemas


def generate_destruct_report(samples: List[schemas.SampleRetained], date: date):
    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font for the document
    pdf.set_font("Times", size=12)

    # Add title
    pdf.cell(200, 10, txt="Destruct Report", ln=True, align="C")

    # Add date
    pdf.cell(
        200, 10, txt=f"Date: {date.strftime('%d-%b-%Y')}", ln=True, align="C")

    # Add sample table
    with pdf.table() as table:
        row = table.row()
        row.cell("Batch Num.")
        row.cell("Product Code")
        row.cell("Man. Date")
        row.cell("Exp. Date")
        row.cell("Des. Date")
        for data_row in samples:
            row = table.row()
            row.cell(data_row.batch_number)
            row.cell(data_row.product_code)
            row.cell(data_row.manufacturing_date.strftime("%d/%b/%Y"))
            row.cell(data_row.expiration_date.strftime("%d/%b/%Y"))
            row.cell(data_row.destruct_date.strftime("%d/%b/%Y"))

    # Save PDF to a file
    pdf_file_path = f"destruct_report_{date.strftime('%Y-%b-%d')}.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path
