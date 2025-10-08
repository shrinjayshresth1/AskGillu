"""
Integration test for Advanced RAG features
"""

import requests
import json
import time
from typing import Dict, Any

class AdvancedRAGTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_enhanced_ask_endpoint(self):
        """Test the enhanced /ask endpoint with advanced RAG features"""
        print("🔍 Testing enhanced /ask endpoint...")
        
        payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are ASK_GILLU, an AI assistant for SRMU.",
            "use_web_search": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/ask", data=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for new advanced RAG metadata
                if "advanced_rag_features" in data:
                    features = data["advanced_rag_features"]
                    print(f"✅ Advanced RAG features detected:")
                    print(f"   - Documents found: {features.get('documents_found', 0)}")
                    print(f"   - Cache hit: {features.get('cache_hit', False)}")
                    print(f"   - Semantic chunks used: {features.get('semantic_chunks_used', False)}")
                    print(f"   - Results reranked: {features.get('results_reranked', False)}")
                    print(f"   - Response time: {features.get('response_time_ms', 0)}ms")
                    
                    self.test_results.append({
                        "test": "enhanced_ask_endpoint",
                        "status": "passed",
                        "features": features
                    })
                else:
                    print("⚠️ Advanced RAG features not found in response")
                    self.test_results.append({
                        "test": "enhanced_ask_endpoint", 
                        "status": "partial",
                        "message": "Missing advanced RAG metadata"
                    })
                
                return True
            else:
                print(f"❌ Request failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing ask endpoint: {e}")
            return False
    
    def test_feedback_endpoint(self):
        """Test the feedback submission endpoint"""
        print("\n📝 Testing feedback endpoint...")
        
        payload = {
            "question": "What is SRMU?",
            "rating": 5,
            "feedback_type": "rating",
            "comment": "Test feedback from integration test",
            "was_helpful": True
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/feedback", data=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Feedback submission successful")
                    print(f"   - Feedback ID: {data.get('feedback_id', 'N/A')}")
                    self.test_results.append({
                        "test": "feedback_endpoint",
                        "status": "passed"
                    })
                    return True
                else:
                    print(f"❌ Feedback submission failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Feedback endpoint returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing feedback endpoint: {e}")
            return False
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("\n📊 Testing analytics endpoints...")
        
        endpoints = [
            "/api/analytics/performance",
            "/api/analytics/feedback", 
            "/api/cache/stats",
            "/api/recommendations"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ {endpoint} - Working")
                        results.append(True)
                    else:
                        print(f"⚠️ {endpoint} - Response indicates failure")
                        results.append(False)
                else:
                    print(f"❌ {endpoint} - Status {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                results.append(False)
        
        if all(results):
            self.test_results.append({
                "test": "analytics_endpoints",
                "status": "passed"
            })
            return True
        else:
            self.test_results.append({
                "test": "analytics_endpoints",
                "status": "partial"
            })
            return False
    
    def test_cache_functionality(self):
        """Test response caching by making identical queries"""
        print("\n💾 Testing cache functionality...")
        
        payload = {
            "question": "Test cache query - What courses does SRMU offer?",
            "system_prompt": "You are ASK_GILLU, an AI assistant for SRMU.",
            "use_web_search": False
        }
        
        try:
            # First query (should be cache miss)
            start_time = time.time()
            response1 = requests.post(f"{self.base_url}/ask", data=payload, timeout=30)
            time1 = time.time() - start_time
            
            if response1.status_code != 200:
                print("❌ First query failed")
                return False
            
            # Wait a moment then make same query (should be cache hit)
            time.sleep(1)
            start_time = time.time()
            response2 = requests.post(f"{self.base_url}/ask", data=payload, timeout=30)
            time2 = time.time() - start_time
            
            if response2.status_code != 200:
                print("❌ Second query failed")
                return False
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Check if second query was faster (indicating cache hit)
            if "advanced_rag_features" in data2:
                cache_hit = data2["advanced_rag_features"].get("cache_hit", False)
                if cache_hit:
                    print(f"✅ Cache hit detected on second query")
                    print(f"   - First query: {time1:.2f}s")
                    print(f"   - Second query: {time2:.2f}s")
                    self.test_results.append({
                        "test": "cache_functionality",
                        "status": "passed",
                        "cache_hit": True
                    })
                    return True
                else:
                    print(f"⚠️ Cache miss on second query (might be expected)")
                    self.test_results.append({
                        "test": "cache_functionality",
                        "status": "partial"
                    })
                    return False
            else:
                print("⚠️ Advanced RAG features not available for cache testing")
                return False
                
        except Exception as e:
            print(f"❌ Error testing cache functionality: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Advanced RAG Integration Tests")
        print("=" * 50)
        
        tests = [
            self.test_enhanced_ask_endpoint,
            self.test_feedback_endpoint,
            self.test_analytics_endpoints,
            self.test_cache_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All advanced RAG features are working correctly!")
        elif passed > 0:
            print("⚠️ Some advanced RAG features may need attention")
        else:
            print("❌ Advanced RAG features are not working")
        
        return passed, total, self.test_results

def main():
    """Main test function"""
    tester = AdvancedRAGTester()
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend returned error status")
            return
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("Please start the backend first: python main.py")
        return
    
    # Run tests
    passed, total, results = tester.run_all_tests()
    
    # Save results
    with open("advanced_rag_test_results.json", "w") as f:
        json.dump({
            "timestamp": time.time(),
            "passed": passed,
            "total": total,
            "results": results
        }, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: advanced_rag_test_results.json")

if __name__ == "__main__":
    main()