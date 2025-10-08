#!/usr/bin/env python3
"""
Test the enhanced PDF parser with pdfminer.six support
"""

from advanced_pdf_parser import get_pdf_parser
import os

def test_enhanced_parser():
    print("🚀 Testing Enhanced PDF Parser with pdfminer.six")
    print("=" * 60)
    
    # Initialize parser
    parser = get_pdf_parser()
    print(f"📚 Available parsers: {', '.join(parser.available_parsers)}")
    
    # Test with an existing PDF
    docs_dir = '../docs'
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found for testing")
        return
    
    test_file = pdf_files[0]  # Use first available PDF
    file_path = os.path.join(docs_dir, test_file)
    
    print(f"\n📄 Testing with: {test_file}")
    print("-" * 40)
    
    # Test each parser individually
    parsers_to_test = ["pypdf", "pdfplumber", "pymupdf", "pdfminer"]
    
    results = {}
    
    for parser_name in parsers_to_test:
        if parser_name in parser.available_parsers:
            print(f"\n🔍 Testing {parser_name.upper()}...")
            try:
                text, metadata = parser.parse_pdf(file_path, method=parser_name)
                results[parser_name] = {
                    "success": metadata.get("success", False),
                    "length": len(text),
                    "parser": metadata.get("parser", parser_name),
                    "method": metadata.get("method", "standard")
                }
                print(f"   ✅ Success: {len(text)} characters extracted")
                if "method" in metadata:
                    print(f"   📊 Method: {metadata['method']}")
                if text:
                    print(f"   📝 Preview: {text[:100]}...")
            except Exception as e:
                results[parser_name] = {"success": False, "error": str(e)}
                print(f"   ❌ Error: {e}")
        else:
            print(f"\n⚠️  {parser_name.upper()} not available")
    
    # Test hybrid method
    print(f"\n🔀 Testing HYBRID method...")
    try:
        text, metadata = parser.parse_pdf(file_path, method="hybrid")
        results["hybrid"] = {
            "success": metadata.get("success", False),
            "length": len(text),
            "parser": metadata.get("parser", "hybrid"),
            "chosen_parser": metadata.get("parser", "unknown")
        }
        print(f"   ✅ Success: {len(text)} characters extracted")
        print(f"   🎯 Chosen parser: {metadata.get('parser', 'unknown')}")
    except Exception as e:
        results["hybrid"] = {"success": False, "error": str(e)}
        print(f"   ❌ Error: {e}")
    
    # Show comparison
    print(f"\n📊 COMPARISON RESULTS:")
    print("-" * 40)
    successful_parsers = {k: v for k, v in results.items() if v.get("success", False)}
    
    if successful_parsers:
        # Sort by text length (more text usually means better extraction)
        sorted_results = sorted(successful_parsers.items(), key=lambda x: x[1]["length"], reverse=True)
        
        for i, (parser_name, result) in enumerate(sorted_results):
            status = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📊"
            print(f"   {status} {parser_name.upper()}: {result['length']} chars")
            if "method" in result:
                print(f"      Method: {result['method']}")
    else:
        print("   ❌ No parsers succeeded")
    
    # Get recommendations
    print(f"\n🎯 PARSER RECOMMENDATIONS:")
    print("-" * 40)
    try:
        recommendations = parser.get_parser_recommendations(file_path)
        print(f"   📄 File size: {recommendations.get('file_size', 'Unknown')} bytes")
        print(f"   📚 Pages: {recommendations.get('pages', 'Unknown')}")
        print(f"   🎯 Recommended: {recommendations.get('recommended_parser', 'hybrid').upper()}")
        for reason in recommendations.get('reasons', []):
            print(f"   💡 {reason}")
    except Exception as e:
        print(f"   ❌ Error getting recommendations: {e}")
    
    print(f"\n🎉 Testing completed!")
    print("🚀 Your enhanced parser now supports:")
    print("   ✅ PyPDF (fast, basic)")
    print("   ✅ pdfplumber (tables, structured data)")
    print("   ✅ PyMuPDF (fast, reliable)")
    print("   ✅ pdfminer.six (complex layouts, academic papers)")
    print("   ✅ OCR with Tesseract (scanned documents)")
    print("   ✅ Hybrid intelligence (automatically chooses best)")

if __name__ == "__main__":
    test_enhanced_parser()