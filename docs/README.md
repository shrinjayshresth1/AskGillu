# CAG Documentation Index

Welcome to the CAG (Conversational AI Gateway) documentation. This comprehensive guide covers all aspects of the system, from basic setup to advanced development.

## 📋 Table of Contents

### 🚀 Getting Started
- [Main README](../README.md) - Project overview and quick start guide
- [Complete Document Guide](guides/COMPLETE_DOCUMENT_GUIDE.md) - Comprehensive setup instructions
- [Testing Guide](guides/TESTING_GUIDE.md) - How to run and write tests

### ✨ Features
- [Web Search Feature](features/WEB_SEARCH_FEATURE.md) - Search functionality documentation
- [Web Scraping Feature](features/WEB_SCRAPING_FEATURE.md) - Web content extraction
- [Auto Scraping Feature](features/AUTO_SCRAPING_FEATURE.md) - Automated content collection
- [Website Restriction Feature](features/WEBSITE_RESTRICTION_FEATURE.md) - Content filtering and restrictions

### 🛠️ Development
- [Security Guidelines](development/SECURITY.md) - Security best practices
- [Backend Architecture](../backend/docs/RESTRUCTURING_GUIDE.md) - Backend structure and organization
- [PDF Parser Enhancement](../backend/docs/PDF_PARSER_ENHANCEMENT.md) - Advanced PDF processing
- [Re-chunking Analysis](../backend/docs/RECHUNKING_ANALYSIS.md) - Document processing optimization
- [Add Documents Guide](../backend/docs/ADD_DOCUMENTS_GUIDE.md) - Document management

### 🏗️ Architecture Overview

```
CAG System Architecture
├── Frontend (React)
│   ├── Modern UI with glass-morphism design
│   ├── Real-time backend health checking
│   └── Interactive chat interface
├── Backend (FastAPI)
│   ├── Core functionality (Vector DB, Search, PDF parsing)
│   ├── Services (Web scraping, Document management)
│   ├── API endpoints (Chat, Documents, Scraper)
│   └── Configuration management
└── AI/ML Components
    ├── Vector databases (Qdrant Cloud, FAISS)
    ├── Hybrid search (BM25 + Vector similarity)
    ├── Multi-parser PDF processing
    └── LLM integration (Groq)
```

### 🎯 Key Features Summary

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Advanced PDF Processing** | Multi-parser system with 65+ char improvement | [PDF Parser Enhancement](../backend/docs/PDF_PARSER_ENHANCEMENT.md) |
| **Hybrid Search** | 30% BM25 + 70% Vector similarity | [Backend Architecture](../backend/docs/RESTRUCTURING_GUIDE.md) |
| **Vector Databases** | Qdrant Cloud and FAISS support | [Re-chunking Analysis](../backend/docs/RECHUNKING_ANALYSIS.md) |
| **Web Scraping** | Intelligent content extraction | [Web Scraping Feature](features/WEB_SCRAPING_FEATURE.md) |
| **Auto Scraping** | Automated content collection | [Auto Scraping Feature](features/AUTO_SCRAPING_FEATURE.md) |
| **Modern UI** | React with glass-morphism design | [Main README](../README.md) |

### 📚 Quick Navigation

#### For Users
1. Start with [Main README](../README.md) for quick setup
2. Read [Complete Document Guide](guides/COMPLETE_DOCUMENT_GUIDE.md) for detailed instructions
3. Check [Testing Guide](guides/TESTING_GUIDE.md) to verify your installation

#### For Developers
1. Review [Backend Architecture](../backend/docs/RESTRUCTURING_GUIDE.md) for system understanding
2. Check [Security Guidelines](development/SECURITY.md) before contributing
3. Read feature documentation for specific functionality

#### For System Administrators
1. Study [Security Guidelines](development/SECURITY.md) for deployment
2. Review [Web Scraping Feature](features/WEB_SCRAPING_FEATURE.md) for content policies
3. Check [Website Restriction Feature](features/WEBSITE_RESTRICTION_FEATURE.md) for access controls

### 🔧 API Documentation

When the backend is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **API Schema**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/status

### 🤝 Contributing

Before contributing, please read:
1. [Security Guidelines](development/SECURITY.md)
2. [Backend Architecture](../backend/docs/RESTRUCTURING_GUIDE.md)
3. [Testing Guide](guides/TESTING_GUIDE.md)

### 📞 Support

For issues and questions:
- Check the [Testing Guide](guides/TESTING_GUIDE.md) for troubleshooting
- Review the relevant feature documentation
- Create an issue in the project repository

---

**Last Updated**: September 14, 2025  
**Version**: 1.0.0  
**Maintained by**: CAG Team