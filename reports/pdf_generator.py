from datetime import date
from typing import List, Literal

from fpdf import FPDF, Align, FontFace

from schemas import schemas

COLUMN_WIDTHS = (3, 20, 8, 11, 11, 9, 9, 7, 7)
APPROVED_STAMP = "reports/assets/approved.png"
B7_LOGO = "reports/assets/b7-biru.png"


class PDF(FPDF):
    def __init__(
        self,
        orientation: Literal[
            "", "portrait", "p", "P", "landscape", "l", "L"
        ] = "portrait",
        unit: float | Literal["pt", "mm", "cm", "in"] = "mm",
        format: tuple[float, float]
        | Literal[
            "", "a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"
        ] = "A4",
        font_cache_dir: Literal["DEPRECATED"] = "DEPRECATED",
    ) -> None:
        super().__init__(orientation, unit, format, font_cache_dir)
        self.finished = False

    def footer(self) -> None:
        self.set_y(-55)
        # Printing page number:
        if self.finished:
            self.b_margin = 60
            with self.table(
                line_height=4,
                col_widths=COLUMN_WIDTHS,
                text_align=Align.L,
                borders_layout="NONE",
            ) as table:
                headers = table.row(style=FontFace(emphasis="BOLD"))
                headers.cell("Note:", colspan=1)
                headers = table.row(style=FontFace(size_pt=8))
                headers.cell()
                headers.cell(
                    "Formulir yang sudah terisi lengkap disimpan pada R. Arsip QC selama 3 tahun terhitung sejak pemusnahan dilakukan Pemusnahan retained dan reference produk jadi dilakukan setelah ED produk + 1 tahun + 1 bulan",
                    colspan=4,
                )

            with self.table(col_widths=COLUMN_WIDTHS, text_align=Align.C) as table:
                headers = table.row(style=FontFace(emphasis="BOLD"))
                headers.cell("Dilakukan oleh:\n\n(QC Inspektor)", colspan=3)
                headers.cell("Diketahui oleh:\n\n(QC Supervisor)", colspan=2)
                headers.cell("Disetujui oleh:\n\n(QC Manager)", colspan=4)
            with self.table(
                col_widths=COLUMN_WIDTHS,
                text_align=Align.C,
                borders_layout="NONE",
                headings_style=FontFace(emphasis=None),
            ) as table:
                headers = table.row()
                headers.cell(colspan=3)
                headers.cell(colspan=2)
                headers.cell("CR-QO-QC-5024.00 (16 Agt 2018)", colspan=4)

            self.image(APPROVED_STAMP, x=135, y=180, w=25)
            self.multi_cell(
                0,
                3,
                "Dokumen ini telah ditandatangani secara elektronik menggunakan aplikasi\nFUPD Online dengan melampirkan lembar persetujuan elektronik milik\nPT. Bintang Toedjoe (A Kalbe Company)",
                center=True,
                align=Align.C,
                padding=2,
            )


def generate_destroy_report(
    samples: List[schemas.SampleProductJoin], date: date, page: int = 1
):
    pdf = PDF(orientation="landscape", format="A4")
    pdf.add_page()

    pdf.set_auto_page_break(True, 60)
    pdf.set_font("Helvetica", size=10)

    with pdf.table(
        line_height=20, col_widths=COLUMN_WIDTHS, text_align=Align.C
    ) as table:
        headers = table.row()
        headers.cell(img=B7_LOGO, colspan=2, padding=3)
        headers.cell(
            "Form Pemusnahan Retained Sampel Finished Goods",
            colspan=7,
            style=FontFace(size_pt=16),
        )

    with pdf.table(col_widths=COLUMN_WIDTHS, text_align=Align.L) as table:
        headers = table.row(style=FontFace(emphasis="BOLD"))
        headers.cell("Tanggal Pemusnahan", colspan=2)
        headers.cell(date.strftime("%B %Y"), colspan=2)
        headers.cell("Jenis Produk Jadi: ")
        headers.cell("OOT", colspan=4)

        headers = table.row(style=FontFace(emphasis="BOLD"))
        headers.cell("Lokasi", colspan=2)
        headers.cell("Pulo Gadung", colspan=7)

    fill_yellow_style = FontFace(fill_color=(255, 255, 0))
    headings_style = FontFace(emphasis="BOLD", fill_color=(192, 192, 192))
    with pdf.table(
        col_widths=COLUMN_WIDTHS, text_align=Align.C, headings_style=headings_style
    ) as table:
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
            table_row.cell(str(idx + 1))
            table_row.cell(data_row.product_name)
            table_row.cell(data_row.product_code)
            table_row.cell(data_row.batch_number)
            table_row.cell(data_row.manufacturing_date.strftime("%b-%y"))
            table_row.cell(data_row.expiration_date.strftime("%b-%y"))
            table_row.cell(data_row.destroy_date.strftime("%b-%y"))
            table_row.cell(style=fill_yellow_style)
            table_row.cell(style=fill_yellow_style)

    # Save PDF to a file
    pdf.finished = True
    pdf_file_path = f"destroy-report_{date.strftime('%Y-%b-%d')}.pdf"
    # pdf.output(pdf_file_path)

    return pdf, pdf_file_path
