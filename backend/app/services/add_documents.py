#!/usr/bin/env python3
"""
Script to add new documents to your vector database system.
Works with both Qdrant and FAISS automatically.
"""

import os
import sys
from unified_vector_manager import get_unified_manager

def add_single_pdf(file_path):
    """Add a single PDF file to the vector database"""
    print(f"📄 Adding PDF: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Get the unified manager
    vm = get_unified_manager()
    
    # Check current database
    status = vm.get_status()
    print(f"🗄️  Current database: {status.get('database_type', 'Unknown')}")
    print(f"📊 Current documents: {status.get('documents_count', 'Unknown')}")
    
    # Add the PDF
    print("🔄 Processing PDF with advanced parsing...")
    success = vm.add_pdf(file_path)
    
    if success:
        print("✅ PDF successfully added!")
        
        # Check new status
        new_status = vm.get_status()
        new_count = new_status.get('documents_count', 'Unknown')
        print(f"📊 Total documents now: {new_count}")
        
        # Test search with content from the new document
        print("\n🔍 Testing search with new content...")
        test_query = input("Enter a test query for the new document: ").strip()
        if test_query:
            results = vm.similarity_search(test_query, k=2)
            print(f"Found {len(results)} results:")
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.page_content[:100]}...")
    else:
        print("❌ Failed to add PDF")
    
    return success

def add_text_documents():
    """Add text documents interactively"""
    print("📝 Adding text documents")
    
    documents = []
    metadatas = []
    
    while True:
        print(f"\n--- Document {len(documents) + 1} ---")
        content = input("Enter document content (or 'done' to finish): ").strip()
        
        if content.lower() == 'done':
            break
            
        if content:
            title = input("Enter document title: ").strip()
            source = input("Enter source/filename: ").strip()
            
            documents.append(content)
            metadatas.append({
                "title": title or f"Document {len(documents)}",
                "source": source or "manual_entry",
                "type": "text"
            })
    
    if documents:
        vm = get_unified_manager()
        print(f"\n🔄 Adding {len(documents)} documents...")
        success = vm.add_documents(documents, metadatas)
        
        if success:
            print("✅ All documents added successfully!")
        else:
            print("❌ Failed to add documents")
    else:
        print("No documents to add.")

def bulk_add_pdfs_from_folder():
    """Add all PDFs from a folder"""
    folder_path = input("Enter folder path containing PDFs: ").strip()
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in folder.")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    
    confirm = input(f"\nAdd all {len(pdf_files)} PDFs? (y/n): ").strip().lower()
    
    if confirm == 'y':
        vm = get_unified_manager()
        success_count = 0
        
        for pdf in pdf_files:
            file_path = os.path.join(folder_path, pdf)
            print(f"\n🔄 Processing: {pdf}")
            
            if vm.add_pdf(file_path):
                success_count += 1
                print(f"✅ Added: {pdf}")
            else:
                print(f"❌ Failed: {pdf}")
        
        print(f"\n🎉 Successfully added {success_count}/{len(pdf_files)} PDFs")

def main():
    """Main menu for adding documents"""
    print("=" * 50)
    print("📚 ADD DOCUMENTS TO VECTOR DATABASE")
    print("=" * 50)
    
    # Show current status
    try:
        vm = get_unified_manager()
        status = vm.get_status()
        print(f"🗄️  Current database: {status.get('database_type', 'Unknown')}")
        print(f"📊 Current documents: {status.get('documents_count', 'Unknown')}")
        print(f"🔍 Hybrid search: {'Enabled' if vm.use_hybrid_search else 'Disabled'}")
    except Exception as e:
        print(f"⚠️  Warning: Could not get status - {e}")
    
    print("\nOptions:")
    print("1. Add single PDF file")
    print("2. Add text documents")
    print("3. Bulk add PDFs from folder")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        file_path = input("Enter PDF file path: ").strip()
        add_single_pdf(file_path)
    elif choice == "2":
        add_text_documents()
    elif choice == "3":
        bulk_add_pdfs_from_folder()
    elif choice == "4":
        print("👋 Goodbye!")
        return
    else:
        print("Invalid option. Please try again.")
        main()

if __name__ == "__main__":
    main()