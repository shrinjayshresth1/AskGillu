# 📄 ADDING NEW DOCUMENTS TO VECTOR DATABASES

## Quick Answer: Use the Unified API!

Your system already handles adding documents to BOTH databases automatically. Here's how:

```python
from unified_vector_manager import get_unified_manager

# Get the manager (it knows which DB you're using)
vm = get_unified_manager()

# Method 1: Add a PDF file (uses advanced parsing automatically)
success = vm.add_pdf("path/to/your/new_document.pdf")

# Method 2: Add text directly
texts = ["Your document content here"]
metadatas = [{"source": "manual_entry", "title": "My Document"}]
success = vm.add_documents(texts, metadatas)
```

## Step-by-Step Process

### 1. Adding a PDF Document

```python
# Example: Adding a new PDF to your system
from unified_vector_manager import get_unified_manager

vm = get_unified_manager()

# Add PDF - automatically uses advanced parsing
pdf_path = "C:/path/to/new_document.pdf"
success = vm.add_pdf(pdf_path)

if success:
    print("✅ PDF added to both vector databases!")
else:
    print("❌ Failed to add PDF")
```

### 2. Adding Multiple Documents

```python
# Example: Adding multiple text documents
texts = [
    "Document 1 content here...",
    "Document 2 content here...",
    "Document 3 content here..."
]

metadatas = [
    {"source": "doc1.txt", "category": "FAQ"},
    {"source": "doc2.txt", "category": "Policy"},
    {"source": "doc3.txt", "category": "Guide"}
]

success = vm.add_documents(texts, metadatas)
```

### 3. What Happens Automatically

When you add documents, the system automatically:

1. **Parses PDFs** using advanced multi-parser (PyMuPDF, pdfplumber, etc.)
2. **Adds to current database** (Qdrant OR FAISS based on your toggle)
3. **Updates hybrid search** with new documents for BM25
4. **Saves FAISS** to disk (if using FAISS)
5. **Syncs Qdrant** to cloud (if using Qdrant)

## Complete Example Script

Let me create a script you can use: