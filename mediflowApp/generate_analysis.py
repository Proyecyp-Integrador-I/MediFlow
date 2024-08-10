from fpdf import FPDF

def generate_analysis_pdf(file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('helvetica', size=12)
    pdf.add_page()

    pdf.cell(40,10, text=f"Analysis: {file.result_analysis}", border=True)
    pdf.output(f"media/analysis_exam_{file.id}.pdf")