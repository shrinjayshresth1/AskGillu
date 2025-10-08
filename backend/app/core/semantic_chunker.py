#!/usr/bin/env python3
"""
Semantic Chunker - Advanced Document Sectioning
Preserves document structure and creates semantic chunks instead of fixed-length chunks
Based on production RAG optimization lessons from legal tech industry
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import spacy
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkType(Enum):
    """Types of semantic chunks"""
    HEADER = "header"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    FOOTNOTE = "footnote"
    SECTION = "section"
    SUBSECTION = "subsection"

@dataclass
class SemanticChunk:
    """A semantically meaningful chunk of text"""
    content: str
    chunk_type: ChunkType
    hierarchy_level: int
    section_title: Optional[str] = None
    parent_section: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None

class SemanticChunker:
    """
    Advanced semantic chunker that preserves document structure
    Creates chunks based on document semantics rather than fixed character limits
    """
    
    def __init__(self, 
                 max_chunk_size: int = 2000,
                 min_chunk_size: int = 100,
                 overlap_sentences: int = 2,
                 enable_spacy: bool = True):
        """
        Initialize semantic chunker
        
        Args:
            max_chunk_size: Maximum characters per chunk
            min_chunk_size: Minimum characters per chunk
            overlap_sentences: Number of sentences to overlap between chunks
            enable_spacy: Whether to use spaCy for advanced NLP processing
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_sentences = overlap_sentences
        self.enable_spacy = enable_spacy
        
        # Initialize spaCy model if available
        self.nlp = None
        if enable_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.enable_spacy = False
        
        # Fallback text splitter for very long chunks
        self.fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Patterns for document structure detection
        self.header_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
            r'^(\d+\.?\s+[A-Z].+)$',  # Numbered sections
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):?\s*$',  # Title case headers
            r'^(Chapter|Section|Part)\s+(\d+|[IVX]+)[\.\:]?\s*(.*)$',  # Chapter/Section headers
        ]
        
        self.list_patterns = [
            r'^[-•*]\s+(.+)$',  # Bullet points
            r'^\d+\.\s+(.+)$',  # Numbered lists
            r'^[a-z]\)\s+(.+)$',  # Lettered lists
            r'^[IVX]+\.\s+(.+)$',  # Roman numeral lists
        ]

    def chunk_document(self, text: str, metadata: Optional[Dict] = None) -> List[Document]:
        """
        Chunk document using semantic analysis
        
        Args:
            text: Raw document text
            metadata: Document metadata
            
        Returns:
            List of LangChain Document objects with semantic chunks
        """
        logger.info(f"Starting semantic chunking for document ({len(text)} characters)")
        
        # Clean and preprocess text
        text = self._preprocess_text(text)
        
        # Detect document structure
        semantic_chunks = self._analyze_document_structure(text)
        
        # Group chunks by semantic boundaries
        grouped_chunks = self._group_semantic_chunks(semantic_chunks)
        
        # Create final document chunks
        documents = self._create_documents(grouped_chunks, metadata or {})
        
        logger.info(f"Created {len(documents)} semantic chunks")
        return documents

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()

    def _analyze_document_structure(self, text: str) -> List[SemanticChunk]:
        """Analyze document structure and create semantic chunks"""
        lines = text.split('\n')
        chunks = []
        current_section = None
        current_subsection = None
        hierarchy_level = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check for headers
            header_info = self._detect_header(line)
            if header_info:
                chunk_type, level, title = header_info
                hierarchy_level = level
                
                if level <= 2:
                    current_section = title
                    current_subsection = None
                else:
                    current_subsection = title
                
                chunks.append(SemanticChunk(
                    content=line,
                    chunk_type=ChunkType.HEADER,
                    hierarchy_level=level,
                    section_title=title,
                    parent_section=current_section,
                    start_position=i
                ))
                
            # Check for list items
            elif self._is_list_item(line):
                # Collect consecutive list items
                list_content = []
                start_idx = i
                
                while i < len(lines) and self._is_list_item(lines[i].strip()):
                    list_content.append(lines[i].strip())
                    i += 1
                
                chunks.append(SemanticChunk(
                    content='\n'.join(list_content),
                    chunk_type=ChunkType.LIST_ITEM,
                    hierarchy_level=hierarchy_level + 1,
                    section_title=current_subsection or current_section,
                    parent_section=current_section,
                    start_position=start_idx,
                    end_position=i-1
                ))
                continue
                
            # Regular paragraph
            else:
                # Collect paragraph content
                paragraph_lines = [line]
                start_idx = i
                i += 1
                
                # Continue collecting until empty line or special content
                while (i < len(lines) and 
                       lines[i].strip() and 
                       not self._detect_header(lines[i].strip()) and
                       not self._is_list_item(lines[i].strip())):
                    paragraph_lines.append(lines[i].strip())
                    i += 1
                
                paragraph_content = ' '.join(paragraph_lines)
                
                # Only create chunk if it has substantial content
                if len(paragraph_content) >= self.min_chunk_size:
                    chunks.append(SemanticChunk(
                        content=paragraph_content,
                        chunk_type=ChunkType.PARAGRAPH,
                        hierarchy_level=hierarchy_level + 1,
                        section_title=current_subsection or current_section,
                        parent_section=current_section,
                        start_position=start_idx,
                        end_position=i-1
                    ))
                continue
            
            i += 1
        
        return chunks

    def _detect_header(self, line: str) -> Optional[Tuple[ChunkType, int, str]]:
        """Detect if line is a header and determine its level"""
        for pattern in self.header_patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # Determine hierarchy level based on pattern type
                if line.startswith('#'):
                    level = len(line.split()[0])  # Count # symbols
                elif line.isupper():
                    level = 1  # ALL CAPS likely top level
                elif re.match(r'^\d+\.', line):
                    level = 2  # Numbered sections
                elif line.startswith(('Chapter', 'Section', 'Part')):
                    level = 1  # Formal sections
                else:
                    level = 3  # Default subsection level
                
                title = match.group(1) if match.groups() else line
                return ChunkType.HEADER, level, title.strip()
        
        return None

    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item"""
        for pattern in self.list_patterns:
            if re.match(pattern, line):
                return True
        return False

    def _group_semantic_chunks(self, chunks: List[SemanticChunk]) -> List[SemanticChunk]:
        """Group chunks by semantic boundaries while respecting size limits"""
        grouped_chunks = []
        current_group = []
        current_size = 0
        
        for chunk in chunks:
            chunk_size = len(chunk.content)
            
            # If adding this chunk would exceed max size, finalize current group
            if current_size + chunk_size > self.max_chunk_size and current_group:
                # Create grouped chunk
                grouped_content = self._merge_chunk_group(current_group)
                grouped_chunks.append(grouped_content)
                
                # Start new group
                current_group = [chunk]
                current_size = chunk_size
            else:
                current_group.append(chunk)
                current_size += chunk_size
        
        # Handle remaining chunks
        if current_group:
            grouped_content = self._merge_chunk_group(current_group)
            grouped_chunks.append(grouped_content)
        
        return grouped_chunks

    def _merge_chunk_group(self, chunk_group: List[SemanticChunk]) -> SemanticChunk:
        """Merge a group of chunks into a single semantic chunk"""
        if not chunk_group:
            return None
        
        if len(chunk_group) == 1:
            return chunk_group[0]
        
        # Determine the dominant chunk type and hierarchy
        main_chunk = chunk_group[0]
        content_parts = []
        
        for chunk in chunk_group:
            content_parts.append(chunk.content)
        
        merged_content = '\n\n'.join(content_parts)
        
        # If merged content is too long, split using fallback splitter
        if len(merged_content) > self.max_chunk_size:
            logger.warning(f"Merged chunk ({len(merged_content)} chars) exceeds max size, using fallback splitting")
            split_docs = self.fallback_splitter.split_text(merged_content)
            
            # Return first split as primary chunk
            if split_docs:
                return SemanticChunk(
                    content=split_docs[0],
                    chunk_type=main_chunk.chunk_type,
                    hierarchy_level=main_chunk.hierarchy_level,
                    section_title=main_chunk.section_title,
                    parent_section=main_chunk.parent_section,
                    metadata={"split_from_large_section": True, "original_size": len(merged_content)}
                )
        
        return SemanticChunk(
            content=merged_content,
            chunk_type=ChunkType.SECTION,
            hierarchy_level=main_chunk.hierarchy_level,
            section_title=main_chunk.section_title,
            parent_section=main_chunk.parent_section,
            metadata={"merged_chunks": len(chunk_group)}
        )

    def _create_documents(self, chunks: List[SemanticChunk], base_metadata: Dict) -> List[Document]:
        """Convert semantic chunks to LangChain Documents"""
        documents = []
        
        for i, chunk in enumerate(chunks):
            if not chunk or not chunk.content.strip():
                continue
            
            # Create enhanced metadata
            metadata = base_metadata.copy()
            metadata.update({
                "chunk_index": i,
                "chunk_type": chunk.chunk_type.value,
                "hierarchy_level": chunk.hierarchy_level,
                "section_title": chunk.section_title,
                "parent_section": chunk.parent_section,
                "chunk_size": len(chunk.content),
                "semantic_chunking": True
            })
            
            # Add chunk-specific metadata
            if chunk.metadata:
                metadata.update(chunk.metadata)
            
            # Create document
            doc = Document(
                page_content=chunk.content,
                metadata=metadata
            )
            
            documents.append(doc)
        
        return documents

    def get_chunking_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the chunking process"""
        if not documents:
            return {}
        
        chunk_sizes = [len(doc.page_content) for doc in documents]
        chunk_types = [doc.metadata.get("chunk_type", "unknown") for doc in documents]
        
        from collections import Counter
        type_counts = Counter(chunk_types)
        
        return {
            "total_chunks": len(documents),
            "average_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "chunk_type_distribution": dict(type_counts),
            "total_characters": sum(chunk_sizes)
        }

def get_semantic_chunker(max_chunk_size: int = 2000, 
                        min_chunk_size: int = 100,
                        overlap_sentences: int = 2,
                        enable_spacy: bool = True) -> SemanticChunker:
    """
    Get a configured semantic chunker instance
    
    Args:
        max_chunk_size: Maximum characters per chunk
        min_chunk_size: Minimum characters per chunk
        overlap_sentences: Number of sentences to overlap
        enable_spacy: Whether to use spaCy for NLP processing
    
    Returns:
        Configured SemanticChunker instance
    """
    return SemanticChunker(
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        overlap_sentences=overlap_sentences,
        enable_spacy=enable_spacy
    )

if __name__ == "__main__":
    # Test the semantic chunker
    sample_text = """
# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.

## Types of Machine Learning

There are three main types of machine learning:

- Supervised Learning: Uses labeled training data
- Unsupervised Learning: Finds patterns in unlabeled data  
- Reinforcement Learning: Learns through interaction with environment

### Supervised Learning

Supervised learning algorithms learn from input-output pairs. Common algorithms include:

1. Linear Regression
2. Decision Trees
3. Neural Networks

The goal is to make predictions on new, unseen data.

## Applications

Machine learning is used in many domains including healthcare, finance, and technology.
    """
    
    chunker = get_semantic_chunker()
    documents = chunker.chunk_document(sample_text)
    
    print(f"Created {len(documents)} semantic chunks:")
    for i, doc in enumerate(documents):
        print(f"\nChunk {i+1}:")
        print(f"Type: {doc.metadata.get('chunk_type')}")
        print(f"Section: {doc.metadata.get('section_title')}")
        print(f"Content: {doc.page_content[:100]}...")
    
    # Print statistics
    stats = chunker.get_chunking_stats(documents)
    print(f"\nChunking Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")