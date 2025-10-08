#!/usr/bin/env python3

import requests
import json

def test_api():
    print("Testing ASK_GILLU API...")
    
    # Test status endpoint
    try:
        response = requests.get("http://localhost:8000/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"Status test failed: {e}")
        return
    
    # Test ask endpoint
    try:
        data = {
            "question": "How do I check my admission status?",
            "system_prompt": "You are ASK_GILLU, an AI assistant for SRMU. Answer based on the provided documents.",
            "use_web_search": False
        }
        
        response = requests.post("http://localhost:8000/ask", data=data)
        print(f"Ask endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result.get('answer', 'No answer found')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Ask test failed: {e}")

if __name__ == "__main__":
    test_api()