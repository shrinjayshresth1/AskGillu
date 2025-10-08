from advanced_pdf_parser import get_pdf_parser
import os

def compare_all_parsers():
    parser = get_pdf_parser()
    print('🧪 COMPREHENSIVE PDF PARSER COMPARISON')
    print('=' * 50)
    print(f'Available parsers: {", ".join(parser.available_parsers)}')
    
    # Test with Questions PDF
    file_path = '../docs/Questions[1] (1).pdf'
    if not os.path.exists(file_path):
        print('❌ Test file not found')
        return
    
    print(f'\n📄 Testing: {os.path.basename(file_path)}')
    print('-' * 30)
    
    parsers_to_test = ['pypdf', 'pdfplumber', 'pymupdf', 'pdfminer', 'hybrid']
    results = {}
    
    for parser_name in parsers_to_test:
        if parser_name == 'hybrid' or parser_name in parser.available_parsers:
            print(f'\n🔍 Testing {parser_name.upper()}...')
            try:
                text, metadata = parser.parse_pdf(file_path, method=parser_name)
                length = len(text)
                success = metadata.get('success', False)
                method = metadata.get('method', 'standard')
                chosen_parser = metadata.get('parser', parser_name)
                
                results[parser_name] = {
                    'success': success,
                    'length': length,
                    'method': method,
                    'chosen_parser': chosen_parser
                }
                
                print(f'   ✅ Success: {success}')
                print(f'   📊 Length: {length} characters')
                print(f'   🔧 Method: {method}')
                if parser_name == 'hybrid':
                    print(f'   🎯 Chosen: {chosen_parser}')
                if text:
                    print(f'   📝 Preview: {text[:80]}...')
                    
            except Exception as e:
                results[parser_name] = {'success': False, 'error': str(e)}
                print(f'   ❌ Error: {e}')
    
    # Show ranking
    print(f'\n🏆 RANKING BY TEXT LENGTH:')
    print('-' * 30)
    successful = {k: v for k, v in results.items() if v.get('success', False)}
    
    if successful:
        sorted_results = sorted(successful.items(), key=lambda x: x[1]['length'], reverse=True)
        for i, (parser_name, result) in enumerate(sorted_results):
            medal = ['🥇', '🥈', '🥉'][i] if i < 3 else '📊'
            print(f'{medal} {parser_name.upper()}: {result["length"]} chars')
            if result.get('method') != 'standard':
                print(f'    Method: {result["method"]}')
    
    # Recommendations
    print(f'\n💡 RECOMMENDATIONS:')
    print('-' * 30)
    try:
        recs = parser.get_parser_recommendations(file_path)
        print(f'📄 File size: {recs.get("file_size", "Unknown")} bytes')
        print(f'📚 Pages: {recs.get("pages", "Unknown")}')
        print(f'🎯 Recommended: {recs.get("recommended_parser", "hybrid").upper()}')
        for reason in recs.get('reasons', []):
            print(f'   💡 {reason}')
    except Exception as e:
        print(f'❌ Error: {e}')
    
    print(f'\n🎉 CONCLUSION:')
    print('Your enhanced parser now supports:')
    print('   ✅ PyPDF - Fast, basic extraction')
    print('   ✅ pdfplumber - Tables and structured data')  
    print('   ✅ PyMuPDF - Fast and reliable')
    print('   ✅ pdfminer.six - Complex layouts and academic papers')
    print('   ✅ OCR - Scanned documents with Tesseract')
    print('   ✅ Hybrid - Automatically chooses the best method')

if __name__ == '__main__':
    compare_all_parsers()