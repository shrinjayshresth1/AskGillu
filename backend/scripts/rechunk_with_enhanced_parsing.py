#!/usr/bin/env python3
"""
Re-chunk existing documents with enhanced PDF parsing
Updates both Qdrant and FAISS databases with improved text extraction
"""

import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from unified_vector_manager import get_unified_manager, switch_vector_database
from advanced_pdf_parser import get_pdf_parser
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentReChunker:
    """Re-chunk documents with enhanced parsing and update vector databases"""
    
    def __init__(self):
        self.docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        self.backup_dir = os.path.join(os.path.dirname(__file__), "backup")
        self.pdf_parser = get_pdf_parser()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize both vector managers
        self.qdrant_manager = None
        self.faiss_manager = None
        
    def create_backup(self) -> Dict[str, str]:
        """Create backup of current vector databases"""
        backup_info = {
            "timestamp": datetime.now().isoformat(),
            "backup_dir": self.backup_dir,
            "backups": {}
        }
        
        print("🔄 Creating backup of current databases...")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Backup FAISS if it exists
        faiss_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore", "db_faiss")
        if os.path.exists(faiss_path):
            backup_faiss_path = os.path.join(self.backup_dir, f"faiss_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(faiss_path, backup_faiss_path)
            backup_info["backups"]["faiss"] = backup_faiss_path
            print(f"   ✅ FAISS backed up to: {backup_faiss_path}")
        
        # For Qdrant, we'll create a status snapshot (cloud-based, so we note current state)
        try:
            vm = get_unified_manager()
            if vm.db_type == "qdrant":
                status = vm.get_status()
                backup_info["backups"]["qdrant"] = {
                    "documents_count": status.get('documents_count', 0),
                    "collection_name": status.get('collection_name', 'askgillu_documents'),
                    "note": "Qdrant is cloud-based - manual recreation required if rollback needed"
                }
                print(f"   ✅ Qdrant status recorded: {status.get('documents_count', 0)} documents")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not backup Qdrant status - {e}")
        
        # Save backup info
        backup_info_file = os.path.join(self.backup_dir, "backup_info.json")
        with open(backup_info_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Backup completed: {backup_info_file}")
        return backup_info
    
    def get_document_list(self) -> List[str]:
        """Get list of PDF documents to re-chunk"""
        pdf_files = []
        
        # Get all PDFs from docs directory
        if os.path.exists(self.docs_dir):
            for file in os.listdir(self.docs_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)
        
        return pdf_files
    
    def extract_enhanced_text(self, file_path: str) -> tuple:
        """Extract text using enhanced parsing methods"""
        print(f"   📄 Parsing: {os.path.basename(file_path)}")
        
        # Use hybrid method for best results
        text, metadata = self.pdf_parser.parse_pdf(file_path, method="hybrid")
        
        if metadata.get("success") and text:
            print(f"   ✅ Extracted {len(text)} characters using {metadata.get('parser', 'unknown')}")
            return text, metadata
        else:
            print(f"   ❌ Failed to extract text: {metadata.get('error', 'Unknown error')}")
            return "", metadata
    
    def create_enhanced_chunks(self, text: str, filename: str, metadata: Dict) -> List[Dict]:
        """Create text chunks with enhanced metadata"""
        if not text.strip():
            return []
        
        # Split text into chunks
        texts = self.text_splitter.split_text(text)
        
        chunks = []
        for i, chunk_text in enumerate(texts):
            chunk_metadata = {
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(texts),
                "parsing_method": metadata.get("parser", "unknown"),
                "extraction_method": metadata.get("method", "standard"),
                "timestamp": datetime.now().isoformat(),
                "enhanced": True,  # Mark as enhanced chunk
                "original_pages": metadata.get("pages", "unknown"),
                "chunk_length": len(chunk_text)
            }
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def clear_database(self, db_type: str):
        """Clear existing documents from database"""
        print(f"🗑️  Clearing {db_type.upper()} database...")
        
        if db_type == "qdrant":
            # Switch to Qdrant and clear
            switch_vector_database("qdrant")
            vm = get_unified_manager()
            # Note: For Qdrant, we'll need to recreate the collection
            # This is handled by the vector manager when we add new documents
            
        elif db_type == "faiss":
            # For FAISS, remove the index files
            faiss_path = os.path.join(os.path.dirname(__file__), "..", "vectorstore", "db_faiss")
            if os.path.exists(faiss_path):
                shutil.rmtree(faiss_path)
                print(f"   ✅ Removed FAISS index at {faiss_path}")
    
    def rechunk_to_database(self, db_type: str, all_chunks: List[Dict]) -> bool:
        """Add enhanced chunks to specified database"""
        print(f"📊 Adding {len(all_chunks)} enhanced chunks to {db_type.upper()}...")
        
        # Switch to the target database
        switch_vector_database(db_type)
        vm = get_unified_manager()
        
        # Prepare texts and metadata
        texts = [chunk["text"] for chunk in all_chunks]
        metadatas = [chunk["metadata"] for chunk in all_chunks]
        
        # Add to vector database
        success = vm.add_documents(texts, metadatas)
        
        if success:
            # Get updated status
            status = vm.get_status()
            print(f"   ✅ Successfully added to {db_type.upper()}")
            print(f"   📊 Total documents now: {status.get('documents_count', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Failed to add documents to {db_type.upper()}")
            return False
    
    def run_rechunking(self, target_databases: List[str] = None) -> Dict:
        """Main method to re-chunk all documents"""
        if target_databases is None:
            target_databases = ["qdrant", "faiss"]
        
        print("🚀 STARTING ENHANCED RE-CHUNKING PROCESS")
        print("=" * 60)
        
        # Step 1: Create backup
        backup_info = self.create_backup()
        
        # Step 2: Get document list
        pdf_files = self.get_document_list()
        print(f"\n📚 Found {len(pdf_files)} PDF documents to re-chunk:")
        for pdf in pdf_files:
            print(f"   📄 {pdf}")
        
        if not pdf_files:
            print("❌ No PDF files found to process")
            return {"success": False, "message": "No PDF files found"}
        
        # Step 3: Extract enhanced text from all documents
        print(f"\n🔄 PHASE 1: Enhanced Text Extraction")
        print("-" * 40)
        
        all_chunks = []
        processed_files = []
        failed_files = []
        
        for pdf_file in pdf_files:
            file_path = os.path.join(self.docs_dir, pdf_file)
            
            try:
                # Extract with enhanced parsing
                text, metadata = self.extract_enhanced_text(file_path)
                
                if text:
                    # Create enhanced chunks
                    chunks = self.create_enhanced_chunks(text, pdf_file, metadata)
                    all_chunks.extend(chunks)
                    processed_files.append(pdf_file)
                    print(f"   ✅ {pdf_file}: {len(chunks)} chunks created")
                else:
                    failed_files.append(pdf_file)
                    print(f"   ❌ {pdf_file}: No text extracted")
                    
            except Exception as e:
                failed_files.append(pdf_file)
                print(f"   ❌ {pdf_file}: Error - {e}")
        
        print(f"\n📊 Extraction Summary:")
        print(f"   ✅ Processed: {len(processed_files)} files")
        print(f"   ❌ Failed: {len(failed_files)} files")
        print(f"   📦 Total chunks: {len(all_chunks)}")
        
        if not all_chunks:
            print("❌ No chunks created - aborting re-chunking")
            return {"success": False, "message": "No chunks created"}
        
        # Step 4: Update databases
        print(f"\n🔄 PHASE 2: Database Updates")
        print("-" * 40)
        
        results = {}
        
        for db_type in target_databases:
            print(f"\n🗄️  Processing {db_type.upper()} database...")
            
            try:
                # Clear existing data
                self.clear_database(db_type)
                
                # Add enhanced chunks
                success = self.rechunk_to_database(db_type, all_chunks)
                results[db_type] = {"success": success}
                
                if success:
                    print(f"   🎉 {db_type.upper()} successfully updated!")
                else:
                    print(f"   ❌ {db_type.upper()} update failed!")
                    
            except Exception as e:
                print(f"   ❌ {db_type.upper()} error: {e}")
                results[db_type] = {"success": False, "error": str(e)}
        
        # Step 5: Summary
        print(f"\n🎉 RE-CHUNKING COMPLETED!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   📄 Documents processed: {len(processed_files)}")
        print(f"   📦 Total chunks created: {len(all_chunks)}")
        print(f"   🔄 Enhanced parsing: ✅ pdfminer.six + hybrid selection")
        print(f"   🗄️  Databases updated:")
        
        for db_type, result in results.items():
            status = "✅" if result.get("success") else "❌"
            print(f"      {status} {db_type.upper()}")
        
        print(f"\n💾 Backup location: {backup_info['backup_dir']}")
        
        return {
            "success": True,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_chunks": len(all_chunks),
            "database_results": results,
            "backup_info": backup_info
        }


def main():
    """Command-line interface for re-chunking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Re-chunk documents with enhanced parsing")
    parser.add_argument("--databases", nargs="+", choices=["qdrant", "faiss"], 
                       default=["qdrant", "faiss"], help="Databases to update")
    parser.add_argument("--backup", action="store_true", default=True, 
                       help="Create backup before re-chunking")
    
    args = parser.parse_args()
    
    rechunker = DocumentReChunker()
    result = rechunker.run_rechunking(target_databases=args.databases)
    
    if result["success"]:
        print("\n🎊 Re-chunking completed successfully!")
    else:
        print(f"\n❌ Re-chunking failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    main()