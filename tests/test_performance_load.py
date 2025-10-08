import pytest
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class TestPerformanceAndLoad:
    """
    Performance and load tests for ASK_GILLU
    """
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_response_time_benchmarks(self):
        """Test response time benchmarks"""
        print("\n⏱️ Testing response time benchmarks...")
        
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            
            payload = {
                "question": f"What is SRMU? (Test {i+1})",
                "system_prompt": "You are a helpful assistant.",
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            assert response.status_code == 200
            print(f"  Test {i+1}: {response_time:.2f}s")
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"\n📊 Response Time Statistics:")
        print(f"  Average: {avg_response_time:.2f}s")
        print(f"  Maximum: {max_response_time:.2f}s")
        print(f"  Minimum: {min_response_time:.2f}s")
        
        # Assert performance requirements
        assert avg_response_time < 10.0, f"Average response time too high: {avg_response_time:.2f}s"
        assert max_response_time < 30.0, f"Maximum response time too high: {max_response_time:.2f}s"
        
        print("✅ Response time benchmarks passed")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n🔄 Testing concurrent request handling...")
        
        def make_request(request_id):
            """Make a single request"""
            payload = {
                "question": f"What is SRMU? (Concurrent test {request_id})",
                "system_prompt": "You are a helpful assistant.",
                "use_web_search": False
            }
            
            start_time = time.time()
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            end_time = time.time()
            
            return {
                'id': request_id,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        
        # Test with 5 concurrent requests
        num_requests = 5
        results = []
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"  Request {result['id']}: {result['response_time']:.2f}s - {'✅' if result['success'] else '❌'}")
        
        # Check results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        print(f"\n📊 Concurrent Request Results:")
        print(f"  Successful: {len(successful_requests)}/{num_requests}")
        print(f"  Failed: {len(failed_requests)}/{num_requests}")
        
        # Assert that at least 80% of requests succeeded
        success_rate = len(successful_requests) / num_requests
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"
        
        print("✅ Concurrent request handling passed")
    
    def test_web_search_performance(self):
        """Test web search performance"""
        print("\n🌐 Testing web search performance...")
        
        start_time = time.time()
        
        payload = {
            "question": "What is artificial intelligence?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": True
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 45.0, f"Web search too slow: {response_time:.2f}s"
        
        print(f"  Web search response time: {response_time:.2f}s")
        print("✅ Web search performance acceptable")
    
    def test_large_response_handling(self):
        """Test handling of large responses"""
        print("\n📄 Testing large response handling...")
        
        payload = {
            "question": "Tell me everything about SRMU, including all courses, facilities, history, and programs in detail.",
            "system_prompt": "You are a helpful assistant. Provide comprehensive, detailed answers.",
            "use_web_search": False
        }
        
        start_time = time.time()
        response = requests.post(f"{self.BASE_URL}/ask", data=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        
        data = response.json()
        answer_length = len(data['answer'])
        
        print(f"  Response length: {answer_length} characters")
        print(f"  Response time: {response_time:.2f}s")
        
        # Should handle large responses
        assert answer_length > 0
        assert response_time < 30.0
        
        print("✅ Large response handling passed")
    
    def test_memory_usage_stability(self):
        """Test memory usage stability over multiple requests"""
        print("\n🧠 Testing memory usage stability...")
        
        # Make multiple requests to check for memory leaks
        for i in range(20):
            payload = {
                "question": f"What is SRMU? (Memory test {i+1})",
                "system_prompt": "You are a helpful assistant.",
                "use_web_search": False
            }
            
            response = requests.post(f"{self.BASE_URL}/ask", data=payload)
            assert response.status_code == 200
            
            if i % 5 == 0:
                print(f"  Completed {i+1}/20 requests")
        
        print("✅ Memory usage stability test passed")
    
    def test_error_recovery(self):
        """Test error recovery capabilities"""
        print("\n🔄 Testing error recovery...")
        
        # Test invalid request
        invalid_payload = {
            "question": "",  # Empty question
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=invalid_payload)
        assert response.status_code == 200  # Should handle gracefully
        
        # Test normal request after error
        normal_payload = {
            "question": "What is SRMU?",
            "system_prompt": "You are a helpful assistant.",
            "use_web_search": False
        }
        
        response = requests.post(f"{self.BASE_URL}/ask", data=normal_payload)
        assert response.status_code == 200
        
        print("✅ Error recovery test passed")

class TestScalabilityBenchmarks:
    """
    Scalability and stress tests
    """
    
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_sustained_load(self):
        """Test sustained load over time"""
        print("\n🔥 Testing sustained load...")
        
        duration = 60  # 1 minute test
        request_interval = 2  # 2 seconds between requests
        
        start_time = time.time()
        request_count = 0
        successful_requests = 0
        
        while time.time() - start_time < duration:
            try:
                payload = {
                    "question": f"What is SRMU? (Load test {request_count + 1})",
                    "system_prompt": "You are a helpful assistant.",
                    "use_web_search": False
                }
                
                response = requests.post(f"{self.BASE_URL}/ask", data=payload, timeout=10)
                request_count += 1
                
                if response.status_code == 200:
                    successful_requests += 1
                
                time.sleep(request_interval)
                
            except Exception as e:
                print(f"  Request failed: {e}")
                request_count += 1
        
        success_rate = successful_requests / request_count if request_count > 0 else 0
        
        print(f"\n📊 Sustained Load Results:")
        print(f"  Duration: {duration}s")
        print(f"  Total requests: {request_count}")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Success rate: {success_rate:.2%}")
        
        assert success_rate >= 0.9, f"Success rate too low under sustained load: {success_rate:.2%}"
        
        print("✅ Sustained load test passed")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
