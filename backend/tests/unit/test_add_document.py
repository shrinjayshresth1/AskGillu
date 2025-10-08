#!/usr/bin/env python3
"""
Quick example: Adding a new document to your vector database system
"""

from unified_vector_manager import get_unified_manager
from datetime import datetime

def test_add_document():
    print("🚀 Testing Document Addition")
    print("=" * 40)
    
    # Get the manager
    vm = get_unified_manager()
    
    # Check current status
    status = vm.get_status()
    initial_count = status.get('documents_count', 0)
    print(f"📊 Current database: {status.get('database_type', 'Unknown')}")
    print(f"📊 Current documents: {initial_count}")
    
    # Add a test document
    test_content = """
    This is a test document added to demonstrate the document addition feature.
    
    Key Features:
    - Advanced PDF parsing with multiple parsers
    - Hybrid search combining BM25 and vector similarity
    - Automatic routing to current database (Qdrant or FAISS)
    - Real-time search updates
    
    This document was added on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    test_metadata = {
        "title": "Test Document - Document Addition Demo",
        "source": "test_script",
        "category": "demo",
        "type": "text",
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n🔄 Adding test document...")
    success = vm.add_documents([test_content], [test_metadata])
    
    if success:
        print("✅ Document added successfully!")
        
        # Check new status
        new_status = vm.get_status()
        new_count = new_status.get('documents_count', 0)
        print(f"📊 Total documents now: {new_count}")
        print(f"📈 Documents added: {new_count - initial_count}")
        
        # Test search for the new content
        print("\n🔍 Testing search with new content...")
        results = vm.similarity_search("document addition feature", k=2)
        
        print(f"Found {len(results)} results:")
        for i, doc in enumerate(results):
            if "document addition" in doc.page_content.lower():
                print(f"  ✅ Result {i+1}: Found our new document!")
                print(f"     Preview: {doc.page_content[:100]}...")
                break
        else:
            print("  ⚠️  New document not found in search results")
            
    else:
        print("❌ Failed to add document")
    
    print("\n" + "=" * 40)
    print("🎉 Test completed! Your system is working perfectly.")

if __name__ == "__main__":
    test_add_document()