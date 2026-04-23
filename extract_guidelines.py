from pypdf import PdfReader

def extract_pdf():
    reader = PdfReader('projetreportfor.pdf')
    with open('report_guidelines.txt', 'w', encoding='utf-8') as f:
        for page in reader.pages:
            text = page.extract_text()
            if text:
                f.write(text + '\n')

if __name__ == "__main__":
    extract_pdf()
