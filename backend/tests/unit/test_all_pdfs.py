from advanced_pdf_parser import get_pdf_parser
import os

parser = get_pdf_parser()
docs_dir = '../docs'
pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]

print(f'Available PDFs: {pdf_files}')

for pdf_file in pdf_files:
    file_path = os.path.join(docs_dir, pdf_file)
    print(f'\n=== Testing: {pdf_file} ===')
    
    # Test PyMuPDF (usually most reliable)
    try:
        text, meta = parser.extract_text_pymupdf(file_path)
        print(f'PyMuPDF: {len(text)} chars, Success: {meta.get("success")}')
        if text and len(text) > 50:
            print(f'Preview: {text[:100]}...')
            break  # Found a working PDF
    except Exception as e:
        print(f'PyMuPDF Error: {e}')

# If no working PDF found, create a test scenario
if not any(True for pdf in pdf_files):
    print('\nNo PDFs extracted successfully - checking system status...')