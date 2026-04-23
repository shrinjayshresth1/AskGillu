"""
Application configuration settings.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Vector Database Configuration
    DEFAULT_DB_TYPE = os.getenv("DEFAULT_DB_TYPE", "qdrant")
    
    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "askgillu_documents")
    
    # FAISS Configuration
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./vectorstore/db_faiss")
    
    # Document Processing Configuration
    ALLOWED_DOCUMENTS: List[str] = [
        "Questions[1] (1).pdf",
        "Shrinjay Shresth Resume DataScience.pdf",
        "Web-Based-GIS.pdf"
    ]
    
    # Web Search Configuration
    # Only allow SRMU domain to restrict web search purely to the university
    ALLOWED_WEBSITES: List[str] = [
        "srmu.ac.in"
    ]
    
    # Auto-scraping Configuration
    AUTO_SCRAPE_WEBSITES: List[Dict[str, Any]] = [
        {
            "url": "https://srmu.ac.in/placement-overview",
            "name": "SRMU Placement Overview",
            "priority": 1
        },
        {
            "url": "https://srmu.ac.in/academics/courses",
            "name": "SRMU Course Catalog", 
            "priority": 1
        },
        {
            "url": "https://en.wikipedia.org/wiki/Data_science",
            "name": "Data Science Overview",
            "priority": 2
        },
        {
            "url": "https://en.wikipedia.org/wiki/Machine_learning",
            "name": "Machine Learning Overview", 
            "priority": 2
        }
    ]
    
    AUTO_SCRAPE_CONFIG: Dict[str, Any] = {
        "enabled": False,
        "scrape_on_startup": False,
        "update_interval_hours": 24,
        "max_retries": 3,
        "timeout_per_url": 30,
    }
    
    WEB_SCRAPER_CONFIG: Dict[str, Any] = {
        "delay": 1.0,
        "max_urls_per_request": 20,
        "max_content_length": 50000,
        "timeout": 30,
        "scraped_data_dir": "scraped_data"
    }
    
    # Advanced RAG Configuration
    ADVANCED_RAG_CONFIG: Dict[str, Any] = {
        # Semantic Chunking
        "enable_semantic_chunking": os.getenv("ENABLE_SEMANTIC_CHUNKING", "true").lower() == "true",
        "semantic_chunk_size": int(os.getenv("SEMANTIC_CHUNK_SIZE", "1000")),
        "semantic_chunk_overlap": int(os.getenv("SEMANTIC_CHUNK_OVERLAP", "200")),
        
        # Advanced Re-ranking
        "enable_reranking": os.getenv("ENABLE_RERANKING", "true").lower() == "true",
        "reranking_strategy": os.getenv("RERANKING_STRATEGY", "rrf"),  # rrf, semantic, diversity, contextual
        "rerank_top_k": int(os.getenv("RERANK_TOP_K", "10")),
        "final_top_k": int(os.getenv("FINAL_TOP_K", "5")),
        
        # Response Caching
        "enable_caching": os.getenv("ENABLE_RESPONSE_CACHING", "true").lower() == "true",
        "cache_similarity_threshold": float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.85")),
        "cache_ttl_hours": int(os.getenv("CACHE_TTL_HOURS", "24")),
        "max_cache_size": int(os.getenv("MAX_CACHE_SIZE", "1000")),
        
        # Feedback Loop
        "enable_feedback_tracking": os.getenv("ENABLE_FEEDBACK_TRACKING", "true").lower() == "true",
        "feedback_weight": float(os.getenv("FEEDBACK_WEIGHT", "0.1")),
        "min_feedback_threshold": int(os.getenv("MIN_FEEDBACK_THRESHOLD", "3")),
        
        # Performance Monitoring
        "enable_performance_monitoring": os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true",
        "performance_log_interval": int(os.getenv("PERFORMANCE_LOG_INTERVAL", "100")),  # queries
        "slow_query_threshold_ms": int(os.getenv("SLOW_QUERY_THRESHOLD_MS", "5000"))
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}