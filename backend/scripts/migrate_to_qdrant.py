"""
Migration script to transfer data from FAISS to Qdrant
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from qdrant_manager import get_qdrant_manager
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_texts_from_faiss_backup() -> List[str]:
    """
    Extract texts from original document sources as backup method
    """
    texts = []
    
    # Configuration - documents to process
    ALLOWED_DOCUMENTS = [
        "Questions[1] (1).pdf",
        "Shrinjay Shresth Resume DataScience.pdf", 
        "Web-Based-GIS.pdf"
    ]
    
    docs_dir = Path("../docs")
    
    for doc_name in ALLOWED_DOCUMENTS:
        doc_path = docs_dir / doc_name
        
        if doc_path.exists():
            logger.info(f"Processing document: {doc_name}")
            
            try:
                reader = PdfReader(str(doc_path))
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                if text.strip():
                    # Split text into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000,
                        chunk_overlap=200
                    )
                    chunks = text_splitter.split_text(text)
                    texts.extend(chunks)
                    logger.info(f"Extracted {len(chunks)} chunks from {doc_name}")
                
            except Exception as e:
                logger.error(f"Error processing {doc_name}: {str(e)}")
        else:
            logger.warning(f"Document not found: {doc_path}")
    
    logger.info(f"Total texts extracted: {len(texts)}")
    return texts

def migrate_faiss_to_qdrant():
    """
    Main migration function
    """
    logger.info("Starting FAISS to Qdrant migration...")
    
    try:
        # Initialize Qdrant manager
        qdrant_manager = get_qdrant_manager()
        
        # Check Qdrant health
        if not qdrant_manager.health_check():
            logger.error("Qdrant service is not available. Please start Qdrant service.")
            return False
        
        # Try to load existing FAISS data first
        faiss_path = "vectorstore/db_faiss"
        texts = []
        
        if os.path.exists(faiss_path):
            try:
                logger.info("Attempting to extract data from existing FAISS index...")
                
                # Initialize embeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                
                # Load FAISS
                vectorstore = FAISS.load_local(
                    faiss_path, 
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
                
                # FAISS doesn't easily expose original texts, so we'll use document sources
                logger.info("FAISS loaded, but extracting original texts from documents...")
                
            except Exception as e:
                logger.warning(f"Could not load FAISS data: {str(e)}")
        
        # Extract texts from original documents
        texts = extract_texts_from_faiss_backup()
        
        if not texts:
            logger.error("No texts found to migrate")
            return False
        
        # Clear existing Qdrant collection if it exists
        logger.info("Clearing existing Qdrant collection...")
        qdrant_manager.clear_collection()
        
        # Add documents to Qdrant
        logger.info(f"Adding {len(texts)} documents to Qdrant...")
        
        # Prepare metadata
        metadatas = []
        for i, text in enumerate(texts):
            metadatas.append({
                "source": "srmu_documents",
                "migrated_from": "faiss",
                "chunk_id": i
            })
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            
            success = qdrant_manager.add_documents(batch_texts, batch_metadatas)
            if success:
                logger.info(f"Added batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            else:
                logger.error(f"Failed to add batch {i//batch_size + 1}")
                return False
        
        # Verify migration
        collection_info = qdrant_manager.get_collection_info()
        logger.info(f"Migration completed! Collection info: {collection_info}")
        
        # Test search functionality
        logger.info("Testing search functionality...")
        test_results = qdrant_manager.similarity_search("What is SRMU?", k=3)
        logger.info(f"Test search returned {len(test_results)} results")
        
        if test_results:
            logger.info("Sample result:")
            logger.info(f"Text: {test_results[0]['text'][:200]}...")
            logger.info(f"Score: {test_results[0]['score']}")
        
        logger.info("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

def verify_qdrant_setup():
    """
    Verify that Qdrant is properly set up
    """
    logger.info("Verifying Qdrant setup...")
    
    try:
        qdrant_manager = get_qdrant_manager()
        
        # Health check
        if not qdrant_manager.health_check():
            logger.error("❌ Qdrant service is not available")
            logger.info("To start Qdrant locally, run:")
            logger.info("docker run -p 6333:6333 qdrant/qdrant")
            return False
        
        # Collection info
        try:
            collection_info = qdrant_manager.get_collection_info()
            logger.info(f"✅ Collection info: {collection_info}")
        except:
            logger.info("Collection doesn't exist yet - will be created during migration")
        
        logger.info("✅ Qdrant setup verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Qdrant setup verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FAISS to Qdrant Migration Tool")
    parser.add_argument("--verify", action="store_true", help="Only verify Qdrant setup")
    parser.add_argument("--migrate", action="store_true", help="Perform migration")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_qdrant_setup()
    elif args.migrate:
        if verify_qdrant_setup():
            migrate_faiss_to_qdrant()
        else:
            logger.error("Qdrant setup verification failed. Cannot proceed with migration.")
    else:
        logger.info("Usage:")
        logger.info("  python migrate_to_qdrant.py --verify   # Verify Qdrant setup")
        logger.info("  python migrate_to_qdrant.py --migrate  # Perform migration")