
from datetime import date
import json
from typing import List

from fpdf import FPDF, Align, FontFace

from schemas import schemas

COLUMN_WIDTHS = (4, 15, 10, 10, 11, 11, 11, 6, 6)


class PDF(FPDF):
    def footer(self) -> None:
        self.set_y(-70)
        # Printing page number:
        with self.table(line_height=4, col_widths=COLUMN_WIDTHS, text_align=Align.L, borders_layout="NONE") as table:
            headers = table.row(style=FontFace(emphasis="BOLD"))
            headers.cell("Note:", colspan=1)
            headers = table.row(style=FontFace(size_pt=8))
            headers.cell()
            headers.cell("Formulir yang sudah terisi lengkap disimpan pada R. Arsip QC selama 3 tahun terhitung sejak pemusnahan dilakukan Pemusnahan retained dan reference produk jadi dilakukan setelah ED produk + 1 tahun + 1 bulan",
                         colspan=4)

        with self.table(col_widths=COLUMN_WIDTHS, text_align=Align.C) as table:
            headers = table.row(style=FontFace(emphasis="BOLD"))
            headers.cell("Dilakukan oleh:\n\n(QC Inspektor)", colspan=3)
            headers.cell("Diketahui oleh:\n\n(QC Supervisor)", colspan=2)
            headers.cell("Disetujui oleh:\n\n(QC Manager)", colspan=4)
        with self.table(col_widths=COLUMN_WIDTHS, text_align=Align.C, borders_layout="NONE", headings_style=FontFace(emphasis=None)) as table:
            headers = table.row()
            headers.cell(colspan=3)
            headers.cell(colspan=2)
            headers.cell("CR-QO-QC-5024.00 (16 Agt 2018)", colspan=4)

        self.multi_cell(0, 3, "Dokumen ini telah ditandatangani secara elektronik menggunakan aplikasi\nFUPD Online dengan melampirkan lembar persetujuan elektronik milik\nPT. Bintang Toedjoe (A Kalbe Company)",
                        center=True,
                        align=Align.C,
                        padding=2)


def generate_pdf(samples: List[schemas.SampleProductJoin], date: date, page: int = 1):
    pdf = PDF(orientation="landscape", format="A4")
    pdf.add_page()

    # Set font for the document
    pdf.set_font("Helvetica", size=10)

    with pdf.table(line_height=20, col_widths=COLUMN_WIDTHS, text_align=Align.C) as table:
        headers = table.row()
        headers.cell(
            img="reports/assets/b7-biru.png",  colspan=2,  padding=3)
        headers.cell(
            "Form Pemusnahan Retained Sampel Finished Goods", colspan=7, )

    with pdf.table(col_widths=COLUMN_WIDTHS, text_align=Align.L) as table:
        headers = table.row(style=FontFace(emphasis="BOLD"))
        headers.cell(
            "Tanggal Pemusnahan", colspan=2)
        headers.cell(
            date.strftime("%B %Y"), colspan=2)
        headers.cell("Jenis Produk Jadi: ")
        headers.cell("OOT", colspan=4)

        headers = table.row(style=FontFace(emphasis="BOLD"))
        headers.cell(
            "Lokasi", colspan=2)
        headers.cell("Pulo Gadung", colspan=7)

    fill_yellow_style = FontFace(fill_color=(255, 255, 0))
    headings_style = FontFace(emphasis="BOLD", fill_color=(192, 192, 192))
    with pdf.table(col_widths=COLUMN_WIDTHS, text_align=Align.C, headings_style=headings_style) as table:
        table_heading = table.row()
        table_heading.cell("No.")
        table_heading.cell("Nama Produk")
        table_heading.cell("Kode Produk")
        table_heading.cell("No. Batch")
        table_heading.cell("Manufacturing Date")
        table_heading.cell("Expired Date")
        table_heading.cell("Destroy Date")
        table_heading.cell("Kemasan")
        table_heading.cell("Berat (Kg)")

        for idx, data_row in enumerate(samples):
            table_row = table.row()
            table_row.cell(str(idx+1))
            table_row.cell(data_row.product_name)
            table_row.cell(data_row.product_code)
            table_row.cell(data_row.batch_number)
            table_row.cell(data_row.manufacturing_date.strftime("%b-%y"))
            table_row.cell(data_row.expiration_date.strftime("%b-%y"))
            table_row.cell(data_row.destroy_date.strftime("%b-%y"))
            table_row.cell(style=fill_yellow_style)
            table_row.cell(style=fill_yellow_style)

    # Save PDF to a file
    pdf_file_path = f"destroy_report_{date.strftime('%Y-%b-%d')}_page-{page}.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path


def generate_destroy_report(samples: List[schemas.SampleProductJoin], date: date):
    num_samples = len(samples)
    # Calculate the number of PDF pages needed
    num_pages = num_samples // 12 + (1 if num_samples % 12 != 0 else 0)
    pdf_files = []

    for idx in range(num_pages):
        # Get samples for the current page
        current_samples = samples[:12]
        samples = samples[12:]

        # Generate PDF for the current page
        pdf_file_path = generate_pdf(current_samples, date, idx+1)
        pdf_files.append(pdf_file_path)

    return pdf_files
