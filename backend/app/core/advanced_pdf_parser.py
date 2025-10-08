#!/usr/bin/env python3
"""
Advanced PDF Parser
Provides multiple PDF parsing strategies for better text extraction
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# PDF parsing libraries
try:
    from pypdf import PdfReader as PyPDFReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pymupdf as fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.layout import LTTextContainer, LTTextBox, LTFigure, LTRect
    from pdfminer.converter import TextConverter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from io import StringIO
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

# OCR libraries for scanned PDFs
try:
    import pytesseract
    from PIL import Image
    import fitz  # For image extraction
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedPDFParser:
    """
    Advanced PDF parser that tries multiple extraction methods
    """
    
    def __init__(self):
        self.available_parsers = self._check_available_parsers()
        logger.info(f"Available PDF parsers: {', '.join(self.available_parsers)}")
    
    def _check_available_parsers(self) -> List[str]:
        """Check which PDF parsing libraries are available"""
        parsers = []
        if PYPDF_AVAILABLE:
            parsers.append("pypdf")
        if PDFPLUMBER_AVAILABLE:
            parsers.append("pdfplumber")
        if PYMUPDF_AVAILABLE:
            parsers.append("pymupdf")
        if PDFMINER_AVAILABLE:
            parsers.append("pdfminer")
        if OCR_AVAILABLE:
            parsers.append("ocr")
        return parsers
        if PYMUPDF_AVAILABLE:
            parsers.append("pymupdf")
        if OCR_AVAILABLE:
            parsers.append("ocr")
        return parsers
    
    def extract_text_pypdf(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using PyPDF (fast but basic)"""
        try:
            reader = PyPDFReader(file_path)
            text = ""
            metadata = {
                "parser": "pypdf",
                "pages": len(reader.pages),
                "success": True
            }
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip(), metadata
            
        except Exception as e:
            logger.error(f"PyPDF extraction failed: {str(e)}")
            return "", {"parser": "pypdf", "success": False, "error": str(e)}
    
    def extract_text_pdfplumber(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using pdfplumber (better table handling)"""
        try:
            text = ""
            metadata = {
                "parser": "pdfplumber",
                "pages": 0,
                "success": True,
                "tables_found": 0
            }
            
            with pdfplumber.open(file_path) as pdf:
                metadata["pages"] = len(pdf.pages)
                
                for page in pdf.pages:
                    # Extract regular text
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        metadata["tables_found"] += len(tables)
                        for table in tables:
                            # Convert table to text
                            for row in table:
                                if row:
                                    row_text = " | ".join([cell if cell else "" for cell in row])
                                    text += row_text + "\n"
            
            return text.strip(), metadata
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return "", {"parser": "pdfplumber", "success": False, "error": str(e)}
    
    def extract_text_pymupdf(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using PyMuPDF (fast and accurate)"""
        try:
            text = ""
            metadata = {
                "parser": "pymupdf",
                "pages": 0,
                "success": True,
                "images_found": 0
            }
            
            doc = fitz.open(file_path)
            metadata["pages"] = len(doc)
            
            for page in doc:
                # Extract text
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
                
                # Count images (for OCR consideration)
                images = page.get_images()
                metadata["images_found"] += len(images)
            
            doc.close()
            return text.strip(), metadata
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            return "", {"parser": "pymupdf", "success": False, "error": str(e)}
    
    def extract_text_ocr(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using OCR for scanned PDFs"""
        try:
            text = ""
            metadata = {
                "parser": "ocr",
                "pages": 0,
                "success": True,
                "method": "tesseract"
            }
            
            doc = fitz.open(file_path)
            metadata["pages"] = len(doc)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Higher resolution for better OCR
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Extract text using OCR
                page_text = pytesseract.image_to_string(img, lang='eng')
                if page_text.strip():
                    text += page_text + "\n"
            
            doc.close()
            return text.strip(), metadata
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return "", {"parser": "ocr", "success": False, "error": str(e)}
    
    def extract_text_pdfminer(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text using pdfminer.six (excellent for complex layouts)"""
        try:
            metadata = {
                "parser": "pdfminer",
                "success": True,
                "method": "high_level",
                "layout_analysis": True
            }
            
            # Method 1: Simple high-level extraction
            text = extract_text(file_path)
            
            if text and len(text.strip()) > 50:
                # Good extraction, return it
                metadata["text_length"] = len(text)
                return text.strip(), metadata
            
            # Method 2: Advanced layout analysis for complex documents
            text_parts = []
            metadata["method"] = "layout_analysis"
            
            for page_layout in extract_pages(file_path):
                page_text = self._extract_text_from_layout(page_layout)
                if page_text:
                    text_parts.append(page_text)
            
            combined_text = "\n".join(text_parts)
            metadata["text_length"] = len(combined_text)
            
            return combined_text.strip(), metadata
            
        except Exception as e:
            logger.error(f"pdfminer extraction failed: {str(e)}")
            return "", {"parser": "pdfminer", "success": False, "error": str(e)}
    
    def _extract_text_from_layout(self, layout_obj) -> str:
        """Extract text from pdfminer layout objects with structure preservation"""
        text_parts = []
        
        def extract_text_recursive(obj):
            if hasattr(obj, 'get_text'):
                return obj.get_text()
            elif isinstance(obj, LTTextContainer):
                # Text container - extract text maintaining structure
                text = ""
                for child in obj:
                    if hasattr(child, 'get_text'):
                        child_text = child.get_text()
                        if child_text.strip():
                            text += child_text
                return text
            elif hasattr(obj, '__iter__'):
                # Iterate through children
                texts = []
                for child in obj:
                    child_text = extract_text_recursive(child)
                    if child_text and child_text.strip():
                        texts.append(child_text.strip())
                return "\n".join(texts)
            return ""
        
        return extract_text_recursive(layout_obj)
    
    def extract_text_hybrid(self, file_path: str) -> Tuple[str, Dict]:
        """
        Try multiple extraction methods and return the best result
        """
        results = []
        
        # Try each available parser
        if "pymupdf" in self.available_parsers:
            text, metadata = self.extract_text_pymupdf(file_path)
            if metadata["success"] and text:
                results.append((text, metadata, len(text)))
        
        if "pdfminer" in self.available_parsers:
            text, metadata = self.extract_text_pdfminer(file_path)
            if metadata["success"] and text:
                results.append((text, metadata, len(text)))
        
        if "pdfplumber" in self.available_parsers:
            text, metadata = self.extract_text_pdfplumber(file_path)
            if metadata["success"] and text:
                results.append((text, metadata, len(text)))
        
        if "pypdf" in self.available_parsers:
            text, metadata = self.extract_text_pypdf(file_path)
            if metadata["success"] and text:
                results.append((text, metadata, len(text)))
        
        # If no text found and OCR is available, try OCR
        if not results and "ocr" in self.available_parsers:
            text, metadata = self.extract_text_ocr(file_path)
            if metadata["success"] and text:
                results.append((text, metadata, len(text)))
        
        if not results:
            return "", {"parser": "hybrid", "success": False, "error": "All parsers failed"}
        
        # Return the result with most text
        best_result = max(results, key=lambda x: x[2])
        text, metadata, _ = best_result
        
        # Update metadata to show it was hybrid
        metadata["parser"] = f"hybrid-{metadata['parser']}"
        metadata["total_parsers_tried"] = len(results)
        
        return text, metadata
    
    def parse_pdf(self, file_path: str, method: str = "hybrid") -> Tuple[str, Dict]:
        """
        Parse PDF with specified method
        
        Args:
            file_path: Path to PDF file
            method: Parsing method ('hybrid', 'pypdf', 'pdfplumber', 'pymupdf', 'pdfminer', 'ocr')
        
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if not os.path.exists(file_path):
            return "", {"success": False, "error": "File not found"}
        
        logger.info(f"Parsing PDF: {file_path} with method: {method}")
        
        if method == "hybrid":
            return self.extract_text_hybrid(file_path)
        elif method == "pypdf" and "pypdf" in self.available_parsers:
            return self.extract_text_pypdf(file_path)
        elif method == "pdfplumber" and "pdfplumber" in self.available_parsers:
            return self.extract_text_pdfplumber(file_path)
        elif method == "pymupdf" and "pymupdf" in self.available_parsers:
            return self.extract_text_pymupdf(file_path)
        elif method == "pdfminer" and "pdfminer" in self.available_parsers:
            return self.extract_text_pdfminer(file_path)
        elif method == "ocr" and "ocr" in self.available_parsers:
            return self.extract_text_ocr(file_path)
        else:
            return "", {"success": False, "error": f"Method '{method}' not available"}
    
    def get_parser_recommendations(self, file_path: str) -> Dict:
        """
        Analyze PDF and recommend best parsing strategy
        """
        recommendations = {
            "file_size": os.path.getsize(file_path),
            "recommended_parser": "hybrid",
            "reasons": []
        }
        
        # Quick check with PyMuPDF to analyze document
        if "pymupdf" in self.available_parsers:
            try:
                doc = fitz.open(file_path)
                page_count = len(doc)
                
                # Check first page for analysis
                if page_count > 0:
                    first_page = doc.load_page(0)
                    text_length = len(first_page.get_text())
                    image_count = len(first_page.get_images())
                    
                    recommendations["pages"] = page_count
                    recommendations["text_on_first_page"] = text_length
                    recommendations["images_on_first_page"] = image_count
                    
                    if text_length < 100 and image_count > 0:
                        recommendations["recommended_parser"] = "ocr"
                        recommendations["reasons"].append("Low text content, high image content - likely scanned")
                    elif page_count > 100:
                        recommendations["recommended_parser"] = "pymupdf"
                        recommendations["reasons"].append("Large document - PyMuPDF is fastest")
                    elif image_count == 0 and text_length > 500:
                        # Text-heavy document might benefit from pdfminer's layout analysis
                        recommendations["recommended_parser"] = "pdfminer"
                        recommendations["reasons"].append("Text-heavy document - pdfminer excellent for complex layouts")
                    else:
                        recommendations["recommended_parser"] = "hybrid"
                        recommendations["reasons"].append("Standard document - hybrid approach recommended")
                
                doc.close()
                
            except Exception as e:
                recommendations["analysis_error"] = str(e)
        
        return recommendations


def get_pdf_parser() -> AdvancedPDFParser:
    """Get a configured PDF parser instance"""
    return AdvancedPDFParser()


if __name__ == "__main__":
    # Test the parser
    parser = AdvancedPDFParser()
    print(f"Available parsers: {parser.available_parsers}")
    
    # Example usage
    # text, metadata = parser.parse_pdf("example.pdf", method="hybrid")
    # print(f"Extracted {len(text)} characters")
    # print(f"Metadata: {metadata}")