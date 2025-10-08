import pytest
import requests
import time
import json
import os
from typing import Dict, Any

class TestIntegration:
    """
    Integration tests for the complete ASK_GILLU system
    """
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_complete_workflow_document_search(self):
        """Test complete workflow with document search"""
        print("\n🔄 Testing complete document search workflow...")
        
        # Step 1: Check system status
        status_response = requests.get(f"{self.BASE_URL}/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["status"] == "ready"
        print("  ✅ System status check passed")
        
        # Step 2: Perform document search
        payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are ASK_GILLU, a helpful assistant for SRMU.",
            "use_web_search": False
        }
        
        ask_response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        assert ask_response.status_code == 200
        
        ask_data = ask_response.json()
        assert "answer" in ask_data
        assert len(ask_data["answer"]) > 0
        print("  ✅ Document search completed")
        
        # Step 3: Verify answer quality
        answer = ask_data["answer"].lower()
        assert any(keyword in answer for keyword in ["srmu", "university", "memorial", "ramswaroop"])
        print("  ✅ Answer quality verified")
        
        print("✅ Complete document search workflow passed")
    
    def test_complete_workflow_web_search(self):
        """Test complete workflow with web search"""
        print("\n🌐 Testing complete web search workflow...")
        
        # Step 1: Check system status
        status_response = requests.get(f"{self.BASE_URL}/status")
        assert status_response.status_code == 200
        print("  ✅ System status check passed")
        
        # Step 2: Perform web search
        payload = {
            "question": "What is artificial intelligence?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": True
        }
        
        ask_response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=30)
        assert ask_response.status_code == 200
        
        ask_data = ask_response.json()
        assert "answer" in ask_data
        assert len(ask_data["answer"]) > 0
        print("  ✅ Web search completed")
        
        # Step 3: Verify answer contains relevant information
        answer = ask_data["answer"].lower()
        assert any(keyword in answer for keyword in ["artificial", "intelligence", "ai", "machine", "learning"])
        print("  ✅ Answer quality verified")
        
        print("✅ Complete web search workflow passed")
    
    def test_complete_workflow_combined_search(self):
        """Test complete workflow with combined search"""
        print("\n🔗 Testing complete combined search workflow...")
        
        # Step 1: Check system status
        status_response = requests.get(f"{self.BASE_URL}/status")
        assert status_response.status_code == 200
        print("  ✅ System status check passed")
        
        # Step 2: Perform combined search
        payload = {
            "question": "What computer science courses does SRMU offer?",
            "system_prompt": "You are ASK_GILLU, combining university documents with web information.",
            "use_web_search": True
        }
        
        ask_response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=30)
        assert ask_response.status_code == 200
        
        ask_data = ask_response.json()
        assert "answer" in ask_data
        assert len(ask_data["answer"]) > 0
        print("  ✅ Combined search completed")
        
        # Step 3: Verify answer contains relevant information
        answer = ask_data["answer"].lower()
        assert any(keyword in answer for keyword in ["computer", "science", "course", "program"])
        print("  ✅ Answer quality verified")
        
        print("✅ Complete combined search workflow passed")
    
    def test_different_prompt_templates(self):
        """Test different prompt templates"""
        print("\n📝 Testing different prompt templates...")
        
        templates = [
            "You are a professional, formal assistant.",
            "You are a casual, friendly assistant.",
            "You are an academic expert providing detailed analysis.",
            "You are a helpful assistant who uses bullet points."
        ]
        
        for i, template in enumerate(templates):
            payload = {
                "question": "What is SRMU?",
                "system_prompt": template,
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0
            
            print(f"  ✅ Template {i+1} worked correctly")
        
        print("✅ Different prompt templates test passed")
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        print("\n🚨 Testing error handling integration...")
        
        # Test 1: Very long question
        long_question = "What is SRMU? " * 1000
        payload = {
            "question": long_question,
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        assert response.status_code == 200  # Should handle gracefully
        print("  ✅ Long question handled correctly")
        
        # Test 2: Special characters
        special_question = "What is SRMU? 🎓📚✨"
        payload = {
            "question": special_question,
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        assert response.status_code == 200
        print("  ✅ Special characters handled correctly")
        
        # Test 3: Multiple rapid requests
        for i in range(5):
            payload = {
                "question": f"What is SRMU? (Rapid test {i+1})",
                "system_prompt": "You are a helpful assistant.",
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            assert response.status_code == 200
        
        print("  ✅ Multiple rapid requests handled correctly")
        
        print("✅ Error handling integration test passed")
    
    def test_data_consistency(self):
        """Test data consistency across multiple requests"""
        print("\n🔄 Testing data consistency...")
        
        # Ask the same question multiple times
        question = "What is SRMU?"
        responses = []
        
        for i in range(5):
            payload = {
                "question": question,
                "system_prompt": "You are ASK_GILLU, the official AI assistant for SRMU.",
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            assert response.status_code == 200
            
            data = response.json()
            responses.append(data["answer"])
        
        # Verify all responses contain key information about SRMU
        for i, response in enumerate(responses):
            assert len(response) > 0
            response_lower = response.lower()
            assert any(keyword in response_lower for keyword in ["srmu", "university", "memorial"])
            print(f"  ✅ Response {i+1} contains consistent information")
        
        print("✅ Data consistency test passed")
    
    def test_security_headers(self):
        """Test security headers and CORS configuration"""
        print("\n🔒 Testing security headers...")
        
        # Test CORS preflight
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{self.BASE_URL}/ask", headers=headers)
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        print("  ✅ CORS headers present")
        
        # Test actual request with CORS
        payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.post(f"{self.BASE_URL}/ask", data=payload, headers=headers)
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers
        print("  ✅ CORS working correctly")
        
        print("✅ Security headers test passed")

class TestEndToEndScenarios:
    """
    End-to-end scenarios testing real user workflows
    """
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_student_information_scenario(self):
        """Test scenario: Student asking about university information"""
        print("\n🎓 Testing student information scenario...")
        
        questions = [
            "What is SRMU?",
            "What courses does SRMU offer?",
            "How do I apply to SRMU?",
            "What are the facilities at SRMU?",
            "What is the admission process at SRMU?"
        ]
        
        for i, question in enumerate(questions):
            payload = {
                "question": question,
                "system_prompt": "You are ASK_GILLU, the official AI assistant for SRMU. Be helpful and informative.",
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0
            
            print(f"  ✅ Question {i+1}: {question[:50]}...")
        
        print("✅ Student information scenario passed")
    
    def test_research_assistance_scenario(self):
        """Test scenario: Research assistance with web search"""
        print("\n🔬 Testing research assistance scenario...")
        
        questions = [
            "What is machine learning?",
            "Latest developments in artificial intelligence",
            "Current trends in computer science education",
            "Best practices in software engineering",
            "What is data science?"
        ]
        
        for i, question in enumerate(questions):
            payload = {
                "question": question,
                "system_prompt": "You are a research assistant. Provide comprehensive, well-sourced information.",
                "use_web_search": True
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=30)
            assert response.status_code == 200
            
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0
            
            print(f"  ✅ Question {i+1}: {question[:50]}...")
        
        print("✅ Research assistance scenario passed")
    
    def test_mixed_mode_scenario(self):
        """Test scenario: Mixed document and web search usage"""
        print("\n🔄 Testing mixed mode scenario...")
        
        # Document-only questions
        doc_questions = [
            ("What is SRMU?", False),
            ("What courses does SRMU offer?", False),
        ]
        
        # Web search questions
        web_questions = [
            ("What is artificial intelligence?", True),
            ("Current trends in higher education", True),
        ]
        
        # Combined questions
        combined_questions = [
            ("How does SRMU compare to other universities in India?", True),
            ("What are the latest developments in computer science education that SRMU might offer?", True),
        ]
        
        all_questions = doc_questions + web_questions + combined_questions
        
        for i, (question, use_web) in enumerate(all_questions):
            payload = {
                "question": question,
                "system_prompt": "You are ASK_GILLU. Provide helpful, accurate information.",
                "use_web_search": use_web
            }
            
            timeout = 30 if use_web else 10
            response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=timeout)
            assert response.status_code == 200
            
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0
            
            mode = "Combined" if use_web else "Document"
            print(f"  ✅ Question {i+1} ({mode}): {question[:50]}...")
        
        print("✅ Mixed mode scenario passed")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
