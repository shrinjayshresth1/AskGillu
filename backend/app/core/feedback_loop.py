#!/usr/bin/env python3
"""
Feedback Loop System for RAG
Tracks missed retrievals and user feedback to continuously improve RAG performance
Based on production RAG optimization lessons
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import sqlite3
import threading
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """Types of feedback"""
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"
    PARTIALLY_RELEVANT = "partially_relevant"
    MISSED_CONTENT = "missed_content"
    INCORRECT_ANSWER = "incorrect_answer"
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"

class QueryCategory(Enum):
    """Categories of queries for analysis"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    EXPLANATORY = "explanatory"
    UNKNOWN = "unknown"

@dataclass
class FeedbackEntry:
    """Individual feedback entry"""
    id: str
    query: str
    query_category: QueryCategory
    retrieved_docs: List[Dict[str, Any]]
    user_feedback: FeedbackType
    relevance_score: float
    response_quality: float
    missing_info: Optional[str] = None
    suggested_improvement: Optional[str] = None
    timestamp: datetime = None
    user_session: Optional[str] = None
    response_time: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class QueryAnalysis:
    """Analysis of query patterns and performance"""
    query: str
    total_occurrences: int
    avg_relevance_score: float
    feedback_distribution: Dict[str, int]
    common_issues: List[str]
    suggested_improvements: List[str]
    last_seen: datetime

class FeedbackLoop:
    """
    Feedback loop system for continuous RAG improvement
    Tracks user feedback, analyzes patterns, and suggests optimizations
    """
    
    def __init__(self, 
                 db_path: str = None,
                 enable_analytics: bool = True,
                 retention_days: int = 90):
        """
        Initialize feedback loop system
        
        Args:
            db_path: Path to SQLite database for feedback storage
            enable_analytics: Whether to enable analytics processing
            retention_days: Days to retain feedback data
        """
        self.enable_analytics = enable_analytics
        self.retention_days = retention_days
        
        # Setup database
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "feedback.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self.db_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_expiry = None

    def record_feedback(self, 
                       query: str,
                       retrieved_docs: List[Document],
                       feedback_type: FeedbackType,
                       relevance_score: float = 0.0,
                       response_quality: float = 0.0,
                       missing_info: str = None,
                       suggested_improvement: str = None,
                       user_session: str = None,
                       response_time: float = None) -> str:
        """
        Record user feedback for a query
        
        Args:
            query: Original search query
            retrieved_docs: Documents that were retrieved
            feedback_type: Type of feedback provided
            relevance_score: Relevance score (0-1)
            response_quality: Overall response quality (0-1)
            missing_info: Information that was missing
            suggested_improvement: User's suggestion for improvement
            user_session: User session identifier
            response_time: Response time in seconds
            
        Returns:
            Feedback entry ID
        """
        # Generate unique ID
        feedback_id = f"fb_{int(datetime.now().timestamp() * 1000)}"
        
        # Categorize query
        query_category = self._categorize_query(query)
        
        # Serialize documents
        serialized_docs = self._serialize_documents(retrieved_docs)
        
        # Create feedback entry
        feedback = FeedbackEntry(
            id=feedback_id,
            query=query,
            query_category=query_category,
            retrieved_docs=serialized_docs,
            user_feedback=feedback_type,
            relevance_score=relevance_score,
            response_quality=response_quality,
            missing_info=missing_info,
            suggested_improvement=suggested_improvement,
            user_session=user_session,
            response_time=response_time
        )
        
        # Store in database
        self._store_feedback(feedback)
        
        logger.info(f"Recorded {feedback_type.value} feedback for query: '{query[:50]}...'")
        
        # Trigger analytics update if enabled
        if self.enable_analytics:
            self._update_analytics_cache()
        
        return feedback_id

    def get_query_performance(self, query: str) -> Optional[QueryAnalysis]:
        """
        Get performance analysis for a specific query
        
        Args:
            query: Query to analyze
            
        Returns:
            QueryAnalysis object or None if no data
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                # Get feedback data for query
                cursor.execute("""
                    SELECT * FROM feedback 
                    WHERE LOWER(query) = LOWER(?) 
                    ORDER BY timestamp DESC
                """, (query,))
                
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Calculate statistics
                total_occurrences = len(rows)
                relevance_scores = [row['relevance_score'] for row in rows if row['relevance_score'] > 0]
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
                
                # Feedback distribution
                feedback_dist = {}
                common_issues = []
                suggestions = []
                
                for row in rows:
                    feedback_type = row['user_feedback']
                    feedback_dist[feedback_type] = feedback_dist.get(feedback_type, 0) + 1
                    
                    if row['missing_info']:
                        common_issues.append(row['missing_info'])
                    
                    if row['suggested_improvement']:
                        suggestions.append(row['suggested_improvement'])
                
                return QueryAnalysis(
                    query=query,
                    total_occurrences=total_occurrences,
                    avg_relevance_score=avg_relevance,
                    feedback_distribution=feedback_dist,
                    common_issues=common_issues[:5],  # Top 5 issues
                    suggested_improvements=suggestions[:5],  # Top 5 suggestions
                    last_seen=datetime.fromisoformat(rows[0]['timestamp'])
                )
                
            finally:
                conn.close()

    def get_problematic_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get queries with poor performance that need attention
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of problematic query analyses
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                # Find queries with low relevance or negative feedback
                cursor.execute("""
                    SELECT query, 
                           COUNT(*) as occurrences,
                           AVG(relevance_score) as avg_relevance,
                           AVG(response_quality) as avg_quality,
                           SUM(CASE WHEN user_feedback IN ('irrelevant', 'not_helpful', 'incorrect_answer') THEN 1 ELSE 0 END) as negative_feedback,
                           MAX(timestamp) as last_seen
                    FROM feedback 
                    WHERE timestamp > datetime('now', '-30 days')
                    GROUP BY LOWER(query)
                    HAVING occurrences >= 2 AND (avg_relevance < 0.5 OR negative_feedback > 0)
                    ORDER BY (negative_feedback * 2 + (1 - avg_relevance)) DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                
                problematic_queries = []
                for row in rows:
                    problematic_queries.append({
                        "query": row["query"],
                        "occurrences": row["occurrences"],
                        "avg_relevance_score": round(row["avg_relevance"], 3),
                        "avg_response_quality": round(row["avg_quality"], 3),
                        "negative_feedback_count": row["negative_feedback"],
                        "last_seen": row["last_seen"],
                        "priority_score": round((row["negative_feedback"] * 2 + (1 - row["avg_relevance"])), 3)
                    })
                
                return problematic_queries
                
            finally:
                conn.close()

    def get_missing_content_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze patterns in missing content to identify knowledge gaps
        
        Returns:
            List of missing content patterns
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT missing_info, COUNT(*) as frequency,
                           GROUP_CONCAT(DISTINCT query) as related_queries
                    FROM feedback 
                    WHERE missing_info IS NOT NULL 
                      AND missing_info != ''
                      AND timestamp > datetime('now', '-60 days')
                    GROUP BY LOWER(missing_info)
                    HAVING frequency >= 2
                    ORDER BY frequency DESC
                    LIMIT 15
                """)
                
                rows = cursor.fetchall()
                
                patterns = []
                for row in rows:
                    related_queries = row["related_queries"].split(",")[:5]  # Top 5 related queries
                    patterns.append({
                        "missing_content": row["missing_info"],
                        "frequency": row["frequency"],
                        "related_queries": related_queries,
                        "urgency": "high" if row["frequency"] >= 5 else "medium"
                    })
                
                return patterns
                
            finally:
                conn.close()

    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get summary of feedback over specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Feedback summary statistics
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                # Get overall statistics
                cursor.execute("""
                    SELECT COUNT(*) as total_feedback,
                           AVG(relevance_score) as avg_relevance,
                           AVG(response_quality) as avg_quality,
                           AVG(response_time) as avg_response_time
                    FROM feedback 
                    WHERE timestamp > datetime('now', '-{} days')
                """.format(days))
                
                stats = cursor.fetchone()
                
                # Get feedback type distribution
                cursor.execute("""
                    SELECT user_feedback, COUNT(*) as count
                    FROM feedback 
                    WHERE timestamp > datetime('now', '-{} days')
                    GROUP BY user_feedback
                    ORDER BY count DESC
                """.format(days))
                
                feedback_dist = dict(cursor.fetchall())
                
                # Get query category distribution
                cursor.execute("""
                    SELECT query_category, COUNT(*) as count
                    FROM feedback 
                    WHERE timestamp > datetime('now', '-{} days')
                    GROUP BY query_category
                    ORDER BY count DESC
                """.format(days))
                
                category_dist = dict(cursor.fetchall())
                
                # Calculate satisfaction rate
                positive_feedback = feedback_dist.get('relevant', 0) + feedback_dist.get('helpful', 0)
                total_feedback = stats['total_feedback']
                satisfaction_rate = positive_feedback / total_feedback if total_feedback > 0 else 0.0
                
                return {
                    "period_days": days,
                    "total_feedback_entries": total_feedback,
                    "avg_relevance_score": round(stats['avg_relevance'], 3) if stats['avg_relevance'] else 0.0,
                    "avg_response_quality": round(stats['avg_quality'], 3) if stats['avg_quality'] else 0.0,
                    "avg_response_time": round(stats['avg_response_time'], 3) if stats['avg_response_time'] else 0.0,
                    "satisfaction_rate": round(satisfaction_rate, 3),
                    "feedback_distribution": feedback_dist,
                    "query_category_distribution": category_dist
                }
                
            finally:
                conn.close()

    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for RAG system improvements
        
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Check for problematic queries
        problematic_queries = self.get_problematic_queries(10)
        if problematic_queries:
            recommendations.append({
                "type": "query_optimization",
                "priority": "high",
                "title": "Optimize Poorly Performing Queries",
                "description": f"Found {len(problematic_queries)} queries with low relevance scores",
                "action_items": [
                    "Review retrieval strategy for these queries",
                    "Consider adding more relevant content",
                    "Adjust search parameters or weights"
                ],
                "affected_queries": [q["query"] for q in problematic_queries[:5]]
            })
        
        # Check for missing content patterns
        missing_patterns = self.get_missing_content_patterns()
        if missing_patterns:
            high_priority_gaps = [p for p in missing_patterns if p["urgency"] == "high"]
            if high_priority_gaps:
                recommendations.append({
                    "type": "content_gaps",
                    "priority": "high",
                    "title": "Address Knowledge Gaps",
                    "description": f"Found {len(high_priority_gaps)} high-priority content gaps",
                    "action_items": [
                        "Add missing content to knowledge base",
                        "Update existing documents with missing information",
                        "Consider adding specialized sources"
                    ],
                    "missing_topics": [p["missing_content"] for p in high_priority_gaps[:5]]
                })
        
        # Check feedback trends
        summary = self.get_feedback_summary()
        if summary["satisfaction_rate"] < 0.7:
            recommendations.append({
                "type": "overall_performance",
                "priority": "medium",
                "title": "Improve Overall Satisfaction",
                "description": f"Current satisfaction rate is {summary['satisfaction_rate']:.1%}",
                "action_items": [
                    "Review retrieval and ranking algorithms",
                    "Analyze user feedback patterns",
                    "Consider re-training or parameter tuning"
                ],
                "current_metrics": summary
            })
        
        # Check response time issues
        if summary["avg_response_time"] > 3.0:  # Assuming 3 seconds is threshold
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "title": "Optimize Response Time",
                "description": f"Average response time is {summary['avg_response_time']:.2f} seconds",
                "action_items": [
                    "Implement or optimize response caching",
                    "Review vector database performance",
                    "Consider model optimization"
                ]
            })
        
        return recommendations

    def cleanup_old_data(self):
        """Remove old feedback data beyond retention period"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                
                cursor.execute("""
                    DELETE FROM feedback 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old feedback entries")
                
            finally:
                conn.close()

    def _init_database(self):
        """Initialize SQLite database for feedback storage"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    query_category TEXT,
                    retrieved_docs TEXT,
                    user_feedback TEXT,
                    relevance_score REAL,
                    response_quality REAL,
                    missing_info TEXT,
                    suggested_improvement TEXT,
                    timestamp TEXT,
                    user_session TEXT,
                    response_time REAL
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON feedback(query)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(user_feedback)")
            
            conn.commit()
            conn.close()

    def _store_feedback(self, feedback: FeedbackEntry):
        """Store feedback entry in database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback (
                    id, query, query_category, retrieved_docs, user_feedback,
                    relevance_score, response_quality, missing_info, 
                    suggested_improvement, timestamp, user_session, response_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.id,
                feedback.query,
                feedback.query_category.value,
                json.dumps(feedback.retrieved_docs),
                feedback.user_feedback.value,
                feedback.relevance_score,
                feedback.response_quality,
                feedback.missing_info,
                feedback.suggested_improvement,
                feedback.timestamp.isoformat(),
                feedback.user_session,
                feedback.response_time
            ))
            
            conn.commit()
            conn.close()

    def _categorize_query(self, query: str) -> QueryCategory:
        """Categorize query based on content analysis"""
        query_lower = query.lower()
        
        # Simple rule-based categorization
        if any(word in query_lower for word in ['what', 'define', 'meaning', 'is']):
            return QueryCategory.FACTUAL
        elif any(word in query_lower for word in ['how', 'steps', 'process', 'procedure']):
            return QueryCategory.PROCEDURAL
        elif any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus', 'better']):
            return QueryCategory.COMPARATIVE
        elif any(word in query_lower for word in ['why', 'explain', 'reason', 'because']):
            return QueryCategory.EXPLANATORY
        else:
            return QueryCategory.UNKNOWN

    def _serialize_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Convert documents to serializable format"""
        return [{
            "page_content": doc.page_content[:500],  # Truncate for storage
            "metadata": doc.metadata
        } for doc in documents]

    def _update_analytics_cache(self):
        """Update analytics cache (placeholder for more complex analytics)"""
        # This could trigger more sophisticated analytics processing
        pass

# Global feedback loop instance
_feedback_instance = None
_feedback_lock = threading.Lock()

def get_feedback_loop(db_path: str = None,
                     enable_analytics: bool = True,
                     retention_days: int = 90) -> FeedbackLoop:
    """
    Get global feedback loop instance (singleton pattern)
    
    Args:
        db_path: Database path
        enable_analytics: Enable analytics processing
        retention_days: Data retention period
    
    Returns:
        FeedbackLoop instance
    """
    global _feedback_instance
    
    with _feedback_lock:
        if _feedback_instance is None:
            _feedback_instance = FeedbackLoop(
                db_path=db_path,
                enable_analytics=enable_analytics,
                retention_days=retention_days
            )
        
        return _feedback_instance

if __name__ == "__main__":
    # Test the feedback loop
    from langchain.schema import Document
    
    feedback_loop = get_feedback_loop()
    
    # Record some test feedback
    docs = [
        Document(page_content="ML is great", metadata={"source": "test1"}),
        Document(page_content="Deep learning rocks", metadata={"source": "test2"})
    ]
    
    feedback_id = feedback_loop.record_feedback(
        query="machine learning basics",
        retrieved_docs=docs,
        feedback_type=FeedbackType.RELEVANT,
        relevance_score=0.8,
        response_quality=0.7
    )
    
    print(f"Recorded feedback: {feedback_id}")
    
    # Get summary
    summary = feedback_loop.get_feedback_summary()
    print(f"Feedback summary: {summary}")
    
    # Get recommendations
    recommendations = feedback_loop.get_improvement_recommendations()
    print(f"Recommendations: {len(recommendations)} found")