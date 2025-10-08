from advanced_pdf_parser import get_pdf_parser
import os

parser = get_pdf_parser()
print('Testing pdfminer extraction...')

# Test with Questions PDF
file_path = '../docs/Questions[1] (1).pdf'
if os.path.exists(file_path):
    text, metadata = parser.parse_pdf(file_path, method='pdfminer')
    print(f'pdfminer: {len(text)} chars, Success: {metadata.get("success")}')
    print(f'Method used: {metadata.get("method", "unknown")}')
    if text:
        print(f'Preview: {text[:100]}...')
else:
    print('Test file not found')