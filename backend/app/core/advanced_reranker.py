#!/usr/bin/env python3
"""
Advanced Re-ranking System for RAG
Implements sophisticated re-ranking strategies for improved retrieval precision
Based on production RAG optimization lessons
"""

import os
import logging
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from langchain_core.documents import Document

# Optional dependencies for advanced re-ranking
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReRankingStrategy(Enum):
    """Different re-ranking strategies"""
    RECIPROCAL_RANK_FUSION = "reciprocal_rank_fusion"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    HYBRID_WEIGHTED = "hybrid_weighted"
    DIVERSITY_BASED = "diversity_based"
    CONTEXTUAL_RELEVANCE = "contextual_relevance"

@dataclass
class ScoredDocument:
    """Document with multiple relevance scores"""
    document: Document
    bm25_score: float = 0.0
    vector_score: float = 0.0
    semantic_score: float = 0.0
    diversity_score: float = 0.0
    final_score: float = 0.0
    rank_position: int = 0
    metadata: Optional[Dict[str, Any]] = None

class AdvancedReRanker:
    """
    Advanced re-ranking system for improving RAG retrieval precision
    Implements multiple re-ranking strategies to filter irrelevant results
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 enable_semantic_rerank: bool = True,
                 diversity_threshold: float = 0.7,
                 max_candidates: int = 50):
        """
        Initialize advanced re-ranker
        
        Args:
            model_name: Sentence transformer model for semantic re-ranking
            enable_semantic_rerank: Whether to use semantic similarity re-ranking
            diversity_threshold: Minimum diversity score for document inclusion
            max_candidates: Maximum number of candidates to consider
        """
        self.model_name = model_name
        self.enable_semantic_rerank = enable_semantic_rerank
        self.diversity_threshold = diversity_threshold
        self.max_candidates = max_candidates
        
        # Initialize semantic similarity model
        self.semantic_model = None
        if enable_semantic_rerank and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer(model_name)
                logger.info(f"Loaded semantic model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load semantic model: {e}")
                self.enable_semantic_rerank = False
        else:
            if enable_semantic_rerank:
                logger.warning("Sentence-transformers not available. Semantic re-ranking disabled.")
            self.enable_semantic_rerank = False

    def rerank_documents(self, 
                        query: str,
                        bm25_results: List[Tuple[Document, float]],
                        vector_results: List[Document],
                        strategy: ReRankingStrategy = ReRankingStrategy.HYBRID_WEIGHTED,
                        k: int = 10) -> List[Document]:
        """
        Re-rank documents using specified strategy
        
        Args:
            query: Original search query
            bm25_results: BM25 results with scores
            vector_results: Vector similarity results
            strategy: Re-ranking strategy to use
            k: Number of top documents to return
            
        Returns:
            Re-ranked list of documents
        """
        logger.debug(f"Re-ranking {len(bm25_results)} BM25 + {len(vector_results)} vector results")
        
        # Convert to scored documents
        scored_docs = self._create_scored_documents(query, bm25_results, vector_results)
        
        # Apply re-ranking strategy
        if strategy == ReRankingStrategy.RECIPROCAL_RANK_FUSION:
            reranked_docs = self._reciprocal_rank_fusion(scored_docs)
        elif strategy == ReRankingStrategy.SEMANTIC_SIMILARITY:
            reranked_docs = self._semantic_similarity_rerank(query, scored_docs)
        elif strategy == ReRankingStrategy.HYBRID_WEIGHTED:
            reranked_docs = self._hybrid_weighted_rerank(query, scored_docs)
        elif strategy == ReRankingStrategy.DIVERSITY_BASED:
            reranked_docs = self._diversity_based_rerank(query, scored_docs)
        elif strategy == ReRankingStrategy.CONTEXTUAL_RELEVANCE:
            reranked_docs = self._contextual_relevance_rerank(query, scored_docs)
        else:
            reranked_docs = scored_docs
        
        # Apply diversity filtering
        filtered_docs = self._apply_diversity_filter(reranked_docs)
        
        # Return top-k documents
        result_docs = [doc.document for doc in filtered_docs[:k]]
        
        logger.debug(f"Re-ranking complete. Returning {len(result_docs)} documents")
        return result_docs

    def _create_scored_documents(self, 
                               query: str,
                               bm25_results: List[Tuple[Document, float]],
                               vector_results: List[Document]) -> List[ScoredDocument]:
        """Create scored document objects from results"""
        scored_docs = []
        seen_content = set()
        
        # Process BM25 results
        max_bm25_score = max((score for _, score in bm25_results), default=1.0)
        
        for i, (doc, score) in enumerate(bm25_results):
            if doc.page_content in seen_content:
                continue
            
            scored_doc = ScoredDocument(
                document=doc,
                bm25_score=score / max_bm25_score,  # Normalize
                rank_position=i + 1
            )
            scored_docs.append(scored_doc)
            seen_content.add(doc.page_content)
        
        # Process vector results
        for i, doc in enumerate(vector_results):
            if doc.page_content in seen_content:
                # Update existing document with vector score
                for scored_doc in scored_docs:
                    if scored_doc.document.page_content == doc.page_content:
                        scored_doc.vector_score = 1.0 - (i / len(vector_results))  # Rank-based score
                        break
            else:
                # Add new document
                scored_doc = ScoredDocument(
                    document=doc,
                    vector_score=1.0 - (i / len(vector_results)),  # Rank-based score
                    rank_position=len(scored_docs) + 1
                )
                scored_docs.append(scored_doc)
                seen_content.add(doc.page_content)
        
        return scored_docs

    def _reciprocal_rank_fusion(self, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """
        Apply Reciprocal Rank Fusion (RRF) re-ranking
        Combines rankings from multiple systems
        """
        k = 60  # RRF constant
        
        # Create ranking maps
        bm25_ranking = {doc.document.page_content: i for i, doc in 
                       enumerate(sorted(scored_docs, key=lambda x: x.bm25_score, reverse=True))}
        vector_ranking = {doc.document.page_content: i for i, doc in 
                         enumerate(sorted(scored_docs, key=lambda x: x.vector_score, reverse=True))}
        
        # Calculate RRF scores
        for doc in scored_docs:
            content = doc.document.page_content
            bm25_rank = bm25_ranking.get(content, len(scored_docs))
            vector_rank = vector_ranking.get(content, len(scored_docs))
            
            rrf_score = (1 / (k + bm25_rank + 1)) + (1 / (k + vector_rank + 1))
            doc.final_score = rrf_score
        
        # Sort by RRF score
        return sorted(scored_docs, key=lambda x: x.final_score, reverse=True)

    def _semantic_similarity_rerank(self, query: str, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """
        Re-rank using semantic similarity to query
        """
        if not self.enable_semantic_rerank or not self.semantic_model:
            logger.warning("Semantic re-ranking not available, using original ranking")
            return scored_docs
        
        try:
            # Encode query
            query_embedding = self.semantic_model.encode([query], convert_to_tensor=True)
            
            # Encode documents
            doc_texts = [doc.document.page_content for doc in scored_docs]
            doc_embeddings = self.semantic_model.encode(doc_texts, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]
            
            # Update semantic scores
            for i, doc in enumerate(scored_docs):
                doc.semantic_score = float(similarities[i])
                # Combine with existing scores
                doc.final_score = (0.4 * doc.bm25_score + 
                                 0.3 * doc.vector_score + 
                                 0.3 * doc.semantic_score)
            
            return sorted(scored_docs, key=lambda x: x.final_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Semantic re-ranking failed: {e}")
            return scored_docs

    def _hybrid_weighted_rerank(self, query: str, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """
        Hybrid weighted re-ranking combining multiple signals
        """
        # Apply semantic re-ranking first if available
        if self.enable_semantic_rerank:
            scored_docs = self._semantic_similarity_rerank(query, scored_docs)
        
        # Calculate query-specific weights
        query_length = len(query.split())
        is_specific_query = query_length > 3
        
        # Adjust weights based on query characteristics
        if is_specific_query:
            # For specific queries, favor BM25 (keyword matching)
            bm25_weight = 0.5
            vector_weight = 0.3
            semantic_weight = 0.2
        else:
            # For general queries, favor vector similarity
            bm25_weight = 0.3
            vector_weight = 0.5
            semantic_weight = 0.2
        
        # Calculate final weighted scores
        for doc in scored_docs:
            weighted_score = (
                bm25_weight * doc.bm25_score +
                vector_weight * doc.vector_score +
                semantic_weight * doc.semantic_score
            )
            
            # Apply document quality boost
            quality_boost = self._calculate_quality_boost(doc.document)
            doc.final_score = weighted_score * quality_boost
        
        return sorted(scored_docs, key=lambda x: x.final_score, reverse=True)

    def _diversity_based_rerank(self, query: str, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """
        Diversity-based re-ranking to avoid redundant results
        """
        if not scored_docs:
            return scored_docs
        
        # Start with hybrid weighted ranking
        ranked_docs = self._hybrid_weighted_rerank(query, scored_docs)
        
        # Apply Maximal Marginal Relevance (MMR) for diversity
        selected_docs = []
        remaining_docs = ranked_docs.copy()
        
        # Select first document (highest scoring)
        if remaining_docs:
            first_doc = remaining_docs.pop(0)
            selected_docs.append(first_doc)
        
        # Select remaining documents considering diversity
        lambda_param = 0.7  # Balance between relevance and diversity
        
        while remaining_docs and len(selected_docs) < self.max_candidates:
            max_mmr_score = -1
            best_doc_idx = -1
            
            for i, candidate in enumerate(remaining_docs):
                # Calculate relevance score
                relevance = candidate.final_score
                
                # Calculate maximum similarity to already selected documents
                max_similarity = 0
                for selected in selected_docs:
                    similarity = self._calculate_text_similarity(
                        candidate.document.page_content,
                        selected.document.page_content
                    )
                    max_similarity = max(max_similarity, similarity)
                
                # Calculate MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                
                if mmr_score > max_mmr_score:
                    max_mmr_score = mmr_score
                    best_doc_idx = i
            
            if best_doc_idx >= 0:
                selected_doc = remaining_docs.pop(best_doc_idx)
                selected_doc.diversity_score = max_mmr_score
                selected_docs.append(selected_doc)
        
        return selected_docs

    def _contextual_relevance_rerank(self, query: str, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """
        Re-rank based on contextual relevance including metadata
        """
        # Start with hybrid ranking
        ranked_docs = self._hybrid_weighted_rerank(query, scored_docs)
        
        # Apply contextual boosts
        for doc in ranked_docs:
            context_boost = 1.0
            metadata = doc.document.metadata
            
            # Boost based on document type and structure
            if metadata.get("semantic_chunking"):
                context_boost *= 1.1  # Favor semantically chunked content
            
            if metadata.get("chunk_type") == "header":
                context_boost *= 1.2  # Headers are often relevant
            
            if metadata.get("hierarchy_level", 0) <= 2:
                context_boost *= 1.1  # Top-level sections
            
            # Boost based on section titles matching query
            section_title = metadata.get("section_title", "")
            if section_title and any(word in section_title.lower() for word in query.lower().split()):
                context_boost *= 1.3
            
            # Apply context boost
            doc.final_score *= context_boost
        
        return sorted(ranked_docs, key=lambda x: x.final_score, reverse=True)

    def _calculate_quality_boost(self, document: Document) -> float:
        """Calculate quality boost for a document"""
        boost = 1.0
        content = document.page_content
        metadata = document.metadata
        
        # Length-based quality
        content_length = len(content)
        if 200 <= content_length <= 2000:
            boost *= 1.1  # Optimal length range
        elif content_length < 50:
            boost *= 0.8  # Too short
        elif content_length > 3000:
            boost *= 0.9  # Too long
        
        # Structure-based quality
        if metadata.get("semantic_chunking"):
            boost *= 1.05
        
        # Content quality indicators
        sentence_count = len([s for s in content.split('.') if s.strip()])
        avg_sentence_length = content_length / max(sentence_count, 1)
        
        if 10 <= avg_sentence_length <= 30:
            boost *= 1.05  # Good sentence length
        
        return boost

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if self.enable_semantic_rerank and self.semantic_model:
            try:
                embeddings = self.semantic_model.encode([text1, text2], convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
                return float(similarity)
            except Exception:
                pass
        
        # Fallback to simple token overlap
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)

    def _apply_diversity_filter(self, scored_docs: List[ScoredDocument]) -> List[ScoredDocument]:
        """Apply final diversity filtering"""
        if not scored_docs:
            return scored_docs
        
        filtered_docs = []
        seen_content_hashes = set()
        
        for doc in scored_docs:
            # Create content hash for similarity detection
            content_hash = hash(doc.document.page_content[:200])  # First 200 chars
            
            # Check if too similar to already selected docs
            is_diverse = True
            for existing_hash in seen_content_hashes:
                # Simple hash-based diversity check
                if abs(content_hash - existing_hash) < 1000:  # Threshold for similarity
                    is_diverse = False
                    break
            
            if is_diverse or len(filtered_docs) < 3:  # Always include top 3
                filtered_docs.append(doc)
                seen_content_hashes.add(content_hash)
            
            # Stop if we have enough diverse results
            if len(filtered_docs) >= self.max_candidates:
                break
        
        return filtered_docs

    def explain_ranking(self, scored_docs: List[ScoredDocument], top_k: int = 5) -> Dict[str, Any]:
        """
        Provide explanation for ranking decisions
        """
        if not scored_docs:
            return {"error": "No documents to explain"}
        
        explanations = []
        for i, doc in enumerate(scored_docs[:top_k]):
            explanation = {
                "rank": i + 1,
                "final_score": round(doc.final_score, 4),
                "bm25_score": round(doc.bm25_score, 4),
                "vector_score": round(doc.vector_score, 4),
                "semantic_score": round(doc.semantic_score, 4),
                "diversity_score": round(doc.diversity_score, 4),
                "content_preview": doc.document.page_content[:150] + "...",
                "metadata": doc.document.metadata
            }
            explanations.append(explanation)
        
        return {
            "total_candidates": len(scored_docs),
            "top_results": explanations,
            "ranking_strategy": "advanced_hybrid_reranking"
        }

def get_advanced_reranker(model_name: str = "all-MiniLM-L6-v2",
                         enable_semantic_rerank: bool = True,
                         diversity_threshold: float = 0.7,
                         max_candidates: int = 50) -> AdvancedReRanker:
    """
    Get a configured advanced re-ranker instance
    
    Args:
        model_name: Sentence transformer model name
        enable_semantic_rerank: Whether to enable semantic re-ranking
        diversity_threshold: Minimum diversity threshold
        max_candidates: Maximum candidates to consider
    
    Returns:
        Configured AdvancedReRanker instance
    """
    return AdvancedReRanker(
        model_name=model_name,
        enable_semantic_rerank=enable_semantic_rerank,
        diversity_threshold=diversity_threshold,
        max_candidates=max_candidates
    )

if __name__ == "__main__":
    # Test the re-ranker
    from langchain.schema import Document
    
    # Sample documents and results
    docs = [
        Document(page_content="Machine learning is a subset of AI", metadata={"source": "doc1"}),
        Document(page_content="Deep learning uses neural networks", metadata={"source": "doc2"}),
        Document(page_content="AI applications in healthcare", metadata={"source": "doc3"})
    ]
    
    bm25_results = [(docs[0], 0.8), (docs[1], 0.6), (docs[2], 0.4)]
    vector_results = [docs[2], docs[0], docs[1]]
    
    reranker = get_advanced_reranker()
    reranked = reranker.rerank_documents(
        query="machine learning artificial intelligence",
        bm25_results=bm25_results,
        vector_results=vector_results,
        strategy=ReRankingStrategy.HYBRID_WEIGHTED
    )
    
    print(f"Re-ranked {len(reranked)} documents")
    for i, doc in enumerate(reranked):
        print(f"{i+1}. {doc.page_content[:50]}...")