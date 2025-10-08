import pytest
import requests
import json
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestASKGILLUBackend:
    """
    Test suite for ASK_GILLU Backend API
    """
    
    BASE_URL = "http://127.0.0.1:8000"
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        print("🚀 Setting up ASK_GILLU Backend Tests...")
        
        # Check if backend is running
        try:
            response = requests.get(f"{cls.BASE_URL}/status", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is running")
            else:
                print("❌ Backend is not responding correctly")
                raise Exception("Backend not ready")
        except requests.exceptions.RequestException:
            print("❌ Backend is not running. Please start it first.")
            raise Exception("Backend not accessible")
    
    def test_backend_status(self):
        """Test /status endpoint"""
        print("\n🔍 Testing backend status endpoint...")
        
        response = requests.get(f"{self.BASE_URL}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert data["status"] == "ready"
        
        print("✅ Status endpoint working correctly")
    
    def test_ask_endpoint_document_only(self):
        """Test /ask endpoint with document-only search"""
        print("\n🔍 Testing document-only search...")
        
        payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert "SRMU" in data["answer"] or "university" in data["answer"].lower()
        
        print("✅ Document-only search working correctly")
    
    def test_ask_endpoint_web_search(self):
        """Test /ask endpoint with web search enabled"""
        print("\n🔍 Testing web search functionality...")
        
        payload = {
            "question": "What is artificial intelligence?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": True
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert len(data["answer"]) > 0
        
        print("✅ Web search functionality working correctly")
    
    def test_ask_endpoint_combined_search(self):
        """Test /ask endpoint with combined search"""
        print("\n🔍 Testing combined search (documents + web)...")
        
        payload = {
            "question": "What courses does SRMU offer in computer science?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": True
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert len(data["answer"]) > 0
        
        print("✅ Combined search working correctly")
    
    def test_ask_endpoint_empty_question(self):
        """Test /ask endpoint with empty question"""
        print("\n🔍 Testing empty question handling...")
        
        payload = {
            "question": "",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        
        # Should handle empty question gracefully
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        
        print("✅ Empty question handled correctly")
    
    def test_ask_endpoint_custom_prompt(self):
        """Test /ask endpoint with custom system prompt"""
        print("\n🔍 Testing custom system prompt...")
        
        custom_prompt = "You are a casual, friendly assistant. Use simple language."
        payload = {
            "question": "What is SRMU?",
            "system_prompt": custom_prompt,
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert len(data["answer"]) > 0
        
        print("✅ Custom system prompt working correctly")
    
    def test_cors_headers(self):
        """Test CORS headers"""
        print("\n🔍 Testing CORS headers...")
        
        response = requests.options(f"{self.BASE_URL}/ask")
        
        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        
        print("✅ CORS headers configured correctly")
    
    def test_response_time(self):
        """Test response time performance"""
        print("\n🔍 Testing response time...")
        
        start_time = time.time()
        
        payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30  # Should respond within 30 seconds
        
        print(f"✅ Response time: {response_time:.2f} seconds")
    
    def test_large_question(self):
        """Test handling of large questions"""
        print("\n🔍 Testing large question handling...")
        
        large_question = "What is SRMU? " * 100  # Repeat question 100 times
        payload = {
            "question": large_question,
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        
        print("✅ Large question handled correctly")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
