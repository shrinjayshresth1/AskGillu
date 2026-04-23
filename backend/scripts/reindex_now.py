import os
import sys
from datetime import datetime

# Add the parent directory to sys.path to import app
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.unified_vector_manager import get_unified_manager
from langchain_text_splitters import RecursiveCharacterTextSplitter

def reindex_now():
    """
    Force re-index: wipe the current Qdrant collection and re-ingest all documents fresh.
    Uses the new chunk_size (4000) defined in main.py logic.
    """
    vector_manager = get_unified_manager()
    print(f"[REINDEX] Starting forced re-indexing on {vector_manager.db_type.upper()}...")
    
    # 1. Delete and recreate collection if Qdrant
    if vector_manager.db_type == "qdrant":
        try:
            vector_manager.vector_store.delete_collection()
            print("[REINDEX] Deleted existing Qdrant collection.")
        except Exception as e:
            print(f"[REINDEX] Could not delete collection (may not exist): {e}")
        
        vector_manager.vector_store.create_collection()
        print("[REINDEX] Recreated empty Qdrant collection.")
    
    # 2. Process documents
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    allowed_docs = ["srmu_brochure.pdf", "srmu_rules.pdf", "fee_structure.pdf", "academic_calendar.pdf"] # Common ones from history
    
    # Actually, let's get them from the allowed list if we can, 
    # but since we're a standalone script we'll just look for all PDFs in docs/
    import glob
    pdf_files = glob.glob(os.path.join(docs_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"[REINDEX] No PDF files found in {docs_dir}")
        return

    all_texts = []
    processed_files = []
    
    for file_path in pdf_files:
        doc_name = os.path.basename(file_path)
        print(f"[REINDEX] Processing {doc_name}...")
        try:
            raw_text, metadata = vector_manager.parse_pdf_advanced(file_path, method="hybrid")
            if raw_text.strip():
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
                    chunk_size=4000,
                    chunk_overlap=1000,
                    length_function=len
                )
                texts = text_splitter.split_text(raw_text)
                all_texts.extend(texts)
                processed_files.append(doc_name)
                print(f"   - Generated {len(texts)} chunks")
        except Exception as e:
            print(f"   - Error: {e}")

    if all_texts:
        metadatas = [
            {"source": "srmu_documents", "chunk_id": i, "processed_at": datetime.now().isoformat()}
            for i in range(len(all_texts))
        ]
        
        print(f"[REINDEX] Adding {len(all_texts)} chunks to vector store...")
        success = vector_manager.add_documents(all_texts, metadatas)
        if success:
            print("[REINDEX] ✅ Successfully re-indexed all documents.")
        else:
            print("[REINDEX] ❌ Failed to add documents.")
    else:
        print("[REINDEX] No text extracted from documents.")

if __name__ == "__main__":
    reindex_now()
