# ASK_GILLU Testing Guide

## 🧪 **Comprehensive Test Suite**

This testing module provides comprehensive Quality Assurance (QA) testing for the ASK_GILLU application, covering all aspects from unit tests to performance benchmarks.

## 📋 **Test Categories**

### **1. Unit Tests** (`test_unit_components.py`)
- **Web Search Function**: Tests DuckDuckGo search integration
- **Source Combination**: Tests merging document and web results
- **Document Initialization**: Tests PDF processing and vector store creation
- **Environment Variables**: Tests configuration loading
- **Error Handling**: Tests graceful error handling

### **2. Backend API Tests** (`test_backend_api.py`)
- **Status Endpoint**: Tests `/status` endpoint
- **Question Answering**: Tests `/ask` endpoint with various scenarios
- **Document Search**: Tests document-only search functionality
- **Web Search**: Tests web search integration
- **Combined Search**: Tests document + web search
- **Error Scenarios**: Tests error handling (empty questions, timeouts)
- **CORS Configuration**: Tests cross-origin resource sharing
- **Performance**: Tests response times and throughput

### **3. Frontend Component Tests** (`test_frontend_components.js`)
- **UI Rendering**: Tests React component rendering
- **Web Search Toggle**: Tests toggle functionality
- **Form Submission**: Tests form data submission
- **API Integration**: Tests frontend-backend communication
- **State Management**: Tests React state updates
- **Error Handling**: Tests frontend error display
- **User Interactions**: Tests user workflow scenarios

### **4. Integration Tests** (`test_integration.py`)
- **End-to-End Workflows**: Tests complete user scenarios
- **Document Search Flow**: Tests full document search process
- **Web Search Flow**: Tests full web search process
- **Combined Search Flow**: Tests mixed search scenarios
- **Prompt Templates**: Tests different AI response styles
- **Data Consistency**: Tests consistent responses
- **Security**: Tests CORS and security headers

### **5. Performance & Load Tests** (`test_performance_load.py`)
- **Response Time Benchmarks**: Tests response time requirements
- **Concurrent Requests**: Tests handling multiple simultaneous requests
- **Web Search Performance**: Tests web search response times
- **Large Response Handling**: Tests handling of large answers
- **Memory Stability**: Tests for memory leaks
- **Sustained Load**: Tests performance under continuous load
- **Error Recovery**: Tests system recovery after errors

## 🚀 **Running Tests**

### **Prerequisites**
1. **Backend Running**: Start ASK_GILLU backend server
   ```bash
   cd frontend-react
   npm run dev
   ```

2. **Install Test Dependencies**:
   ```bash
   pip install -r tests/requirements.txt
   ```

### **Test Execution Options**

#### **1. Run All Tests**
```bash
python run_tests.py
```

#### **2. Run Specific Test Suite**
```bash
# Unit tests only
python run_tests.py --test unit

# API tests only  
python run_tests.py --test api

# Integration tests only
python run_tests.py --test integration

# Performance tests only
python run_tests.py --test performance
```

#### **3. Quick Test Suite** (Unit + API only)
```bash
python run_tests.py --quick
```

#### **4. Skip Slow Tests**
```bash
python run_tests.py --skip-slow
```

#### **5. Run Individual Test Files**
```bash
# Run specific test file
pytest tests/test_backend_api.py -v

# Run with coverage
pytest tests/test_backend_api.py --cov=backend --cov-report=html
```

## 📊 **Test Reports**

### **HTML Reports**
Tests generate HTML reports in `test_reports/`:
- `report.html` - Test execution report
- `coverage/` - Code coverage report

### **Console Output**
```
🧪 Running Backend API Tests...
  ✅ Status endpoint working correctly
  ✅ Document-only search working correctly
  ✅ Web search functionality working correctly
  ✅ Combined search working correctly
  ✅ Custom system prompt working correctly

📊 TEST SUMMARY
Backend API Tests          ✅ PASSED    (12.34s)
Unit Tests                ✅ PASSED    (8.76s)
Integration Tests         ✅ PASSED    (15.43s)
Performance Tests         ✅ PASSED    (45.67s)

🎉 All tests passed! ASK_GILLU is ready for deployment.
```

## 🎯 **Test Scenarios**

### **Document Search Scenarios**
- ✅ "What is SRMU?" → University information
- ✅ "What courses does SRMU offer?" → Course listings
- ✅ "SRMU admission process?" → Admission details
- ✅ Empty question handling
- ✅ Special characters in questions
- ✅ Very long questions

### **Web Search Scenarios**
- ✅ "What is artificial intelligence?" → Current AI information
- ✅ "Latest developments in technology" → Recent tech news
- ✅ "Current trends in education" → Educational trends
- ✅ Network error handling
- ✅ No search results handling

### **Combined Search Scenarios**
- ✅ "How does SRMU compare to other universities?" → Mixed sources
- ✅ "SRMU computer science vs industry trends" → Document + web
- ✅ "SRMU facilities and modern university standards" → Combined info

### **Performance Scenarios**
- ✅ Response time < 10 seconds (average)
- ✅ Response time < 30 seconds (maximum)
- ✅ 5 concurrent requests handling
- ✅ Web search within 45 seconds
- ✅ Memory stability over 20 requests
- ✅ Sustained load for 1 minute

## 🔍 **Quality Assurance Checklist**

### **Before Deployment**
- [ ] All unit tests pass
- [ ] All API tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks meet requirements
- [ ] Frontend components render correctly
- [ ] Web search functionality works
- [ ] Document search accuracy verified
- [ ] Error handling works gracefully
- [ ] Security headers configured
- [ ] CORS working correctly

### **Performance Requirements**
- [ ] Average response time < 10 seconds
- [ ] Maximum response time < 30 seconds
- [ ] Web search response time < 45 seconds
- [ ] Concurrent request handling (5+ simultaneous)
- [ ] Memory stability (no leaks)
- [ ] Sustained load handling (1 minute)

### **Functionality Requirements**
- [ ] Document search accuracy
- [ ] Web search integration
- [ ] Combined search results
- [ ] Prompt customization
- [ ] Error messages helpful
- [ ] UI responsive and intuitive
- [ ] API endpoints reliable

## 🛠️ **Troubleshooting Tests**

### **Common Issues**

#### **Backend Not Running**
```
❌ Backend is not running. Please start it first:
   cd frontend-react && npm run dev
```

#### **Test Dependencies Missing**
```bash
pip install -r tests/requirements.txt
```

#### **Test Timeouts**
- Increase timeout values in test configuration
- Check network connectivity for web search tests
- Verify backend performance

#### **Failed Web Search Tests**
- Check internet connectivity
- Verify DuckDuckGo accessibility
- Check for rate limiting

### **Debug Individual Tests**
```bash
# Run with verbose output
pytest tests/test_backend_api.py::TestASKGILLUBackend::test_ask_endpoint_web_search -v -s

# Run with debugging
pytest tests/test_backend_api.py --pdb
```

## 📈 **Test Metrics**

### **Coverage Goals**
- **Backend Code Coverage**: >90%
- **Frontend Component Coverage**: >80%
- **Integration Coverage**: >95%

### **Performance Targets**
- **Response Time**: <10s average, <30s maximum
- **Throughput**: 5+ concurrent requests
- **Reliability**: >99% success rate
- **Memory**: Stable over extended use

### **Quality Metrics**
- **Test Pass Rate**: 100%
- **Code Quality**: No lint errors
- **Security**: All security tests pass
- **Documentation**: Complete test coverage

## 🎉 **Continuous Integration**

### **CI/CD Pipeline**
```yaml
# Example GitHub Actions workflow
name: ASK_GILLU Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r tests/requirements.txt
      - name: Run tests
        run: python run_tests.py --quick
```

This comprehensive test suite ensures ASK_GILLU meets all quality standards before deployment! 🚀
