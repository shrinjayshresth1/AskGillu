#!/usr/bin/env python3
"""
ASK_GILLU Test Runner
Run comprehensive tests for the ASK_GILLU application
"""

import subprocess
import sys
import os
import time
import requests
from typing import List, Dict, Any
import argparse

class TestRunner:
    """Test runner for ASK_GILLU application"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        
    def check_backend_status(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def install_test_dependencies(self):
        """Install test dependencies"""
        print("📦 Installing test dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                os.path.join("tests", "requirements.txt")
            ], check=True)
            print("✅ Test dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return False
        
        return True
    
    def run_test_suite(self, test_file: str, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        print(f"\n🧪 Running {suite_name}...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                f"tests/{test_file}",
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=600)
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            test_result = {
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if success:
                print(f"✅ {suite_name} passed ({duration:.2f}s)")
            else:
                print(f"❌ {suite_name} failed ({duration:.2f}s)")
                if result.stderr:
                    print(f"Error: {result.stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {suite_name} timed out")
            return {
                'success': False,
                'duration': 600,
                'stdout': '',
                'stderr': 'Test timed out',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ {suite_name} failed with exception: {e}")
            return {
                'success': False,
                'duration': 0,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
    
    def run_all_tests(self, skip_slow: bool = False):
        """Run all test suites"""
        print("🚀 Starting ASK_GILLU Test Suite")
        print("=" * 50)
        
        # Check if backend is running
        if not self.check_backend_status():
            print("❌ Backend is not running. Please start it first:")
            print("   cd frontend-react && npm run dev")
            return False
        
        print("✅ Backend is running and ready")
        
        # Install dependencies
        if not self.install_test_dependencies():
            return False
        
        # Test suites to run
        test_suites = [
            ("test_unit_components.py", "Unit Tests"),
            ("test_backend_api.py", "Backend API Tests"),
            ("test_integration.py", "Integration Tests"),
        ]
        
        if not skip_slow:
            test_suites.append(("test_performance_load.py", "Performance & Load Tests"))
        
        # Run each test suite
        total_duration = 0
        passed_suites = 0
        
        for test_file, suite_name in test_suites:
            result = self.run_test_suite(test_file, suite_name)
            self.test_results[suite_name] = result
            
            total_duration += result['duration']
            if result['success']:
                passed_suites += 1
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for suite_name, result in self.test_results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"{suite_name:<30} {status:<10} ({result['duration']:.2f}s)")
        
        print(f"\nTotal Duration: {total_duration:.2f}s")
        print(f"Passed: {passed_suites}/{len(test_suites)} suites")
        
        overall_success = passed_suites == len(test_suites)
        
        if overall_success:
            print("\n🎉 All tests passed! ASK_GILLU is ready for deployment.")
        else:
            print(f"\n⚠️  {len(test_suites) - passed_suites} test suite(s) failed. Please review and fix issues.")
        
        return overall_success
    
    def run_specific_test(self, test_name: str):
        """Run a specific test"""
        test_map = {
            "unit": ("test_unit_components.py", "Unit Tests"),
            "api": ("test_backend_api.py", "Backend API Tests"),
            "integration": ("test_integration.py", "Integration Tests"),
            "performance": ("test_performance_load.py", "Performance & Load Tests"),
        }
        
        if test_name.lower() not in test_map:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
            return False
        
        test_file, suite_name = test_map[test_name.lower()]
        
        print(f"🚀 Running {suite_name}")
        print("=" * 50)
        
        if not self.check_backend_status():
            print("❌ Backend is not running. Please start it first.")
            return False
        
        if not self.install_test_dependencies():
            return False
        
        result = self.run_test_suite(test_file, suite_name)
        
        if result['success']:
            print(f"\n🎉 {suite_name} completed successfully!")
        else:
            print(f"\n❌ {suite_name} failed. Please review the output above.")
        
        return result['success']

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ASK_GILLU Test Runner')
    parser.add_argument('--test', '-t', 
                       help='Run specific test (unit, api, integration, performance)')
    parser.add_argument('--skip-slow', '-s', action='store_true',
                       help='Skip slow tests (performance tests)')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run only quick tests (unit and api)')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.test:
        success = runner.run_specific_test(args.test)
    elif args.quick:
        # Run only quick tests
        test_suites = [
            ("test_unit_components.py", "Unit Tests"),
            ("test_backend_api.py", "Backend API Tests"),
        ]
        
        print("🚀 Running Quick Test Suite")
        print("=" * 50)
        
        if not runner.check_backend_status():
            print("❌ Backend is not running. Please start it first.")
            return
        
        if not runner.install_test_dependencies():
            return
        
        passed = 0
        for test_file, suite_name in test_suites:
            result = runner.run_test_suite(test_file, suite_name)
            if result['success']:
                passed += 1
        
        success = passed == len(test_suites)
        print(f"\n🎯 Quick tests: {passed}/{len(test_suites)} passed")
        
    else:
        success = runner.run_all_tests(skip_slow=args.skip_slow)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
