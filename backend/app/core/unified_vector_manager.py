#!/usr/bin/env python3
"""
Unified Vector Store Manager
Provides a single interface to switch between FAISS and Qdrant vector databases
with advanced PDF parsing, semantic chunking, hybrid search, response caching, and feedback tracking
Enhanced for production-grade RAG performance
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Import our advanced components
from .advanced_pdf_parser import get_pdf_parser
from .hybrid_search import get_hybrid_retriever
from .semantic_chunker import get_semantic_chunker
from .response_cache import get_response_cache
from .feedback_loop import get_feedback_loop, FeedbackType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedVectorManager:
    """
    Unified interface for both FAISS and Qdrant vector databases
    with advanced PDF parsing, semantic chunking, hybrid search, response caching, and feedback tracking
    Enhanced for production-grade RAG performance
    """
    
    def __init__(self, 
                 db_type: str = None, 
                 use_hybrid_search: bool = None,
                 enable_semantic_chunking: bool = None,
                 enable_response_caching: bool = None,
                 enable_feedback_tracking: bool = None):
        """Initialize the vector manager with specified database type and advanced features"""
        self.db_type = db_type or os.getenv("VECTOR_DB_TYPE", "qdrant").lower()
        self.use_hybrid_search = (
            use_hybrid_search if use_hybrid_search is not None 
            else os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true"
        )
        self.enable_semantic_chunking = (
            enable_semantic_chunking if enable_semantic_chunking is not None
            else os.getenv("ENABLE_SEMANTIC_CHUNKING", "true").lower() == "true"
        )
        self.enable_response_caching = (
            enable_response_caching if enable_response_caching is not None
            else os.getenv("ENABLE_RESPONSE_CACHING", "true").lower() == "true"
        )
        self.enable_feedback_tracking = (
            enable_feedback_tracking if enable_feedback_tracking is not None
            else os.getenv("ENABLE_FEEDBACK_TRACKING", "true").lower() == "true"
        )
        
        # Core components
        self.embeddings = None
        self.vector_store = None
        self.hybrid_retriever = None
        self.pdf_parser = None
        self.documents_cache = []  # Cache for hybrid search
        
        # Advanced RAG components
        self.semantic_chunker = None
        self.response_cache = None
        self.feedback_loop = None
        
        # Performance metrics
        self.search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0,
            "feedback_count": 0
        }
        
        # Initialize components
        self._init_embeddings()
        self._init_pdf_parser()
        self._init_advanced_components()
        self._init_vector_store()
        
        if self.use_hybrid_search:
            self._init_hybrid_search()
        
        logger.info(f"Initialized UnifiedVectorManager with {self.db_type.upper()} backend and {'hybrid' if self.use_hybrid_search else 'vector-only'} search")
    
    def _init_embeddings(self):
        """Initialize HuggingFace embeddings"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def _init_pdf_parser(self):
        """Initialize advanced PDF parser"""
        try:
            self.pdf_parser = get_pdf_parser()
            logger.info("Advanced PDF parser initialized")
        except Exception as e:
            logger.warning(f"Advanced PDF parser initialization failed: {e}. Falling back to basic parsing.")
            self.pdf_parser = None
    
    def _init_advanced_components(self):
        """Initialize advanced RAG components"""
        # Initialize semantic chunker
        if self.enable_semantic_chunking:
            try:
                self.semantic_chunker = get_semantic_chunker(
                    max_chunk_size=int(os.getenv("SEMANTIC_CHUNK_SIZE", "2000")),
                    min_chunk_size=int(os.getenv("MIN_CHUNK_SIZE", "100")),
                    overlap_sentences=int(os.getenv("CHUNK_OVERLAP_SENTENCES", "2"))
                )
                logger.info("Semantic chunker initialized")
            except Exception as e:
                logger.warning(f"Semantic chunker initialization failed: {e}")
                self.enable_semantic_chunking = False
        
        # Initialize response cache
        if self.enable_response_caching:
            try:
                self.response_cache = get_response_cache(
                    max_cache_size=int(os.getenv("CACHE_SIZE", "1000")),
                    default_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
                    similarity_threshold=float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.85"))
                )
                logger.info("Response cache initialized")
            except Exception as e:
                logger.warning(f"Response cache initialization failed: {e}")
                self.enable_response_caching = False
        
        # Initialize feedback loop
        if self.enable_feedback_tracking:
            try:
                self.feedback_loop = get_feedback_loop(
                    retention_days=int(os.getenv("FEEDBACK_RETENTION_DAYS", "90"))
                )
                logger.info("Feedback loop initialized")
            except Exception as e:
                logger.warning(f"Feedback loop initialization failed: {e}")
                self.enable_feedback_tracking = False

    def _init_hybrid_search(self):
        """Initialize hybrid search retriever"""
        try:
            self.hybrid_retriever = get_hybrid_retriever(
                vector_store=self.vector_store,
                bm25_weight=float(os.getenv("BM25_WEIGHT", "0.3")),
                vector_weight=float(os.getenv("VECTOR_WEIGHT", "0.7"))
            )
            logger.info("Hybrid search retriever initialized successfully")
        except Exception as e:
            logger.warning(f"Hybrid search initialization failed: {e}. Using vector-only search.")
            self.hybrid_retriever = None
    
    def _init_vector_store(self):
        """Initialize the appropriate vector store based on db_type"""
        if self.db_type == "qdrant":
            self._init_qdrant()
        elif self.db_type == "faiss":
            self._init_faiss()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_qdrant(self):
        """Initialize Qdrant vector store"""
        try:
            from app.core.qdrant_manager import get_qdrant_manager
            self.vector_store = get_qdrant_manager()
            logger.info("Qdrant vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {str(e)}")
            raise
    
    def _init_faiss(self):
        """Initialize FAISS vector store"""
        try:
            from langchain_community.vectorstores import FAISS
            
            faiss_path = os.getenv("FAISS_INDEX_PATH", "./vectorstore/db_faiss")
            
            if os.path.exists(f"{faiss_path}/index.faiss"):
                # Load existing FAISS index
                self.vector_store = FAISS.load_local(
                    faiss_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                logger.info(f"FAISS vector store loaded from {faiss_path}")
            else:
                # Create new FAISS index with dummy document
                dummy_texts = ["Initializing FAISS vector store"]
                self.vector_store = FAISS.from_texts(dummy_texts, self.embeddings)
                self.vector_store.save_local(faiss_path)
                logger.info(f"New FAISS vector store created at {faiss_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}")
            raise
    
    def switch_database(self, new_db_type: str) -> bool:
        """Switch to a different vector database"""
        try:
            if new_db_type.lower() not in ["qdrant", "faiss"]:
                logger.error(f"Invalid database type: {new_db_type}")
                return False
            
            if new_db_type.lower() == self.db_type:
                logger.info(f"Already using {new_db_type.upper()}")
                return True
            
            logger.info(f"Switching from {self.db_type.upper()} to {new_db_type.upper()}")
            
            # Update database type
            self.db_type = new_db_type.lower()
            
            # Reinitialize vector store
            self._init_vector_store()
            
            # Reinitialize hybrid search if enabled
            if self.use_hybrid_search:
                self._init_hybrid_search()
                # Re-fit hybrid search with cached documents
                if self.hybrid_retriever and self.documents_cache:
                    self.hybrid_retriever.fit(self.documents_cache)
            
            logger.info(f"Successfully switched to {self.db_type.upper()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch database: {str(e)}")
            return False
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 3, 
                         use_hybrid: bool = None,
                         use_cache: bool = None,
                         user_session: str = None) -> Tuple[List[Document], Dict[str, Any]]:
        """
        Perform similarity search with advanced RAG features
        
        Args:
            query: Search query
            k: Number of documents to return
            use_hybrid: Override to use/not use hybrid search for this query
            use_cache: Override to use/not use response caching for this query
            user_session: User session identifier for feedback tracking
            
        Returns:
            Tuple of (documents, metadata) where metadata includes cache info, timing, etc.
        """
        start_time = time.time()
        search_metadata = {
            "query": query,
            "k": k,
            "cached": False,
            "search_type": "unknown",
            "search_time": 0.0,
            "user_session": user_session
        }
        
        try:
            # Update search statistics
            self.search_stats["total_searches"] += 1
            
            # Check cache first if enabled
            should_use_cache = (
                use_cache if use_cache is not None
                else (self.enable_response_caching and self.response_cache is not None)
            )
            
            if should_use_cache:
                cached_result = self.response_cache.get(query, k)
                if cached_result:
                    documents, cache_metadata = cached_result
                    search_metadata.update(cache_metadata)
                    search_metadata["search_time"] = time.time() - start_time
                    
                    # Update cache hit statistics
                    self.search_stats["cache_hits"] += 1
                    
                    logger.debug(f"Cache HIT for query: '{query[:50]}...'")
                    return documents, search_metadata
            
            # Determine search strategy
            should_use_hybrid = (
                use_hybrid if use_hybrid is not None 
                else (self.use_hybrid_search and self.hybrid_retriever is not None)
            )
            
            # Perform search
            if should_use_hybrid:
                logger.debug("Using hybrid search with advanced re-ranking")
                search_metadata["search_type"] = "hybrid_advanced"
                documents = self.hybrid_retriever.search(query, k, use_advanced_rerank=True)
            else:
                logger.debug(f"Using {self.db_type} vector search")
                search_metadata["search_type"] = f"{self.db_type}_vector"
                if self.db_type == "qdrant":
                    documents = self.vector_store.similarity_search(query, k)
                elif self.db_type == "faiss":
                    documents = self.vector_store.similarity_search(query, k)
                else:
                    raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Calculate search time
            search_time = time.time() - start_time
            search_metadata["search_time"] = search_time
            
            # Update average search time
            total_searches = self.search_stats["total_searches"]
            current_avg = self.search_stats["avg_search_time"]
            self.search_stats["avg_search_time"] = ((current_avg * (total_searches - 1)) + search_time) / total_searches
            
            # Cache the results if caching is enabled
            if should_use_cache and documents:
                try:
                    # Calculate relevance score for caching (simplified)
                    relevance_score = min(1.0, len(documents) / k)  # Basic relevance based on result count
                    
                    self.response_cache.put(
                        query=query,
                        documents=documents,
                        k=k,
                        search_metadata=search_metadata,
                        relevance_score=relevance_score
                    )
                    logger.debug(f"Cached results for query: '{query[:50]}...'")
                except Exception as e:
                    logger.warning(f"Failed to cache results: {e}")
            
            return documents, search_metadata
                
        except Exception as e:
            search_metadata["error"] = str(e)
            search_metadata["search_time"] = time.time() - start_time
            logger.error(f"Error in similarity search: {str(e)}")
            return [], search_metadata

    def record_feedback(self, 
                       query: str,
                       retrieved_docs: List[Document],
                       feedback_type: str,
                       relevance_score: float = 0.0,
                       response_quality: float = 0.0,
                       missing_info: str = None,
                       suggested_improvement: str = None,
                       user_session: str = None,
                       response_time: float = None) -> Optional[str]:
        """
        Record user feedback for a search query
        
        Args:
            query: Original search query
            retrieved_docs: Documents that were retrieved
            feedback_type: Type of feedback (relevant, irrelevant, etc.)
            relevance_score: Relevance score (0-1)
            response_quality: Overall response quality (0-1)
            missing_info: Information that was missing
            suggested_improvement: User's suggestion for improvement
            user_session: User session identifier
            response_time: Response time in seconds
            
        Returns:
            Feedback entry ID if successful, None otherwise
        """
        if not self.enable_feedback_tracking or not self.feedback_loop:
            logger.debug("Feedback tracking not enabled")
            return None
        
        try:
            # Convert string feedback type to enum
            feedback_enum = getattr(FeedbackType, feedback_type.upper(), FeedbackType.RELEVANT)
            
            feedback_id = self.feedback_loop.record_feedback(
                query=query,
                retrieved_docs=retrieved_docs,
                feedback_type=feedback_enum,
                relevance_score=relevance_score,
                response_quality=response_quality,
                missing_info=missing_info,
                suggested_improvement=suggested_improvement,
                user_session=user_session,
                response_time=response_time
            )
            
            # Update feedback statistics
            self.search_stats["feedback_count"] += 1
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return None
    
    def add_documents(self, 
                     texts: List[str], 
                     metadatas: List[Dict] = None,
                     use_semantic_chunking: bool = None) -> bool:
        """
        Add documents to the current vector database with optional semantic chunking
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries
            use_semantic_chunking: Override semantic chunking setting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine if we should use semantic chunking
            should_use_semantic = (
                use_semantic_chunking if use_semantic_chunking is not None
                else (self.enable_semantic_chunking and self.semantic_chunker is not None)
            )
            
            # Process documents with semantic chunking if enabled
            if should_use_semantic:
                logger.info(f"Processing {len(texts)} documents with semantic chunking")
                all_documents = []
                
                for text, metadata in zip(texts, metadatas or [{}] * len(texts)):
                    try:
                        # Use semantic chunker to create meaningful chunks
                        semantic_docs = self.semantic_chunker.chunk_document(text, metadata)
                        all_documents.extend(semantic_docs)
                        logger.debug(f"Created {len(semantic_docs)} semantic chunks from document")
                    except Exception as e:
                        logger.warning(f"Semantic chunking failed for document, using original: {e}")
                        # Fallback to original document
                        all_documents.append(Document(page_content=text, metadata=metadata or {}))
                
                logger.info(f"Total semantic chunks created: {len(all_documents)}")
                
                # Get chunking statistics
                if all_documents:
                    stats = self.semantic_chunker.get_chunking_stats(all_documents)
                    logger.info(f"Chunking stats: {stats}")
                
            else:
                # Create Document objects without semantic chunking
                all_documents = [
                    Document(page_content=text, metadata=metadata or {})
                    for text, metadata in zip(texts, metadatas or [{}] * len(texts))
                ]
            
            # Add to documents cache for hybrid search
            self.documents_cache.extend(all_documents)
            
            # Extract texts and metadatas for vector store
            document_texts = [doc.page_content for doc in all_documents]
            document_metadatas = [doc.metadata for doc in all_documents]
            
            # Add to vector store
            if self.db_type == "qdrant":
                success = self.vector_store.add_documents(document_texts, document_metadatas)
            elif self.db_type == "faiss":
                # For FAISS, add texts and save
                self.vector_store.add_texts(texts, metadatas or [])
                faiss_path = os.getenv("FAISS_INDEX_PATH", "./vectorstore/db_faiss")
                self.vector_store.save_local(faiss_path)
                success = True
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Update hybrid search with new documents
            if success and self.hybrid_retriever:
                self.hybrid_retriever.fit(self.documents_cache)
                logger.info("Updated hybrid search with new documents")
            
            return success
                
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about the current vector database"""
        try:
            status = {
                "database_type": self.db_type.upper(),
                "status": "ready",
                "message": f"Using {self.db_type.upper()} vector database"
            }
            
            if self.db_type == "qdrant":
                # Get Qdrant-specific info
                is_healthy, error_msg = self.vector_store.health_check()
                if is_healthy:
                    collection_info = self.vector_store.get_collection_info()
                    status["documents_count"] = collection_info.get("points_count", 0)
                    status["collection_name"] = self.vector_store.collection_name
                else:
                    status["status"] = "not_ready"
                    if error_msg:
                        status["message"] = f"Qdrant service not available: {error_msg}"
                    else:
                        status["message"] = "Qdrant service not available"
                    
            elif self.db_type == "faiss":
                # Get FAISS-specific info
                faiss_path = os.getenv("FAISS_INDEX_PATH", "./vectorstore/db_faiss")
                if os.path.exists(f"{faiss_path}/index.faiss"):
                    # Try to get document count (approximate)
                    status["documents_count"] = "Available"
                    status["index_path"] = faiss_path
                else:
                    status["status"] = "not_ready"
                    status["message"] = "FAISS index not found"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                "database_type": self.db_type.upper(),
                "status": "error",
                "message": f"Error: {str(e)}"
            }
    
    def get_available_databases(self) -> List[str]:
        """Get list of available vector database types"""
        return ["qdrant", "faiss"]
    
    def parse_pdf_advanced(self, file_path: str, method: str = "hybrid") -> tuple:
        """
        Parse PDF using advanced parser
        
        Returns:
            tuple: (extracted_text, metadata)
        """
        if self.pdf_parser:
            return self.pdf_parser.parse_pdf(file_path, method)
        else:
            # Fallback to basic PyPDF parsing
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text.strip(), {
                    "parser": "pypdf-fallback",
                    "pages": len(reader.pages),
                    "success": True
                }
            except Exception as e:
                return "", {"parser": "pypdf-fallback", "success": False, "error": str(e)}
    
    def get_search_explanation(self, query: str, k: int = 3) -> Dict[str, Any]:
        """Get detailed explanation of search results for debugging"""
        if self.hybrid_retriever:
            return self.hybrid_retriever.get_search_explanation(query, k)
        else:
            # Simple explanation for vector-only search
            try:
                results = self.similarity_search(query, k, use_hybrid=False)
                return {
                    "query": query,
                    "search_type": f"{self.db_type}_only",
                    "results": [
                        {
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "metadata": doc.metadata
                        }
                        for doc in results
                    ]
                }
            except Exception as e:
                return {"error": str(e)}
    
    def update_hybrid_weights(self, bm25_weight: float, vector_weight: float):
        """Update hybrid search weights"""
        if self.hybrid_retriever:
            self.hybrid_retriever.update_weights(bm25_weight, vector_weight)
    
    def get_document_count(self) -> int:
        """Get number of cached documents for hybrid search"""
        return len(self.documents_cache)
    
    def clear_document_cache(self):
        """Clear the document cache"""
        self.documents_cache = []
        if self.hybrid_retriever:
            self.hybrid_retriever.fit([])  # Reset with empty documents

    def clear_database(self) -> bool:
        """Clear all documents from the current database"""
        try:
            logger.info(f"Clearing {self.db_type.upper()} database...")
            
            if self.db_type == "qdrant":
                # For Qdrant, recreate the collection
                if hasattr(self.vector_store, 'recreate_collection'):
                    success = self.vector_store.recreate_collection()
                    if success:
                        logger.info("Qdrant collection recreated successfully")
                        # Clear documents cache and reinitialize hybrid search
                        self.documents_cache = []
                        if self.hybrid_retriever:
                            self.hybrid_retriever.fit([])
                        return True
                else:
                    logger.warning("Qdrant clear method not available")
                    return False
                    
            elif self.db_type == "faiss":
                # For FAISS, remove the index files and reinitialize
                faiss_path = os.getenv("FAISS_INDEX_PATH", "./vectorstore/db_faiss")
                if os.path.exists(faiss_path):
                    import shutil
                    shutil.rmtree(faiss_path)
                    logger.info(f"Removed FAISS index at {faiss_path}")
                
                # Reinitialize FAISS
                self._init_faiss()
                
                # Clear documents cache and reinitialize hybrid search
                self.documents_cache = []
                if self.hybrid_retriever:
                    self.hybrid_retriever.fit([])
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return False
    
    def get_documents_count(self) -> int:
        """Get the current number of documents in the database"""
        try:
            status = self.get_status()
            return status.get('documents_count', 0)
        except Exception as e:
            logger.error(f"Error getting documents count: {str(e)}")
            return 0
    
    def bulk_add_documents(self, documents_data: List[Dict], batch_size: int = 50) -> bool:
        """
        Add multiple documents in batches for better performance
        
        Args:
            documents_data: List of dictionaries with 'text' and 'metadata' keys
            batch_size: Number of documents to process in each batch
            
        Returns:
            bool: True if all batches were successful
        """
        try:
            total_docs = len(documents_data)
            logger.info(f"Bulk adding {total_docs} documents in batches of {batch_size}")
            
            successful_batches = 0
            total_batches = (total_docs + batch_size - 1) // batch_size
            
            for i in range(0, total_docs, batch_size):
                batch = documents_data[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")
                
                # Prepare texts and metadata for this batch
                texts = [doc["text"] for doc in batch]
                metadatas = [doc["metadata"] for doc in batch]
                
                # Add batch to database
                success = self.add_documents(texts, metadatas)
                
                if success:
                    successful_batches += 1
                    logger.info(f"Batch {batch_num} added successfully")
                else:
                    logger.error(f"Batch {batch_num} failed")
            
            success_rate = successful_batches / total_batches
            logger.info(f"Bulk add completed: {successful_batches}/{total_batches} batches successful ({success_rate:.1%})")
            
            return successful_batches == total_batches
            
        except Exception as e:
            logger.error(f"Error in bulk add documents: {str(e)}")
            return False
    
    def rechunk_documents(self, parsing_method: str = "hybrid") -> Dict:
        """
        Re-chunk existing documents with enhanced parsing
        
        Args:
            parsing_method: Method to use for PDF parsing ('hybrid', 'pdfminer', etc.)
            
        Returns:
            Dict with rechunking results
        """
        try:
            logger.info(f"Starting document re-chunking with {parsing_method} parsing")
            
            # Get current document count for comparison
            initial_count = self.get_documents_count()
            
            # Import the rechunker
            from scripts.rechunk_with_enhanced_parsing import DocumentReChunker
            
            # Create rechunker instance
            rechunker = DocumentReChunker()
            
            # Run re-chunking for current database type only
            result = rechunker.run_rechunking(target_databases=[self.db_type])
            
            if result.get("success"):
                final_count = self.get_documents_count()
                
                # Handle case where document count might be string (like 'Available' for FAISS)
                try:
                    if isinstance(initial_count, str) or isinstance(final_count, str):
                        # For FAISS, we can't calculate exact count change
                        result["initial_count"] = initial_count
                        result["final_count"] = final_count
                        result["count_change"] = "Documents updated (exact count unavailable for FAISS)"
                    else:
                        result["initial_count"] = initial_count
                        result["final_count"] = final_count
                        result["count_change"] = final_count - initial_count
                except Exception:
                    result["initial_count"] = initial_count
                    result["final_count"] = final_count
                    result["count_change"] = "Count calculation unavailable"
                
                logger.info(f"Re-chunking completed: {initial_count} -> {final_count} documents")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during re-chunking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Re-chunking failed"
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for the RAG system
        
        Returns:
            Dictionary containing performance metrics
        """
        metrics = {
            "search_performance": self.search_stats.copy(),
            "database_info": {
                "type": self.db_type,
                "status": self.get_status(),
                "cached_documents": len(self.documents_cache)
            },
            "advanced_features": {
                "semantic_chunking_enabled": self.enable_semantic_chunking,
                "response_caching_enabled": self.enable_response_caching,
                "feedback_tracking_enabled": self.enable_feedback_tracking,
                "hybrid_search_enabled": self.use_hybrid_search
            }
        }
        
        # Add cache statistics if available
        if self.response_cache:
            try:
                cache_stats = self.response_cache.get_cache_stats()
                metrics["cache_performance"] = cache_stats
            except Exception as e:
                logger.warning(f"Failed to get cache stats: {e}")
        
        # Add feedback statistics if available
        if self.feedback_loop:
            try:
                feedback_summary = self.feedback_loop.get_feedback_summary(days=30)
                metrics["feedback_performance"] = feedback_summary
            except Exception as e:
                logger.warning(f"Failed to get feedback stats: {e}")
        
        return metrics

    def get_system_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get system optimization recommendations based on performance data
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        try:
            # Performance-based recommendations
            if self.search_stats["avg_search_time"] > 2.0:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "title": "Optimize Search Performance",
                    "description": f"Average search time is {self.search_stats['avg_search_time']:.2f}s",
                    "suggestions": [
                        "Enable response caching if not already enabled",
                        "Consider optimizing vector database configuration",
                        "Review document chunking strategy"
                    ]
                })
            
            # Cache utilization recommendations
            if self.response_cache:
                cache_stats = self.response_cache.get_cache_stats()
                if cache_stats.get("hit_rate", 0) < 0.3:
                    recommendations.append({
                        "type": "caching",
                        "priority": "low",
                        "title": "Improve Cache Utilization",
                        "description": f"Cache hit rate is {cache_stats.get('hit_rate', 0):.1%}",
                        "suggestions": [
                            "Review cache similarity threshold",
                            "Increase cache TTL for stable queries",
                            "Analyze query patterns for better caching"
                        ]
                    })
            
            # Get feedback-based recommendations
            if self.feedback_loop:
                feedback_recommendations = self.feedback_loop.get_improvement_recommendations()
                recommendations.extend(feedback_recommendations)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations

    def cleanup_resources(self):
        """
        Cleanup system resources and perform maintenance tasks
        """
        try:
            # Cleanup expired cache entries
            if self.response_cache:
                self.response_cache.cleanup_expired()
                logger.info("Cache cleanup completed")
            
            # Cleanup old feedback data
            if self.feedback_loop:
                self.feedback_loop.cleanup_old_data()
                logger.info("Feedback cleanup completed")
            
            # Reset performance statistics
            self.search_stats = {
                "total_searches": 0,
                "cache_hits": 0,
                "avg_search_time": 0.0,
                "feedback_count": 0
            }
            
            logger.info("Resource cleanup completed")
            
        except Exception as e:
            logger.error(f"Resource cleanup failed: {e}")

    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for analytics dashboard
        
        Returns:
            Dictionary containing dashboard data
        """
        dashboard_data = {
            "overview": {
                "total_searches": self.search_stats["total_searches"],
                "cache_hit_rate": 0.0,
                "avg_search_time": self.search_stats["avg_search_time"],
                "total_documents": len(self.documents_cache),
                "feedback_entries": self.search_stats["feedback_count"]
            },
            "performance_trends": {},
            "popular_queries": [],
            "problematic_queries": [],
            "system_health": "good"
        }
        
        try:
            # Add cache metrics
            if self.response_cache:
                cache_stats = self.response_cache.get_cache_stats()
                dashboard_data["overview"]["cache_hit_rate"] = cache_stats.get("hit_rate", 0.0)
                dashboard_data["popular_queries"] = self.response_cache.get_popular_queries(10)
            
            # Add feedback metrics and problematic queries
            if self.feedback_loop:
                dashboard_data["problematic_queries"] = self.feedback_loop.get_problematic_queries(10)
                feedback_summary = self.feedback_loop.get_feedback_summary(30)
                dashboard_data["overview"]["satisfaction_rate"] = feedback_summary.get("satisfaction_rate", 0.0)
            
            # Determine system health
            if dashboard_data["overview"]["avg_search_time"] > 3.0:
                dashboard_data["system_health"] = "warning"
            if dashboard_data["overview"]["cache_hit_rate"] < 0.2:
                dashboard_data["system_health"] = "warning"
            if dashboard_data["overview"]["satisfaction_rate"] < 0.6:
                dashboard_data["system_health"] = "critical"
                
        except Exception as e:
            logger.error(f"Failed to generate dashboard data: {e}")
            dashboard_data["error"] = str(e)
        
        return dashboard_data


# Global instance
_unified_manager = None

def get_unified_manager() -> UnifiedVectorManager:
    """Get the global unified vector manager instance"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = UnifiedVectorManager()
    return _unified_manager

def switch_vector_database(db_type: str) -> bool:
    """Switch the global vector database"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = UnifiedVectorManager(db_type)
        return True
    return _unified_manager.switch_database(db_type)


if __name__ == "__main__":
    # Test the unified manager
    manager = UnifiedVectorManager()
    print(f"Current database: {manager.db_type}")
    print(f"Status: {manager.get_status()}")
    
    # Test switching
    print(f"Switching to FAISS...")
    success = manager.switch_database("faiss")
    print(f"Switch successful: {success}")
    print(f"New status: {manager.get_status()}")