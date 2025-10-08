# 🚀 COMPLETE GUIDE: Adding Documents to Both Vector Databases

## 📋 Summary
Your system automatically handles adding documents to **BOTH** Qdrant and FAISS databases. No matter which database you're currently using, new documents get added properly!

## 🛠️ 4 Ways to Add Documents

### 1. 📁 Script Method (Recommended)
```bash
cd backend
python add_documents.py
```
This interactive script helps you:
- Add single PDF files
- Add multiple text documents  
- Bulk add entire folders of PDFs
- See real-time status updates

### 2. 🌐 API Method (Upload Files)
```bash
# Upload a PDF file via API
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@path/to/your/document.pdf" \
  -F "title=My Document" \
  -F "category=uploaded"

# Add text content directly
curl -X POST "http://localhost:8000/api/documents/add-text" \
  -F "content=Your document text here..." \
  -F "title=My Text Document" \
  -F "source=manual_entry"
```

### 3. 💻 Python Code Method
```python
from unified_vector_manager import get_unified_manager

# Initialize the manager
vm = get_unified_manager()

# Method A: Add PDF with advanced parsing
success = vm.add_pdf("path/to/document.pdf")

# Method B: Add text documents
texts = ["Document content here"]
metadatas = [{"title": "My Doc", "source": "manual"}]
success = vm.add_documents(texts, metadatas)

# Check status
status = vm.get_status()
print(f"Total documents: {status['documents_count']}")
```

### 4. 📂 Automatic Method (For Developers)
Add documents to the auto-load list in `main.py`:
```python
DOCUMENT_NAMES = [
    "existing_doc1.pdf",
    "existing_doc2.pdf", 
    "your_new_document.pdf"  # Add here
]
```

## 🔄 What Happens Automatically

When you add ANY document:

✅ **Advanced PDF Parsing** - Uses PyMuPDF, pdfplumber, or OCR  
✅ **Smart Database Routing** - Goes to your current database (Qdrant OR FAISS)  
✅ **Hybrid Search Update** - BM25 index updated for better search  
✅ **Auto-Save** - FAISS saves to disk, Qdrant syncs to cloud  
✅ **Metadata Management** - Title, source, timestamp added automatically  

## 🎯 Real Example

Let's add a new document right now!