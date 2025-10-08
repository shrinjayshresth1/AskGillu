# Backend Documentation

This directory contains all backend-specific documentation for the CAG (Conversational AI Gateway) system.

## 📁 Documentation Structure

### Core Documentation
- **[RESTRUCTURING_GUIDE.md](RESTRUCTURING_GUIDE.md)** - Complete backend restructuring and architecture
- **[PDF_PARSER_ENHANCEMENT.md](PDF_PARSER_ENHANCEMENT.md)** - Advanced PDF parsing implementation
- **[RECHUNKING_ANALYSIS.md](RECHUNKING_ANALYSIS.md)** - Document processing optimization
- **[ADD_DOCUMENTS_GUIDE.md](ADD_DOCUMENTS_GUIDE.md)** - Document management procedures

## 🏗️ Backend Architecture

```
backend/
├── app/                          # Main application package
│   ├── api/endpoints/            # API route handlers
│   │   ├── chat.py              # Chat and query endpoints
│   │   ├── documents.py         # Document management
│   │   └── scraper.py           # Web scraping endpoints
│   ├── core/                     # Core functionality
│   │   ├── unified_vector_manager.py    # Vector DB management
│   │   ├── hybrid_search.py     # Search implementation
│   │   ├── advanced_pdf_parser.py       # PDF processing
│   │   └── qdrant_manager.py     # Qdrant operations
│   ├── services/                 # Business logic
│   │   ├── web_scraper.py        # Web scraping service
│   │   └── add_documents.py      # Document services
│   ├── models/                   # Data models
│   └── utils/                    # Utility functions
├── config/                       # Configuration
│   └── settings.py              # Centralized settings
├── scripts/                      # Utilities and migration
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
└── docs/                        # This documentation
```

## 🔧 Key Components

### Vector Database Management
- **Unified Interface**: Support for both Qdrant and FAISS
- **Hybrid Search**: BM25 + Vector similarity (30%/70% split)
- **Enhanced Parsing**: Multi-parser PDF processing with pdfminer.six
- **Re-chunking**: Automated document optimization

### API Structure
- **FastAPI Framework**: Modern async Python web framework
- **Modular Endpoints**: Organized by functionality
- **CORS Enabled**: Frontend-backend communication
- **Interactive Docs**: Automatic API documentation

### Configuration Management
- **Environment-based**: Development/production configs
- **Centralized Settings**: Single source of truth
- **Security**: API keys and sensitive data protection

## 🚀 Getting Started

### Development Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Running the Backend
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# All tests
python -m pytest tests/ -v

# Specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

## 📊 Performance Metrics

### PDF Processing
- **Enhanced Extraction**: +65 characters per document with pdfminer.six
- **Multi-parser Support**: Automatic fallback system
- **Quality Improvement**: 6,556 vs 6,491 characters (pdfminer vs PyPDF)

### Search Performance
- **Hybrid Search**: Combines keyword and semantic search
- **Response Time**: Sub-second query responses
- **Accuracy**: Improved relevance with BM25 + Vector combination

### Database Operations
- **Batch Processing**: Efficient document re-chunking
- **Backup System**: Automatic backup before major operations
- **Scalability**: Support for thousands of documents

## 🔗 Related Documentation

### Project-Level Documentation
- [Main README](../../README.md) - Project overview
- [Feature Documentation](../../docs/features/) - Feature-specific guides
- [Development Guidelines](../../docs/development/) - Development standards

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs (when running)
- **API Schema**: http://localhost:8000/redoc (when running)

## 🛠️ Development Guidelines

### Code Organization
- Follow the modular structure outlined in RESTRUCTURING_GUIDE.md
- Use proper import paths for the new package structure
- Maintain separation of concerns between core, services, and API layers

### Testing Standards
- Write unit tests for new functionality
- Include integration tests for API endpoints
- Maintain test coverage above 80%

### Configuration
- Use environment variables for all configurable values
- Never commit sensitive data to version control
- Document all configuration options

## 📈 Recent Improvements

### Version 1.0.0 (September 2025)
- ✅ Complete backend restructuring
- ✅ Enhanced PDF parsing with pdfminer.six
- ✅ Hybrid search implementation
- ✅ Centralized configuration management
- ✅ Comprehensive test suite
- ✅ Professional project structure

## 🤝 Contributing

1. Read the [RESTRUCTURING_GUIDE.md](RESTRUCTURING_GUIDE.md) first
2. Follow the established code organization
3. Add tests for new functionality
4. Update documentation for changes
5. Use the configuration system for all settings

---

**Maintained by**: CAG Development Team  
**Last Updated**: September 14, 2025