#!/usr/bin/env python3
"""
Hybrid Search Implementation
Combines BM25 keyword search with vector similarity search for better retrieval
Enhanced with advanced re-ranking capabilities for production-grade RAG
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import re
import math
from collections import Counter, defaultdict
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import advanced re-ranker
try:
    from .advanced_reranker import get_advanced_reranker, ReRankingStrategy
    ADVANCED_RERANKER_AVAILABLE = True
except ImportError:
    logger.warning("Advanced re-ranker not available")
    ADVANCED_RERANKER_AVAILABLE = False

class BM25Retriever:
    """
    BM25 (Best Matching 25) algorithm implementation for keyword-based search
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 retriever
        
        Args:
            k1: Controls term frequency saturation (typically 1.2-2.0)
            b: Controls length normalization (typically 0.75)
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.tokenized_docs = []
        self.doc_frequencies = {}
        self.idf_scores = {}
        self.avgdl = 0.0
        self.doc_lengths = []
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization and preprocessing"""
        # Convert to lowercase and split on non-alphanumeric characters
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _compute_idf(self):
        """Compute IDF (Inverse Document Frequency) scores"""
        n_docs = len(self.documents)
        
        for term, df in self.doc_frequencies.items():
            # IDF = log((N - df + 0.5) / (df + 0.5))
            idf = math.log((n_docs - df + 0.5) / (df + 0.5))
            self.idf_scores[term] = max(idf, 0.01)  # Avoid negative IDF
    
    def fit(self, documents: List[Document]):
        """
        Fit BM25 on a collection of documents
        
        Args:
            documents: List of LangChain Document objects
        """
        self.documents = documents
        self.tokenized_docs = []
        self.doc_frequencies = defaultdict(int)
        self.doc_lengths = []
        
        # Tokenize all documents and compute statistics
        for doc in documents:
            tokens = self._tokenize(doc.page_content)
            self.tokenized_docs.append(tokens)
            self.doc_lengths.append(len(tokens))
            
            # Count term frequencies across documents
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_frequencies[token] += 1
        
        # Compute average document length
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Compute IDF scores
        self._compute_idf()
        
        logger.info(f"BM25 fitted on {len(documents)} documents")
        logger.info(f"Vocabulary size: {len(self.doc_frequencies)}")
        logger.info(f"Average document length: {self.avgdl:.2f}")
    
    def _score_document(self, query_tokens: List[str], doc_tokens: List[str], doc_length: int) -> float:
        """Calculate BM25 score for a single document"""
        score = 0.0
        doc_token_counts = Counter(doc_tokens)
        
        for token in query_tokens:
            if token in doc_token_counts:
                tf = doc_token_counts[token]  # Term frequency in document
                idf = self.idf_scores.get(token, 0.01)  # IDF score
                
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
                score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """
        Search for top-k documents using BM25
        
        Args:
            query: Search query string
            k: Number of top documents to return
            
        Returns:
            List of (Document, score) tuples sorted by relevance
        """
        if not self.documents:
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        # Score all documents
        scores = []
        for i, (doc, doc_tokens) in enumerate(zip(self.documents, self.tokenized_docs)):
            score = self._score_document(query_tokens, doc_tokens, self.doc_lengths[i])
            scores.append((doc, score))
        
        # Sort by score and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]


class HybridRetriever:
    """
    Hybrid retriever combining BM25 keyword search with vector similarity search
    Enhanced with advanced re-ranking for production-grade RAG
    """
    
    def __init__(self, 
                 vector_store=None,
                 bm25_weight: float = 0.3,
                 vector_weight: float = 0.7,
                 min_bm25_score: float = 0.1,
                 enable_advanced_rerank: bool = True,
                 rerank_strategy: str = "hybrid_weighted"):
        """
        Initialize hybrid retriever
        
        Args:
            vector_store: Vector store instance (Qdrant or FAISS)
            bm25_weight: Weight for BM25 scores (0-1)
            vector_weight: Weight for vector similarity scores (0-1)
            min_bm25_score: Minimum BM25 score threshold
            enable_advanced_rerank: Whether to use advanced re-ranking
            rerank_strategy: Re-ranking strategy to use
        """
        self.vector_store = vector_store
        self.bm25_retriever = BM25Retriever()
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.min_bm25_score = min_bm25_score
        self.enable_advanced_rerank = enable_advanced_rerank and ADVANCED_RERANKER_AVAILABLE
        
        # Ensure weights sum to 1
        total_weight = bm25_weight + vector_weight
        if total_weight != 1.0:
            self.bm25_weight = bm25_weight / total_weight
            self.vector_weight = vector_weight / total_weight
        
        # Initialize advanced re-ranker if available
        self.advanced_reranker = None
        if self.enable_advanced_rerank:
            try:
                self.advanced_reranker = get_advanced_reranker()
                self.rerank_strategy = getattr(ReRankingStrategy, rerank_strategy.upper(), ReRankingStrategy.HYBRID_WEIGHTED)
                logger.info(f"Advanced re-ranker initialized with strategy: {rerank_strategy}")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced re-ranker: {e}")
                self.enable_advanced_rerank = False
        
        logger.info(f"Hybrid retriever initialized with BM25 weight: {self.bm25_weight:.2f}, Vector weight: {self.vector_weight:.2f}")
    
    def fit(self, documents: List[Document]):
        """
        Fit the BM25 retriever on documents
        (Vector store should already be populated)
        """
        self.bm25_retriever.fit(documents)
        logger.info("Hybrid retriever fitted successfully")
    
    def search(self, query: str, k: int = 10, rerank: bool = True, use_advanced_rerank: bool = None) -> List[Document]:
        """
        Perform hybrid search combining BM25 and vector similarity
        
        Args:
            query: Search query
            k: Number of documents to return
            rerank: Whether to rerank results using combined scores
            use_advanced_rerank: Override advanced re-ranking setting for this query
            
        Returns:
            List of top-k documents
        """
        if not self.vector_store:
            logger.warning("No vector store available, falling back to BM25 only")
            bm25_results = self.bm25_retriever.search(query, k)
            return [doc for doc, score in bm25_results]
        
        # Determine if we should use advanced re-ranking
        should_use_advanced = (
            use_advanced_rerank if use_advanced_rerank is not None 
            else (self.enable_advanced_rerank and self.advanced_reranker is not None)
        )
        
        # Get more candidates if using advanced re-ranking
        candidate_multiplier = 3 if should_use_advanced else 2
        
        # Get results from both retrievers
        try:
            # Vector similarity search
            vector_results = self.vector_store.similarity_search(query, k=k*candidate_multiplier)
            logger.debug(f"Vector search returned {len(vector_results)} results")
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            vector_results = []
        
        # BM25 keyword search
        try:
            bm25_results = self.bm25_retriever.search(query, k=k*candidate_multiplier)
            logger.debug(f"BM25 search returned {len(bm25_results)} results")
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            bm25_results = []
        
        if not vector_results and not bm25_results:
            return []
        
        # Use advanced re-ranking if available and enabled
        if should_use_advanced and rerank:
            try:
                logger.debug(f"Using advanced re-ranking with strategy: {self.rerank_strategy}")
                reranked_docs = self.advanced_reranker.rerank_documents(
                    query=query,
                    bm25_results=bm25_results,
                    vector_results=vector_results,
                    strategy=self.rerank_strategy,
                    k=k
                )
                return reranked_docs
            except Exception as e:
                logger.error(f"Advanced re-ranking failed: {e}. Falling back to basic re-ranking")
                # Fall through to basic re-ranking
        
        if not rerank:
            # Simple concatenation without reranking
            seen_content = set()
            combined_results = []
            
            # Add vector results first
            for doc in vector_results:
                if doc.page_content not in seen_content:
                    combined_results.append(doc)
                    seen_content.add(doc.page_content)
            
            # Add BM25 results
            for doc, score in bm25_results:
                if doc.page_content not in seen_content and score >= self.min_bm25_score:
                    combined_results.append(doc)
                    seen_content.add(doc.page_content)
            
            return combined_results[:k]
        
        # Rerank using basic combined scores
        return self._rerank_results(query, vector_results, bm25_results, k)
    
    def _rerank_results(self, 
                       query: str, 
                       vector_results: List[Document], 
                       bm25_results: List[Tuple[Document, float]], 
                       k: int) -> List[Document]:
        """
        Rerank results by combining BM25 and vector similarity scores
        """
        # Create a mapping of document content to documents and scores
        doc_scores = {}
        
        # Normalize vector scores (assuming they're similarity scores between 0 and 1)
        for i, doc in enumerate(vector_results):
            content = doc.page_content
            # Assign decreasing scores based on ranking
            vector_score = 1.0 - (i / len(vector_results)) if vector_results else 0.0
            doc_scores[content] = {
                'doc': doc,
                'vector_score': vector_score,
                'bm25_score': 0.0
            }
        
        # Add BM25 scores
        if bm25_results:
            max_bm25_score = max(score for _, score in bm25_results) if bm25_results else 1.0
            max_bm25_score = max(max_bm25_score, 1.0)  # Avoid division by zero
            
            for doc, bm25_score in bm25_results:
                content = doc.page_content
                normalized_bm25_score = bm25_score / max_bm25_score
                
                if content in doc_scores:
                    doc_scores[content]['bm25_score'] = normalized_bm25_score
                else:
                    # Document found only in BM25 results
                    if normalized_bm25_score >= self.min_bm25_score:
                        doc_scores[content] = {
                            'doc': doc,
                            'vector_score': 0.0,
                            'bm25_score': normalized_bm25_score
                        }
        
        # Calculate combined scores and sort
        scored_docs = []
        for content, scores in doc_scores.items():
            combined_score = (
                self.vector_weight * scores['vector_score'] + 
                self.bm25_weight * scores['bm25_score']
            )
            scored_docs.append((scores['doc'], combined_score))
        
        # Sort by combined score and return top-k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"Reranked {len(scored_docs)} documents")
        return [doc for doc, score in scored_docs[:k]]
    
    def update_weights(self, bm25_weight: float, vector_weight: float):
        """Update the weights for BM25 and vector search"""
        total_weight = bm25_weight + vector_weight
        if total_weight > 0:
            self.bm25_weight = bm25_weight / total_weight
            self.vector_weight = vector_weight / total_weight
            logger.info(f"Updated weights - BM25: {self.bm25_weight:.2f}, Vector: {self.vector_weight:.2f}")
    
    def get_search_explanation(self, query: str, k: int = 3) -> Dict[str, Any]:
        """
        Get detailed explanation of search results for debugging
        """
        explanation = {
            "query": query,
            "vector_results": [],
            "bm25_results": [],
            "hybrid_results": [],
            "weights": {
                "bm25": self.bm25_weight,
                "vector": self.vector_weight
            }
        }
        
        try:
            # Get vector results
            if self.vector_store:
                vector_docs = self.vector_store.similarity_search(query, k=k)
                explanation["vector_results"] = [
                    {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in vector_docs
                ]
            
            # Get BM25 results
            bm25_results = self.bm25_retriever.search(query, k=k)
            explanation["bm25_results"] = [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                }
                for doc, score in bm25_results
            ]
            
            # Get hybrid results
            hybrid_docs = self.search(query, k=k)
            explanation["hybrid_results"] = [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in hybrid_docs
            ]
            
        except Exception as e:
            explanation["error"] = str(e)
        
        return explanation


def get_hybrid_retriever(vector_store=None, 
                        bm25_weight: float = 0.3, 
                        vector_weight: float = 0.7) -> HybridRetriever:
    """
    Get a configured hybrid retriever instance
    
    Args:
        vector_store: Vector store instance
        bm25_weight: Weight for BM25 scores
        vector_weight: Weight for vector similarity scores
    
    Returns:
        Configured HybridRetriever instance
    """
    return HybridRetriever(
        vector_store=vector_store,
        bm25_weight=bm25_weight,
        vector_weight=vector_weight
    )


if __name__ == "__main__":
    # Test the hybrid retriever
    from langchain.schema import Document
    
    # Sample documents
    docs = [
        Document(page_content="Machine learning is a subset of artificial intelligence.", metadata={"source": "doc1"}),
        Document(page_content="Python is a programming language used for data science.", metadata={"source": "doc2"}),
        Document(page_content="Natural language processing helps computers understand human language.", metadata={"source": "doc3"}),
    ]
    
    # Create and test hybrid retriever
    retriever = get_hybrid_retriever()
    retriever.fit(docs)
    
    # Test search
    results = retriever.search("machine learning AI", k=2)
    print(f"Found {len(results)} results")
    for doc in results:
        print(f"- {doc.page_content}")