"""
Qdrant Vector Database Utilities for ASK_GILLU
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class QdrantManager:
    """
    Manager class for Qdrant vector database operations
    """
    
    def __init__(self):
        # Configuration
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # Handle URL construction properly
        if self.qdrant_host.startswith(("http://", "https://")):
            # Host already contains protocol
            self.qdrant_url = self.qdrant_host
        elif self.qdrant_host == ":memory:":
            # Memory mode
            self.qdrant_url = ":memory:"
        else:
            # Local host without protocol
            self.qdrant_url = f"http://{self.qdrant_host}:{self.qdrant_port}"
            
        # Override with explicit QDRANT_URL if provided
        self.qdrant_url = os.getenv("QDRANT_URL", self.qdrant_url)
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "srmu_documents")
        
        # Initialize Qdrant client
        if self.qdrant_host == ":memory:":
            # Use in-memory mode
            self.client = QdrantClient(":memory:")
            self.qdrant_url = ":memory:"
        elif self.qdrant_api_key:
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key
            )
        else:
            # For local Qdrant instance without API key
            self.client = QdrantClient(url=self.qdrant_url)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Get embedding dimension
        sample_text = "sample"
        self.embedding_dim = len(self.embeddings.embed_query(sample_text))
        
        logger.info(f"Initialized QdrantManager with URL: {self.qdrant_url}")
        logger.info(f"Collection: {self.collection_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def create_collection(self) -> bool:
        """
        Create a new collection in Qdrant
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created collection '{self.collection_name}' successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> bool:
        """
        Add documents to the Qdrant collection
        """
        try:
            # Ensure collection exists
            if not self.create_collection():
                return False
            
            # Generate embeddings for all texts
            embeddings = self.embeddings.embed_documents(texts)
            
            # Prepare points for Qdrant
            points = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                point_id = str(uuid.uuid4())
                
                # Prepare metadata
                payload = {
                    "text": text,
                    "source": "document",
                    "index": i
                }
                
                # Add custom metadata if provided
                if metadatas and i < len(metadatas):
                    payload.update(metadatas[i])
                
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                ))
            
            # Upsert points to collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} documents to collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 3, score_threshold: float = 0.0) -> List:
        """
        Perform similarity search in the Qdrant collection
        Returns LangChain Document objects for compatibility
        """
        try:
            # Import here to avoid circular imports
            from langchain.schema import Document
            
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                score_threshold=score_threshold
            )
            
            # Format results as LangChain Document objects
            documents = []
            for result in search_results:
                doc = Document(
                    page_content=result.payload.get("text", ""),
                    metadata={
                        "id": result.id,
                        "score": result.score,
                        **{k: v for k, v in result.payload.items() if k != "text"}
                    }
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} similar documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def delete_collection(self) -> bool:
        """
        Delete the collection
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """
        Clear all points from the collection
        """
        try:
            # Delete all points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter()  # Empty filter deletes all
            )
            logger.info(f"Cleared all points from collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def update_document(self, point_id: str, text: str, metadata: Optional[Dict] = None) -> bool:
        """
        Update a specific document in the collection
        """
        try:
            # Generate new embedding
            embedding = self.embeddings.embed_query(text)
            
            # Prepare payload
            payload = {"text": text}
            if metadata:
                payload.update(metadata)
            
            # Update point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )]
            )
            
            logger.info(f"Updated document with ID: {point_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy
        """
        try:
            collections = self.client.get_collections()
            logger.info("Qdrant health check: OK")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False


def get_qdrant_manager() -> QdrantManager:
    """
    Factory function to get QdrantManager instance
    """
    return QdrantManager()


# For backward compatibility with existing code
class QdrantVectorStore:
    """
    Wrapper class to provide FAISS-like interface for Qdrant
    """
    
    def __init__(self, qdrant_manager: QdrantManager):
        self.qdrant_manager = qdrant_manager
    
    @classmethod
    def from_texts(cls, texts: List[str], embeddings, metadatas: Optional[List[Dict]] = None):
        """
        Create QdrantVectorStore from texts (similar to FAISS.from_texts)
        """
        manager = get_qdrant_manager()
        manager.add_documents(texts, metadatas)
        return cls(manager)
    
    def similarity_search(self, query: str, k: int = 3):
        """
        Perform similarity search (compatible with FAISS interface)
        """
        results = self.qdrant_manager.similarity_search(query, k)
        
        # Convert to LangChain Document format for compatibility
        from langchain.schema import Document
        
        documents = []
        for result in results:
            doc = Document(
                page_content=result["text"],
                metadata=result["metadata"]
            )
            documents.append(doc)
        
        return documents
    
    def as_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        Return as retriever for LangChain compatibility
        """
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        
        class QdrantRetriever:
            def __init__(self, vector_store, search_kwargs):
                self.vector_store = vector_store
                self.search_kwargs = search_kwargs
            
            def get_relevant_documents(self, query: str):
                return self.vector_store.similarity_search(query, **self.search_kwargs)
        
        return QdrantRetriever(self, search_kwargs)