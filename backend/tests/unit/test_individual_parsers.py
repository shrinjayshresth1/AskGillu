from advanced_pdf_parser import get_pdf_parser
import os

parser = get_pdf_parser()
docs_dir = '../docs'
pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]

if pdf_files:
    test_file = pdf_files[0]
    file_path = os.path.join(docs_dir, test_file)
    print(f'Testing: {test_file}')
    
    # Test each parser individually
    methods = [
        ('PyPDF', parser.extract_text_pypdf),
        ('PDFPlumber', parser.extract_text_pdfplumber),
        ('PyMuPDF', parser.extract_text_pymupdf)
    ]
    
    for name, method in methods:
        try:
            text, meta = method(file_path)
            print(f'{name}: {len(text)} chars, Success: {meta.get("success")}')
            if text and len(text) > 100:
                print(f'  Preview: {text[:100]}...')
            print()
        except Exception as e:
            print(f'{name}: Error - {e}\n')
else:
    print('No PDF files found')