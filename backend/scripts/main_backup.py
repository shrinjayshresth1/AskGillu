from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from pypdf import PdfReader
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import json
from typing import Optional

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FAISS_PATH = 'vectorstore/db_faiss'

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please check your .env file.")

# Configuration - Specify which documents to use for ASK_GILLU
# Add or remove documents from this list as needed
ALLOWED_DOCUMENTS = [
    "Questions[1] (1).pdf",
    "Shrinjay Shresth Resume DataScience.pdf",
    "Web-Based-GIS.pdf"
    # Add more document filenames here as needed
    # "Another_Document.pdf",
]

# Configuration - Specify which websites to search from (optional)
# If this list is empty, all websites will be searched
# If populated, only these domains will be searched
ALLOWED_WEBSITES = [
    # Educational and academic websites
    "wikipedia.org",
    "edu",  # This will match any .edu domain
    "scholar.google.com",
    "researchgate.net",
    "arxiv.org",
    "ieee.org",
    "acm.org",
    
    # News and reliable sources
    "bbc.com",
    "reuters.com",
    "nature.com",
    "science.org",
    
    # Government and official sources
    "gov",  # This will match any .gov domain
    "who.int",
    "un.org",
    
    # Technology and documentation
    "stackoverflow.com",
    "github.com",
    "docs.python.org",
    "developer.mozilla.org"
    
    # Add more trusted websites here as needed
    # "example.com",
    # "trusted-source.org"
]

def initialize_documents():
    """Initialize the vector store with specific documents from the allowed list"""
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    
    # Check if the directory exists
    if not os.path.exists(docs_dir):
        print(f"Documents directory not found: {docs_dir}")
        return
    
    print("📚 Initializing documents...")
    
    all_texts = []
    processed_files = []
    skipped_files = []
    
    for doc_name in ALLOWED_DOCUMENTS:
        file_path = os.path.join(docs_dir, doc_name)
        
        print(f"📄 Processing document: {doc_name}")
        
        if os.path.exists(file_path):
            try:
                reader = PdfReader(file_path)
                raw_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        raw_text += text
                
                if raw_text.strip():
                    text_splitter = RecursiveCharacterTextSplitter(
                        separators=["\n\n", "\n", " ", ""],
                        chunk_size=10000,
                        chunk_overlap=1000,
                        length_function=len
                    )
                    texts = text_splitter.split_text(raw_text)
                    all_texts.extend(texts)
                    processed_files.append(doc_name)
                    print(f"   Successfully processed {len(texts)} chunks from {doc_name}")
                else:
                    print(f"   No text content found in {doc_name}")
                    skipped_files.append(doc_name)
            except Exception as e:
                print(f"   Error processing {doc_name}: {str(e)}")
                skipped_files.append(doc_name)
        else:
            print(f"   Document not found: {file_path}")
            skipped_files.append(doc_name)
    
    if all_texts:
        # Create embeddings and vector store
        print(f"Creating embeddings and vector store...")
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                           model_kwargs={'device': 'cpu'})
        vectorstore = FAISS.from_texts(all_texts, embeddings)
        
        # Create vectorstore directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)
        vectorstore.save_local(DB_FAISS_PATH)
        
        print(f"Successfully processed {len(processed_files)} documents: {', '.join(processed_files)}")
        print(f"Created vector store with {len(all_texts)} text chunks")
        
        if skipped_files:
            print(f"Skipped {len(skipped_files)} documents: {', '.join(skipped_files)}")
            
    else:
        print("No text content found in any specified documents!")
        if skipped_files:
            print(f"   All {len(skipped_files)} documents were skipped or not found")
        
        # Show available documents in docs folder for reference
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        available_docs = glob.glob(os.path.join(docs_dir, "*.pdf"))
        if available_docs:
            print("📁 Available documents in docs folder:")
            for doc in available_docs:
                print(f"   - {os.path.basename(doc)}")
        else:
            print("📁 No PDF documents found in docs folder!")

@app.on_event("startup")
async def startup_event():
    """Initialize documents when the server starts"""
    initialize_documents()

@app.get("/")
async def root():
    """Root endpoint to check if documents are loaded"""
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                           model_kwargs={'device': 'cpu'})
        vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        return {
            "message": "ASK_GILLU is ready with SRMU documents loaded!", 
            "status": "ready",
            "configured_documents": ALLOWED_DOCUMENTS,
            "total_documents": len(ALLOWED_DOCUMENTS),
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0
        }
    except Exception as e:
        return {
            "message": "Documents not loaded yet", 
            "status": "not_ready", 
            "error": str(e),
            "configured_documents": ALLOWED_DOCUMENTS,
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0
        }

@app.get("/status")
async def get_status():
    """Get system status"""
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                           model_kwargs={'device': 'cpu'})
        vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        return {
            "status": "ready", 
            "message": f"ASK_GILLU is ready to answer questions about SRMU using {len(ALLOWED_DOCUMENTS)} configured documents!",
            "configured_documents": ALLOWED_DOCUMENTS,
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0,
            "total_allowed_websites": len(ALLOWED_WEBSITES)
        }
    except Exception as e:
        return {
            "status": "not_ready", 
            "message": f"System not ready: {str(e)}",
            "configured_documents": ALLOWED_DOCUMENTS,
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0
        }

def perform_web_search(query: str, max_results: int = 5) -> str:
    """
    Perform web search using DuckDuckGo and return formatted results
    Only searches from allowed websites if ALLOWED_WEBSITES is configured
    """
    try:
        # If no allowed websites specified, search normally
        if not ALLOWED_WEBSITES:
            search_query = query
        else:
            # Create site-restricted query
            site_restrictions = " OR ".join([f"site:{site}" for site in ALLOWED_WEBSITES])
            search_query = f"{query} ({site_restrictions})"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=max_results))
            
        if not results:
            if ALLOWED_WEBSITES:
                return f"No web search results found for this query from allowed websites: {', '.join(ALLOWED_WEBSITES[:5])}{'...' if len(ALLOWED_WEBSITES) > 5 else ''}"
            else:
                return "No web search results found for this query."
            
        # Filter results to ensure they're from allowed websites (double-check)
        if ALLOWED_WEBSITES:
            filtered_results = []
            for result in results:
                url = result.get('href', '')
                # Check if the URL contains any of the allowed domains
                if any(allowed_site in url for allowed_site in ALLOWED_WEBSITES):
                    filtered_results.append(result)
            results = filtered_results
            
        if not results:
            return f"No results found from allowed websites: {', '.join(ALLOWED_WEBSITES[:5])}{'...' if len(ALLOWED_WEBSITES) > 5 else ''}"
            
        # Format results for the AI to use
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""
Result {i}:
Title: {result.get('title', 'No title')}
URL: {result.get('href', 'No URL')}
Content: {result.get('body', 'No content')}
"""
            formatted_results.append(formatted_result)
            
        # Add information about search restrictions if applicable
        search_info = ""
        if ALLOWED_WEBSITES:
            search_info = f"\n[Search limited to trusted websites: {', '.join(ALLOWED_WEBSITES[:3])}{'...' if len(ALLOWED_WEBSITES) > 3 else ''}]\n"
            
        return search_info + "\n".join(formatted_results)
        
    except Exception as e:
        return f"Web search error: {str(e)}"

def combine_sources(question: str, system_prompt: str, use_web_search: bool = False) -> str:
    """
    Combine document search and web search results
    """
    context_parts = []
    
    # Always include document-based context if available
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                         model_kwargs={'device': 'cpu'})
        vectorstore = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        
        # Get relevant documents
        docs = vectorstore.similarity_search(question, k=3)
        if docs:
            doc_context = "\n\n".join([doc.page_content for doc in docs])
            context_parts.append(f"UNIVERSITY DOCUMENTS:\n{doc_context}")
    except Exception as e:
        print(f"Error loading documents: {e}")
    
    # Add web search results if requested
    if use_web_search:
        web_results = perform_web_search(question)
        if web_results and "No web search results found" not in web_results:
            context_parts.append(f"WEB SEARCH RESULTS:\n{web_results}")
    
    # Combine all context
    combined_context = "\n\n" + "="*50 + "\n\n".join(context_parts) if context_parts else ""
    
    return combined_context

@app.post("/ask")
async def ask_question(
    question: str = Form(...),
    system_prompt: str = Form("You are ASK_GILLU, an AI assistant for SRMU (Shri Ramswaroop Memorial University). Answer questions based on the provided documents and be helpful and accurate."),
    use_web_search: bool = Form(False)
):
    """Answer questions based on documents with optional web search"""
    try:
        # Get context from documents and optionally web search
        context = combine_sources(question, system_prompt, use_web_search)
        
        # Create the full prompt
        full_prompt = f"""
{system_prompt}

{context}

Question: {question}

Please provide a comprehensive answer based on the available information above. If using web search results, prioritize university documents but supplement with web information where helpful.
"""
        
        # Initialize the language model
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            groq_api_key=GROQ_API_KEY
        )
        
        # Get response from the model
        response = llm.invoke(full_prompt)
        
        return {
            "answer": response.content,
            "sources_used": {
                "documents": True,
                "web_search": use_web_search,
                "web_search_restricted": len(ALLOWED_WEBSITES) > 0 if use_web_search else False
            }
        }
        
    except Exception as e:
        return {"error": f"Error processing question: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
