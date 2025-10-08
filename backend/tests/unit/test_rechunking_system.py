#!/usr/bin/env python3
"""
Test the complete re-chunking system to ensure it works properly
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from unified_vector_manager import UnifiedVectorManager
from rechunk_with_enhanced_parsing import DocumentReChunker

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_rechunking_system():
    """Test the complete re-chunking system"""
    print("=" * 60)
    print("TESTING RE-CHUNKING SYSTEM")
    print("=" * 60)
    
    # Test both database types
    db_types = ["qdrant", "faiss"]
    
    for db_type in db_types:
        print(f"\n{'='*20} Testing {db_type.upper()} {'='*20}")
        
        try:
            # Initialize vector manager
            print(f"Initializing {db_type} vector manager...")
            vm = UnifiedVectorManager(db_type=db_type)
            
            # Get initial status
            initial_status = vm.get_status()
            print(f"Initial status: {initial_status}")
            
            # Test clear_database method
            print(f"\nTesting clear_database method...")
            clear_result = vm.clear_database()
            print(f"Clear result: {clear_result}")
            
            # Check status after clearing
            cleared_status = vm.get_status()
            print(f"Status after clearing: {cleared_status}")
            
            # Test rechunk_documents method
            print(f"\nTesting rechunk_documents method...")
            rechunk_result = vm.rechunk_documents(parsing_method="hybrid")
            print(f"Rechunk result: {rechunk_result}")
            
            # Get final status
            final_status = vm.get_status()
            print(f"Final status: {final_status}")
            
            # Test search functionality
            print(f"\nTesting search after re-chunking...")
            search_results = vm.search("student queries", k=3, search_type="hybrid")
            print(f"Found {len(search_results)} results")
            
            if search_results:
                print("Sample result metadata:")
                print(search_results[0].get('metadata', 'No metadata'))
            
        except Exception as e:
            print(f"Error testing {db_type}: {str(e)}")
            import traceback
            traceback.print_exc()

def test_individual_components():
    """Test individual components separately"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL COMPONENTS")
    print("=" * 60)
    
    # Test DocumentReChunker
    print("\nTesting DocumentReChunker...")
    try:
        rechunker = DocumentReChunker()
        
        # Test backup creation
        print("Creating backup...")
        backup_result = rechunker.create_backup()
        print(f"Backup result: {backup_result}")
        
        # Test document listing
        print("Listing available documents...")
        docs_path = Path("../docs")
        if docs_path.exists():
            pdf_files = list(docs_path.glob("*.pdf"))
            print(f"Found {len(pdf_files)} PDF files:")
            for pdf in pdf_files:
                print(f"  - {pdf.name}")
        
    except Exception as e:
        print(f"Error testing DocumentReChunker: {str(e)}")
        import traceback
        traceback.print_exc()

def test_enhanced_parsing():
    """Test the enhanced parsing capabilities"""
    print("\n" + "="*60)
    print("TESTING ENHANCED PARSING")
    print("=" * 60)
    
    try:
        from advanced_pdf_parser import AdvancedPDFParser
        
        parser = AdvancedPDFParser()
        
        # Find a test PDF
        docs_path = Path("../docs")
        if docs_path.exists():
            pdf_files = list(docs_path.glob("*.pdf"))
            if pdf_files:
                test_pdf = pdf_files[0]
                print(f"Testing parsing with: {test_pdf.name}")
                
                # Test different parsing methods
                methods = ["hybrid", "pdfminer", "pypdf", "pdfplumber"]
                
                for method in methods:
                    try:
                        print(f"\nTesting {method} method...")
                        text = parser.extract_text(str(test_pdf), method=method)
                        print(f"Extracted {len(text)} characters")
                        print(f"First 100 chars: {text[:100]}...")
                    except Exception as e:
                        print(f"Error with {method}: {str(e)}")
            else:
                print("No PDF files found for testing")
        else:
            print("Docs directory not found")
            
    except Exception as e:
        print(f"Error testing enhanced parsing: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main test runner"""
    setup_logging()
    
    print("Starting comprehensive re-chunking system test...")
    
    # Test individual components first
    test_individual_components()
    test_enhanced_parsing()
    
    # Test the complete system
    test_rechunking_system()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()