import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import json
import importlib.util

# Add the backend directory to the path and import main module
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import main module dynamically
spec = importlib.util.spec_from_file_location("main", os.path.join(backend_path, "main.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

# Get the functions and variables to test
perform_web_search = main_module.perform_web_search
combine_sources = main_module.combine_sources
initialize_documents = main_module.initialize_documents

class TestCoreComponents:
    """
    Unit tests for core ASK_GILLU functions
    """
    
    def test_perform_web_search_success(self):
        """Test web search function with successful results"""
        print("\n🔍 Testing web search function...")
        
        # Mock DuckDuckGo results
        mock_results = [
            {
                'title': 'Test Title 1',
                'href': 'https://example.com/1',
                'body': 'Test content 1'
            },
            {
                'title': 'Test Title 2',
                'href': 'https://example.com/2',
                'body': 'Test content 2'
            }
        ]
        
        with patch('main.DDGS') as mock_ddgs:
            mock_ddgs.return_value.__enter__.return_value.text.return_value = mock_results
            
            result = perform_web_search("test query")
            
            assert "Result 1:" in result
            assert "Test Title 1" in result
            assert "https://example.com/1" in result
            assert "Test content 1" in result
            assert "Result 2:" in result
            assert "Test Title 2" in result
        
        print("✅ Web search function working correctly")
    
    def test_perform_web_search_no_results(self):
        """Test web search function with no results"""
        print("\n🔍 Testing web search with no results...")
        
        with patch('main.DDGS') as mock_ddgs:
            mock_ddgs.return_value.__enter__.return_value.text.return_value = []
            
            result = perform_web_search("test query")
            
            assert "No web search results found" in result
        
        print("✅ No results case handled correctly")
    
    def test_perform_web_search_error(self):
        """Test web search function with error"""
        print("\n🔍 Testing web search error handling...")
        
        with patch('main.DDGS') as mock_ddgs:
            mock_ddgs.return_value.__enter__.side_effect = Exception("Network error")
            
            result = perform_web_search("test query")
            
            assert "Web search error" in result
            assert "Network error" in result
        
        print("✅ Web search error handled correctly")
    
    def test_combine_sources_document_only(self):
        """Test combining sources with documents only"""
        print("\n🔍 Testing document-only source combination...")
        
        with patch('main.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('main.FAISS') as mock_faiss:
            
            # Mock vectorstore
            mock_vectorstore = MagicMock()
            mock_doc1 = MagicMock()
            mock_doc1.page_content = "Document content 1"
            mock_doc2 = MagicMock()
            mock_doc2.page_content = "Document content 2"
            mock_vectorstore.similarity_search.return_value = [mock_doc1, mock_doc2]
            mock_faiss.load_local.return_value = mock_vectorstore
            
            result = combine_sources("test question", "test prompt", use_web_search=False)
            
            assert "UNIVERSITY DOCUMENTS:" in result
            assert "Document content 1" in result
            assert "Document content 2" in result
            assert "WEB SEARCH RESULTS:" not in result
        
        print("✅ Document-only combination working correctly")
    
    def test_combine_sources_with_web_search(self):
        """Test combining sources with web search"""
        print("\n🔍 Testing combined sources with web search...")
        
        with patch('main.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('main.FAISS') as mock_faiss, \
             patch('main.perform_web_search') as mock_web_search:
            
            # Mock vectorstore
            mock_vectorstore = MagicMock()
            mock_doc1 = MagicMock()
            mock_doc1.page_content = "Document content 1"
            mock_vectorstore.similarity_search.return_value = [mock_doc1]
            mock_faiss.load_local.return_value = mock_vectorstore
            
            # Mock web search
            mock_web_search.return_value = "Web search result 1"
            
            result = combine_sources("test question", "test prompt", use_web_search=True)
            
            assert "UNIVERSITY DOCUMENTS:" in result
            assert "Document content 1" in result
            assert "WEB SEARCH RESULTS:" in result
            assert "Web search result 1" in result
        
        print("✅ Combined sources working correctly")
    
    def test_combine_sources_no_documents(self):
        """Test combining sources when no documents are found"""
        print("\n🔍 Testing source combination with no documents...")
        
        with patch('main.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('main.FAISS') as mock_faiss:
            
            # Mock empty vectorstore
            mock_faiss.load_local.side_effect = Exception("No documents found")
            
            result = combine_sources("test question", "test prompt", use_web_search=False)
            
            # Should handle gracefully
            assert isinstance(result, str)
        
        print("✅ No documents case handled correctly")
    
    @patch('main.os.path.exists')
    @patch('main.glob.glob')
    @patch('main.PdfReader')
    def test_initialize_documents_success(self, mock_pdf_reader, mock_glob, mock_exists):
        """Test document initialization with successful loading"""
        print("\n🔍 Testing document initialization...")
        
        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [
            '/path/to/docs/Questions[1] (1).pdf',
            '/path/to/docs/Shrinjay Shresth Resume DataScience.pdf'
        ]
        
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Mock text splitter and embeddings
        with patch('main.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('main.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('main.FAISS') as mock_faiss, \
             patch('main.os.makedirs'):
            
            mock_splitter.return_value.split_text.return_value = ["chunk1", "chunk2"]
            mock_vectorstore = MagicMock()
            mock_faiss.from_texts.return_value = mock_vectorstore
            
            # This should not raise an exception
            initialize_documents()
        
        print("✅ Document initialization working correctly")
    
    @patch('main.os.path.exists')
    @patch('main.glob.glob')
    def test_initialize_documents_no_files(self, mock_glob, mock_exists):
        """Test document initialization with no files"""
        print("\n🔍 Testing document initialization with no files...")
        
        mock_exists.return_value = True
        mock_glob.return_value = []
        
        # This should handle gracefully
        initialize_documents()
        
        print("✅ No files case handled correctly")

class TestEnvironmentVariables:
    """Test environment variable handling"""
    
    def test_groq_api_key_present(self):
        """Test that GROQ_API_KEY is properly loaded"""
        print("\n🔍 Testing GROQ API key loading...")
        
        # Use the dynamically imported module
        GROQ_API_KEY = getattr(main_module, 'GROQ_API_KEY', None)
        
        assert GROQ_API_KEY is not None
        assert len(GROQ_API_KEY) > 0
        assert GROQ_API_KEY.startswith("gsk_")
        
        print("✅ GROQ API key loaded correctly")
    
    def test_db_path_configuration(self):
        """Test database path configuration"""
        print("\n🔍 Testing database path configuration...")
        
        DB_FAISS_PATH = getattr(main_module, 'DB_FAISS_PATH', None)
        
        assert DB_FAISS_PATH == 'vectorstore/db_faiss'
        
        print("✅ Database path configured correctly")

class TestDocumentConfiguration:
    """Test document configuration"""
    
    def test_allowed_documents_list(self):
        """Test allowed documents configuration"""
        print("\n🔍 Testing allowed documents configuration...")
        
        ALLOWED_DOCUMENTS = getattr(main_module, 'ALLOWED_DOCUMENTS', None)
        
        assert isinstance(ALLOWED_DOCUMENTS, list)
        assert len(ALLOWED_DOCUMENTS) > 0
        assert "Questions[1] (1).pdf" in ALLOWED_DOCUMENTS
        assert "Shrinjay Shresth Resume DataScience.pdf" in ALLOWED_DOCUMENTS
        assert "Web-Based-GIS.pdf" in ALLOWED_DOCUMENTS
        
        print("✅ Allowed documents configured correctly")

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_missing_environment_variable(self):
        """Test handling of missing environment variables"""
        print("\n🔍 Testing missing environment variable handling...")
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.load_dotenv'):
                with patch('main.os.getenv', return_value=None):
                    try:
                        # This should raise an exception
                        exec(open('../backend/main.py').read())
                        assert False, "Should have raised ValueError"
                    except ValueError as e:
                        assert "GROQ_API_KEY" in str(e)
        
        print("✅ Missing environment variable handled correctly")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
