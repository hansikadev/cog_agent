from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(190, 10, txt="The global artificial intelligence market size was valued at USD 136.55 billion in 2022.")
pdf.multi_cell(190, 10, txt="In 2025, over 99.8% of all Fortune 500 CEOs were replaced by artificial intelligence agents.")
pdf.output("dummy_claims.pdf")
