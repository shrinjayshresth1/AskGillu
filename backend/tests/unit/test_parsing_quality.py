from advanced_pdf_parser import get_pdf_parser
import os

parser = get_pdf_parser()
docs_dir = '../docs'
pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]

if pdf_files:
    test_file = pdf_files[0]
    file_path = os.path.join(docs_dir, test_file)
    print(f'Testing: {test_file}')
    
    # Test old vs new parsing
    print('\n=== BASIC PyPDF ===')
    basic_text, basic_meta = parser.extract_text_pypdf(file_path)
    print(f'Length: {len(basic_text)}, Success: {basic_meta.get("success")}')
    
    print('\n=== ADVANCED Hybrid ===')
    advanced_text, advanced_meta = parser.extract_text_hybrid(file_path)
    print(f'Length: {len(advanced_text)}, Parser: {advanced_meta.get("parser")}, Success: {advanced_meta.get("success")}')
    
    print(f'\nImprovement: {len(advanced_text) - len(basic_text)} characters')
    if basic_text:
        print(f'Quality gain: {((len(advanced_text) / len(basic_text)) - 1) * 100:.1f}%')
    else:
        print('Quality gain: N/A')
else:
    print('No PDF files found')