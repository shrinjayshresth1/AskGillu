#!/usr/bin/env python3

from qdrant_manager import get_qdrant_manager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_similarity_search():
    print("Testing Qdrant similarity search...")
    
    # Get manager
    manager = get_qdrant_manager()
    
    # Test search
    query = "admission status"
    docs = manager.similarity_search(query, k=3)
    
    print(f"Found {len(docs)} documents for query: '{query}'")
    
    for i, doc in enumerate(docs):
        print(f"\nDoc {i+1}:")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Score: {doc.metadata.get('score', 'N/A')}")
        print(f"Metadata: {list(doc.metadata.keys())}")
        print("-" * 50)

if __name__ == "__main__":
    test_similarity_search()