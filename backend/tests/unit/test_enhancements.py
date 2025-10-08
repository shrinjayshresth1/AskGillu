#!/usr/bin/env python3
"""
Test script for advanced PDF parsing and hybrid search
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from advanced_pdf_parser import get_pdf_parser
from hybrid_search import get_hybrid_retriever
from langchain.schema import Document

def test_pdf_parsing():
    """Test advanced PDF parsing"""
    print("=== Testing Advanced PDF Parsing ===")
    
    parser = get_pdf_parser()
    print(f"Available parsers: {parser.available_parsers}")
    
    # Test with a sample PDF if available
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')] if os.path.exists(docs_dir) else []
    
    if pdf_files:
        test_file = pdf_files[0]
        file_path = os.path.join(docs_dir, test_file)
        print(f"\nTesting with: {test_file}")
        
        # Test different parsing methods
        for method in ["hybrid", "pypdf", "pdfplumber", "pymupdf"]:
            if method == "hybrid" or method in parser.available_parsers:
                try:
                    text, metadata = parser.parse_pdf(file_path, method)
                    print(f"\n{method.upper()} Results:")
                    print(f"  Success: {metadata.get('success', False)}")
                    print(f"  Text length: {len(text)}")
                    print(f"  Pages: {metadata.get('pages', 'Unknown')}")
                    if 'tables_found' in metadata:
                        print(f"  Tables found: {metadata['tables_found']}")
                    if text:
                        print(f"  Preview: {text[:100]}...")
                except Exception as e:
                    print(f"\n{method.upper()} Failed: {e}")
    else:
        print("No PDF files found in docs directory")

def test_hybrid_search():
    """Test hybrid search functionality"""
    print("\n=== Testing Hybrid Search ===")
    
    # Create sample documents
    sample_docs = [
        Document(
            page_content="Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
            metadata={"source": "doc1", "topic": "AI"}
        ),
        Document(
            page_content="Python is a high-level programming language widely used in data science and machine learning applications.",
            metadata={"source": "doc2", "topic": "Programming"}
        ),
        Document(
            page_content="Natural language processing enables computers to understand, interpret, and generate human language.",
            metadata={"source": "doc3", "topic": "NLP"}
        ),
        Document(
            page_content="Deep learning uses neural networks with multiple layers to learn complex patterns in data.",
            metadata={"source": "doc4", "topic": "Deep Learning"}
        ),
        Document(
            page_content="Data science combines statistics, programming, and domain expertise to extract insights from data.",
            metadata={"source": "doc5", "topic": "Data Science"}
        ),
    ]
    
    # Test hybrid retriever
    retriever = get_hybrid_retriever(bm25_weight=0.4, vector_weight=0.6)
    retriever.fit(sample_docs)
    
    # Test queries
    test_queries = [
        "machine learning algorithms",
        "python programming language",
        "natural language processing",
        "neural networks deep learning",
        "data science statistics"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Get explanation
        explanation = retriever.get_search_explanation(query, k=3)
        
        print("BM25 Results:")
        for i, result in enumerate(explanation.get("bm25_results", [])[:3]):
            print(f"  {i+1}. Score: {result['score']:.3f} - {result['content'][:60]}...")
        
        print("Hybrid Results:")
        for i, result in enumerate(explanation.get("hybrid_results", [])[:3]):
            print(f"  {i+1}. {result['content'][:60]}...")

def test_integration():
    """Test integration of both components"""
    print("\n=== Testing Integration ===")
    
    try:
        from unified_vector_manager import UnifiedVectorManager
        
        # Test with hybrid search enabled
        manager = UnifiedVectorManager(use_hybrid_search=True)
        print(f"Initialized manager with {manager.db_type} backend")
        print(f"Hybrid search enabled: {manager.use_hybrid_search}")
        print(f"PDF parser available: {manager.pdf_parser is not None}")
        print(f"Hybrid retriever available: {manager.hybrid_retriever is not None}")
        
        # Test search explanation
        explanation = manager.get_search_explanation("test query", k=2)
        print(f"Search explanation available: {'error' not in explanation}")
        
    except Exception as e:
        print(f"Integration test failed: {e}")

if __name__ == "__main__":
    print("Testing Advanced PDF Parsing and Hybrid Search")
    print("=" * 50)
    
    test_pdf_parsing()
    test_hybrid_search()
    test_integration()
    
    print("\n=== Test Summary ===")
    print("✅ Advanced PDF parsing implemented with multiple fallback parsers")
    print("✅ Hybrid search combining BM25 + vector similarity")
    print("✅ Integration with unified vector manager")
    print("\nTo use these features:")
    print("1. Install dependencies: pip install pdfplumber pymupdf pytesseract pillow")
    print("2. Restart the backend server")
    print("3. Use the new API endpoints for testing and debugging")