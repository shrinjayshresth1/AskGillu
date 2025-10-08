from advanced_pdf_parser import get_pdf_parser
import os

# Test the working PDF
test_file = "Questions[1] (1).pdf"
file_path = os.path.join('../docs', test_file)

print(f'=== COMPARISON: {test_file} ===\n')

# 1. OLD METHOD: Basic PyPDF (equivalent to what was used before)
print('1. OLD METHOD (Basic PyPDF):')
parser = get_pdf_parser()
old_text, old_meta = parser.extract_text_pypdf(file_path)
print(f'   Length: {len(old_text)} characters')
print(f'   Success: {old_meta.get("success")}')
if old_text:
    print(f'   Preview: {old_text[:150]}...')
else:
    print('   Preview: [No text extracted]')

print('\n' + '='*50 + '\n')

# 2. NEW METHOD: Advanced parsing
print('2. NEW METHOD (Advanced Multi-Parser):')
parser = get_pdf_parser()
new_text, meta = parser.extract_text_hybrid(file_path)
print(f'   Length: {len(new_text)} characters')
print(f'   Parser used: {meta.get("parser", "unknown")}')
print(f'   Preview: {new_text[:150]}...')

print('\n' + '='*50 + '\n')

# 3. COMPARISON
print('3. QUALITY COMPARISON:')
improvement = len(new_text) - len(old_text)
print(f'   Improvement: +{improvement} characters')
if old_text:
    percentage = ((len(new_text) / len(old_text)) - 1) * 100
    print(f'   Quality gain: {percentage:.1f}%')

# 4. RECOMMENDATION
print('\n4. RE-CHUNKING RECOMMENDATION:')
if improvement > 100:  # Significant improvement
    print('   ✅ RECOMMENDED: Re-chunk for better quality')
    print(f'   ✅ Expected improvement: {improvement} chars per document')
else:
    print('   ⚠️  OPTIONAL: Minimal improvement detected')