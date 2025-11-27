#!/usr/bin/env python3
"""
Response Caching System for RAG
Implements intelligent caching for common queries to reduce latency
Based on production RAG optimization lessons
"""

import os
import json
import hashlib
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from threading import Lock
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cached query response entry"""
    query: str
    query_hash: str
    results: List[Dict[str, Any]]  # Serializable document data
    timestamp: datetime
    hit_count: int = 1
    avg_relevance_score: float = 0.0
    search_metadata: Optional[Dict[str, Any]] = None
    ttl_hours: int = 24

    def is_expired(self, ttl_hours: Optional[int] = None) -> bool:
        """Check if cache entry is expired"""
        effective_ttl = ttl_hours or self.ttl_hours
        expiry_time = self.timestamp + timedelta(hours=effective_ttl)
        return datetime.now() > expiry_time

    def update_hit(self, relevance_score: float = 0.0):
        """Update hit count and relevance tracking"""
        self.hit_count += 1
        if relevance_score > 0:
            # Update running average of relevance scores
            total_score = self.avg_relevance_score * (self.hit_count - 1) + relevance_score
            self.avg_relevance_score = total_score / self.hit_count

class ResponseCache:
    """
    Intelligent response caching system for RAG queries
    Provides fast responses for common queries and tracks usage patterns
    """
    
    def __init__(self, 
                 cache_dir: str = None,
                 max_cache_size: int = 1000,
                 default_ttl_hours: int = 24,
                 similarity_threshold: float = 0.85,
                 enable_persistence: bool = True):
        """
        Initialize response cache
        
        Args:
            cache_dir: Directory to store persistent cache
            max_cache_size: Maximum number of cached entries
            default_ttl_hours: Default time-to-live in hours
            similarity_threshold: Threshold for query similarity matching
            enable_persistence: Whether to persist cache to disk
        """
        self.max_cache_size = max_cache_size
        self.default_ttl_hours = default_ttl_hours
        self.similarity_threshold = similarity_threshold
        self.enable_persistence = enable_persistence
        
        # In-memory cache
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = Lock()
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "response_cache.pkl"
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        # Cache statistics
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_size": 0,
            "avg_response_time_cached": 0.0,
            "avg_response_time_uncached": 0.0,
            "top_queries": {},
            "last_cleanup": None
        }
        
        # Load existing cache
        if enable_persistence:
            self._load_cache()
            self._load_stats()

    def get(self, query: str, k: int = 3) -> Optional[Tuple[List[Document], Dict[str, Any]]]:
        """
        Get cached response for query
        
        Args:
            query: Search query
            k: Number of results requested
            
        Returns:
            Tuple of (documents, metadata) if cached, None otherwise
        """
        start_time = time.time()
        
        with self.cache_lock:
            # Generate query hash
            query_hash = self._generate_query_hash(query, k)
            
            # Check exact match first
            if query_hash in self.cache:
                entry = self.cache[query_hash]
                
                if not entry.is_expired():
                    # Update hit statistics
                    entry.update_hit()
                    self.stats["cache_hits"] += 1
                    
                    # Convert cached data back to documents
                    documents = self._deserialize_documents(entry.results)
                    
                    # Update response time stats
                    response_time = time.time() - start_time
                    self._update_response_time_stats(response_time, cached=True)
                    
                    logger.debug(f"Cache HIT for query: '{query[:50]}...' (hits: {entry.hit_count})")
                    
                    metadata = {
                        "cached": True,
                        "cache_hit_count": entry.hit_count,
                        "cache_timestamp": entry.timestamp.isoformat(),
                        "avg_relevance": entry.avg_relevance_score
                    }
                    
                    return documents, metadata
                else:
                    # Remove expired entry
                    del self.cache[query_hash]
                    logger.debug(f"Removed expired cache entry for query: '{query[:50]}...'")
            
            # Check for similar queries
            similar_entry = self._find_similar_query(query, k)
            if similar_entry:
                # Update hit statistics for similar query
                similar_entry.update_hit()
                self.stats["cache_hits"] += 1
                
                documents = self._deserialize_documents(similar_entry.results)
                
                response_time = time.time() - start_time
                self._update_response_time_stats(response_time, cached=True)
                
                logger.debug(f"Cache HIT (similar) for query: '{query[:50]}...'")
                
                metadata = {
                    "cached": True,
                    "similar_query": True,
                    "original_query": similar_entry.query,
                    "cache_hit_count": similar_entry.hit_count,
                    "cache_timestamp": similar_entry.timestamp.isoformat()
                }
                
                return documents, metadata
            
            # Cache miss
            self.stats["cache_misses"] += 1
            self.stats["total_queries"] += 1
            
            logger.debug(f"Cache MISS for query: '{query[:50]}...'")
            return None

    def put(self, query: str, documents: List[Document], k: int = 3, 
            search_metadata: Optional[Dict[str, Any]] = None,
            relevance_score: float = 0.0,
            ttl_hours: Optional[int] = None):
        """
        Cache query response
        
        Args:
            query: Search query
            documents: Retrieved documents
            k: Number of results requested
            search_metadata: Additional search metadata
            relevance_score: Relevance score for this response
            ttl_hours: Custom TTL for this entry
        """
        with self.cache_lock:
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_cache_size:
                self._evict_entries()
            
            # Generate query hash
            query_hash = self._generate_query_hash(query, k)
            
            # Serialize documents
            serialized_docs = self._serialize_documents(documents)
            
            # Create cache entry
            entry = CacheEntry(
                query=query,
                query_hash=query_hash,
                results=serialized_docs,
                timestamp=datetime.now(),
                hit_count=1,
                avg_relevance_score=relevance_score,
                search_metadata=search_metadata,
                ttl_hours=ttl_hours or self.default_ttl_hours
            )
            
            # Store in cache
            self.cache[query_hash] = entry
            
            # Update statistics
            self.stats["cache_size"] = len(self.cache)
            self._update_query_stats(query)
            
            logger.debug(f"Cached response for query: '{query[:50]}...' ({len(documents)} docs)")
            
            # Persist cache if enabled
            if self.enable_persistence:
                self._save_cache()

    def invalidate(self, query: str = None, pattern: str = None):
        """
        Invalidate cache entries
        
        Args:
            query: Specific query to invalidate
            pattern: Pattern to match for invalidation
        """
        with self.cache_lock:
            if query:
                # Invalidate specific query
                query_hashes_to_remove = []
                for hash_key, entry in self.cache.items():
                    if entry.query == query:
                        query_hashes_to_remove.append(hash_key)
                
                for hash_key in query_hashes_to_remove:
                    del self.cache[hash_key]
                    logger.debug(f"Invalidated cache for query: '{query[:50]}...'")
            
            elif pattern:
                # Invalidate by pattern
                query_hashes_to_remove = []
                for hash_key, entry in self.cache.items():
                    if pattern.lower() in entry.query.lower():
                        query_hashes_to_remove.append(hash_key)
                
                for hash_key in query_hashes_to_remove:
                    del self.cache[hash_key]
                
                logger.info(f"Invalidated {len(query_hashes_to_remove)} cache entries matching pattern: '{pattern}'")
            
            self.stats["cache_size"] = len(self.cache)

    def cleanup_expired(self):
        """Remove expired cache entries"""
        with self.cache_lock:
            expired_hashes = []
            
            for hash_key, entry in self.cache.items():
                if entry.is_expired():
                    expired_hashes.append(hash_key)
            
            for hash_key in expired_hashes:
                del self.cache[hash_key]
            
            self.stats["cache_size"] = len(self.cache)
            self.stats["last_cleanup"] = datetime.now().isoformat()
            
            if expired_hashes:
                logger.info(f"Cleaned up {len(expired_hashes)} expired cache entries")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.cache_lock:
            hit_rate = 0.0
            if self.stats["total_queries"] > 0:
                hit_rate = self.stats["cache_hits"] / self.stats["total_queries"]
            
            # Calculate cache efficiency metrics
            avg_hits_per_entry = 0.0
            if self.cache:
                total_hits = sum(entry.hit_count for entry in self.cache.values())
                avg_hits_per_entry = total_hits / len(self.cache)
            
            return {
                **self.stats,
                "hit_rate": round(hit_rate, 3),
                "miss_rate": round(1 - hit_rate, 3),
                "avg_hits_per_entry": round(avg_hits_per_entry, 2),
                "current_cache_size": len(self.cache),
                "cache_utilization": round(len(self.cache) / self.max_cache_size, 3)
            }

    def get_popular_queries(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get most popular cached queries"""
        with self.cache_lock:
            sorted_entries = sorted(
                self.cache.values(), 
                key=lambda x: x.hit_count, 
                reverse=True
            )
            
            popular_queries = []
            for entry in sorted_entries[:top_k]:
                popular_queries.append({
                    "query": entry.query,
                    "hit_count": entry.hit_count,
                    "avg_relevance": round(entry.avg_relevance_score, 3),
                    "cached_since": entry.timestamp.isoformat(),
                    "last_accessed": "recent"  # Could track this separately
                })
            
            return popular_queries

    def _generate_query_hash(self, query: str, k: int) -> str:
        """Generate hash for query + parameters"""
        # Normalize query for consistent hashing
        normalized_query = query.lower().strip()
        query_data = f"{normalized_query}|k={k}"
        return hashlib.md5(query_data.encode()).hexdigest()

    def _serialize_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Convert documents to serializable format"""
        serialized = []
        for doc in documents:
            serialized.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        return serialized

    def _deserialize_documents(self, serialized_docs: List[Dict[str, Any]]) -> List[Document]:
        """Convert serialized data back to documents"""
        documents = []
        for doc_data in serialized_docs:
            doc = Document(
                page_content=doc_data["page_content"],
                metadata=doc_data["metadata"]
            )
            documents.append(doc)
        return documents

    def _find_similar_query(self, query: str, k: int) -> Optional[CacheEntry]:
        """Find similar cached query using fuzzy matching"""
        if not self.cache:
            return None
        
        query_words = set(query.lower().split())
        best_similarity = 0.0
        best_entry = None
        
        for entry in self.cache.values():
            if entry.is_expired():
                continue
            
            entry_words = set(entry.query.lower().split())
            
            # Calculate Jaccard similarity
            intersection = query_words.intersection(entry_words)
            union = query_words.union(entry_words)
            
            if union:
                similarity = len(intersection) / len(union)
                
                if similarity >= self.similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_entry = entry
        
        return best_entry

    def _evict_entries(self):
        """Evict least useful cache entries"""
        # Calculate eviction scores (lower is worse)
        entries_with_scores = []
        
        for hash_key, entry in self.cache.items():
            # Score based on recency, hit count, and relevance
            age_penalty = (datetime.now() - entry.timestamp).days * 0.1
            score = (entry.hit_count * 2 + entry.avg_relevance_score) - age_penalty
            entries_with_scores.append((hash_key, entry, score))
        
        # Sort by score and remove bottom 20%
        entries_with_scores.sort(key=lambda x: x[2])
        evict_count = max(1, len(entries_with_scores) // 5)
        
        for i in range(evict_count):
            hash_key, entry, score = entries_with_scores[i]
            del self.cache[hash_key]
            logger.debug(f"Evicted cache entry: '{entry.query[:30]}...' (score: {score:.2f})")

    def _update_response_time_stats(self, response_time: float, cached: bool):
        """Update response time statistics"""
        if cached:
            current_avg = self.stats["avg_response_time_cached"]
            hits = self.stats["cache_hits"]
            self.stats["avg_response_time_cached"] = ((current_avg * (hits - 1)) + response_time) / hits
        else:
            current_avg = self.stats["avg_response_time_uncached"]
            misses = self.stats["cache_misses"]
            self.stats["avg_response_time_uncached"] = ((current_avg * (misses - 1)) + response_time) / misses

    def _update_query_stats(self, query: str):
        """Update query frequency statistics"""
        if query in self.stats["top_queries"]:
            self.stats["top_queries"][query] += 1
        else:
            self.stats["top_queries"][query] = 1
        
        # Keep only top 50 queries
        if len(self.stats["top_queries"]) > 50:
            sorted_queries = sorted(
                self.stats["top_queries"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            self.stats["top_queries"] = dict(sorted_queries[:50])

    def _save_cache(self):
        """Persist cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _load_cache(self):
        """Load cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                logger.info(f"Loaded {len(self.cache)} cache entries from disk")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.cache = {}

    def _load_stats(self):
        """Load statistics from disk"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    loaded_stats = json.load(f)
                    self.stats.update(loaded_stats)
                logger.info("Loaded cache statistics from disk")
        except Exception as e:
            logger.error(f"Failed to load cache stats: {e}")

# Global cache instance
_cache_instance = None
_cache_lock = Lock()

def get_response_cache(cache_dir: str = None,
                      max_cache_size: int = 1000,
                      default_ttl_hours: int = 24,
                      similarity_threshold: float = 0.85) -> ResponseCache:
    """
    Get global response cache instance (singleton pattern)
    
    Args:
        cache_dir: Cache directory path
        max_cache_size: Maximum cache size
        default_ttl_hours: Default TTL in hours
        similarity_threshold: Query similarity threshold
    
    Returns:
        ResponseCache instance
    """
    global _cache_instance
    
    with _cache_lock:
        if _cache_instance is None:
            _cache_instance = ResponseCache(
                cache_dir=cache_dir,
                max_cache_size=max_cache_size,
                default_ttl_hours=default_ttl_hours,
                similarity_threshold=similarity_threshold
            )
        
        return _cache_instance

if __name__ == "__main__":
    # Test the response cache
    from langchain.schema import Document
    
    cache = get_response_cache()
    
    # Test caching
    query = "machine learning algorithms"
    docs = [
        Document(page_content="ML is great", metadata={"source": "test1"}),
        Document(page_content="Deep learning rocks", metadata={"source": "test2"})
    ]
    
    # Cache response
    cache.put(query, docs, relevance_score=0.85)
    
    # Try to retrieve
    cached_result = cache.get(query)
    if cached_result:
        cached_docs, metadata = cached_result
        print(f"Retrieved {len(cached_docs)} cached documents")
        print(f"Cache metadata: {metadata}")
    
    # Print stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")