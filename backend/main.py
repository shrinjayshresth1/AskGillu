from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from pypdf import PdfReader
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import json
from typing import Optional, List, Dict
import uuid
from datetime import datetime

# Import from new structured modules
from app.services.web_scraper import WebScraper
from app.core.unified_vector_manager import get_unified_manager, switch_vector_database
from config.settings import Config, config

# Load environment variables from .env file
load_dotenv()

# Get configuration
app_config = config['default']

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Unified Vector Manager
vector_manager = get_unified_manager()

# Get API key from configuration
GROQ_API_KEY = app_config.GROQ_API_KEY
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please check your .env file.")

# Use configuration from settings
ALLOWED_DOCUMENTS = app_config.ALLOWED_DOCUMENTS
ALLOWED_WEBSITES = app_config.ALLOWED_WEBSITES
AUTO_SCRAPE_WEBSITES = app_config.AUTO_SCRAPE_WEBSITES
AUTO_SCRAPE_CONFIG = app_config.AUTO_SCRAPE_CONFIG
WEB_SCRAPER_CONFIG = app_config.WEB_SCRAPER_CONFIG

def initialize_documents():
    """Initialize the vector store with specific documents from the allowed list"""
    # First check if documents already exist
    try:
        status = vector_manager.get_status()
        existing_count = status.get("documents_count", 0)
        
        if existing_count > 0:
            print(f"[DOCS] Vector database already contains {existing_count} documents. Skipping initialization.")
            print(f"[DOCS] If you want to reload documents, clear the collection first or restart with a fresh database.")
            return
        else:
            print(f"[DOCS] Qdrant collection is empty. Proceeding with document initialization...")
    except Exception as e:
        print(f"[DOCS] Could not check existing documents: {str(e)}. Proceeding with initialization...")
    
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    
    # Check if the directory exists
    if not os.path.exists(docs_dir):
        print(f"Documents directory not found: {docs_dir}")
        return
    
    print("[DOCS] Initializing documents...")
    
    all_texts = []
    processed_files = []
    skipped_files = []
    
    for doc_name in ALLOWED_DOCUMENTS:
        file_path = os.path.join(docs_dir, doc_name)
        
        print(f"[DOCS] Processing document: {doc_name}")
        
        if os.path.exists(file_path):
            try:
                # Use advanced PDF parsing
                raw_text, parsing_metadata = vector_manager.parse_pdf_advanced(file_path, method="hybrid")
                
                if raw_text.strip():
                    # Enhanced text splitting with better parameters
                    text_splitter = RecursiveCharacterTextSplitter(
                        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
                        chunk_size=8000,  # Slightly smaller chunks for better retrieval
                        chunk_overlap=1200,  # More overlap for context preservation
                        length_function=len
                    )
                    texts = text_splitter.split_text(raw_text)
                    all_texts.extend(texts)
                    processed_files.append(doc_name)
                    
                    # Enhanced logging with parsing metadata
                    parser_info = f" (parser: {parsing_metadata.get('parser', 'unknown')})"
                    print(f"   Successfully processed {len(texts)} chunks from {doc_name}{parser_info}")
                    
                    if parsing_metadata.get('tables_found', 0) > 0:
                        print(f"   Found {parsing_metadata['tables_found']} tables in {doc_name}")
                else:
                    print(f"   No text content found in {doc_name}")
                    if not parsing_metadata.get('success', False):
                        print(f"   Parsing error: {parsing_metadata.get('error', 'Unknown error')}")
                    skipped_files.append(doc_name)
            except Exception as e:
                print(f"   Error processing {doc_name}: {str(e)}")
                skipped_files.append(doc_name)
        else:
            print(f"   Document not found: {file_path}")
            skipped_files.append(doc_name)
    
    if all_texts:
        # Create embeddings and add to Qdrant
        print(f"Creating embeddings and adding to Qdrant...")
        
        # Prepare metadata for documents
        metadatas = []
        for i, text in enumerate(all_texts):
            metadatas.append({
                "source": "srmu_documents",
                "chunk_id": i,
                "processed_at": datetime.now().isoformat()
            })
        
        # Add documents to vector store
        success = vector_manager.add_documents(all_texts, metadatas)
        
        if success:
            print(f"Successfully processed {len(processed_files)} documents: {', '.join(processed_files)}")
            print(f"Added {len(all_texts)} text chunks to {vector_manager.db_type.upper()} vector store")
        else:
            print(f"Failed to add documents to {vector_manager.db_type.upper()} vector store")
        
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
            print("[DOCS] Available documents in docs folder:")
            for doc in available_docs:
                print(f"   - {os.path.basename(doc)}")
        else:
            print("[DOCS] No PDF documents found in docs folder!")

@app.on_event("startup")
async def startup_event():
    """Initialize documents and auto-scrape websites when the server starts"""
    # Initialize PDF documents first
    initialize_documents()
    
    # Auto-scrape developer-configured websites
    if AUTO_SCRAPE_CONFIG["scrape_on_startup"]:
        await auto_scrape_developer_websites()

@app.get("/")
async def root():
    """Root endpoint to check if documents are loaded"""
    try:
        # Check vector database status
        status = vector_manager.get_status()
        
        if status["status"] != "ready":
            return {
                "message": f"ASK_GILLU is not ready - {status['message']}",
                "status": "not_ready",
                "error": status.get("message", "Vector database not accessible")
            }
        
        # Check auto-scrape status
        auto_scrape_info = {"enabled": False, "websites_count": 0}
        if AUTO_SCRAPE_CONFIG["enabled"]:
            auto_scrape_info = {
                "enabled": True,
                "websites_count": len(AUTO_SCRAPE_WEBSITES),
                "scrape_on_startup": AUTO_SCRAPE_CONFIG["scrape_on_startup"]
            }
        
        return {
            "message": "ASK_GILLU is ready with SRMU documents loaded in Qdrant!", 
            "status": "ready",
            "configured_documents": ALLOWED_DOCUMENTS,
            "total_documents": len(ALLOWED_DOCUMENTS),
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0,
            "auto_scrape_info": auto_scrape_info
        }
    except Exception as e:
        return {
            "message": "Documents not loaded yet", 
            "status": "not_ready", 
            "error": str(e),
            "configured_documents": ALLOWED_DOCUMENTS,
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0,
            "auto_scrape_info": {"enabled": AUTO_SCRAPE_CONFIG["enabled"], "websites_count": len(AUTO_SCRAPE_WEBSITES)}
        }

@app.get("/status")
async def get_status():
    """Get system status"""
    try:
        # Check vector database status
        db_status = vector_manager.get_status()
        
        if db_status["status"] != "ready":
            return {
                "status": "not_ready", 
                "message": f"{vector_manager.db_type.upper()} service is not available: {db_status.get('message', '')}",
                "configured_documents": ALLOWED_DOCUMENTS,
                "allowed_websites": ALLOWED_WEBSITES,
                "web_search_restricted": len(ALLOWED_WEBSITES) > 0,
                "database_type": vector_manager.db_type.upper()
            }
        
        documents_count = db_status.get("documents_count", 0)
        
        return {
            "status": "ready", 
            "message": f"ASK_GILLU is ready with {documents_count} documents in {vector_manager.db_type.upper()} vector store!",
            "configured_documents": ALLOWED_DOCUMENTS,
            "allowed_websites": ALLOWED_WEBSITES,
            "web_search_restricted": len(ALLOWED_WEBSITES) > 0,
            "total_allowed_websites": len(ALLOWED_WEBSITES),
            "database_type": vector_manager.db_type.upper(),
            "vector_store": vector_manager.db_type.upper(),
            "documents_count": documents_count
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

def combine_sources(question: str, system_prompt: str, use_web_search: bool = False) -> tuple[str, dict]:
    """
    Combine document search and web search results using advanced RAG features
    Returns: (context_string, metadata_dict)
    """
    context_parts = []
    search_metadata = {
        "documents_found": 0,
        "cache_hit": False,
        "semantic_chunks": False,
        "reranked": False,
        "web_search_used": use_web_search
    }
    
    # Always include document-based context if available
    try:
        # Get relevant documents from enhanced vector store with caching and feedback
        search_result = vector_manager.similarity_search(question, k=5)
        
        # Handle both old and new return formats
        if isinstance(search_result, tuple):
            docs, metadata = search_result
            search_metadata.update(metadata)
        else:
            # Backward compatibility - old format returns just docs
            docs = search_result
            search_metadata["documents_found"] = len(docs) if docs else 0
        
        if docs:
            doc_context = "\n\n".join([doc.page_content for doc in docs])
            context_parts.append(f"UNIVERSITY DOCUMENTS:\n{doc_context}")
            
    except Exception as e:
        print(f"Error loading documents: {e}")
        search_metadata["error"] = str(e)
    
    # Add web search results if requested
    if use_web_search:
        web_results = perform_web_search(question)
        if web_results and "No web search results found" not in web_results:
            context_parts.append(f"WEB SEARCH RESULTS:\n{web_results}")
    
    # Combine all context
    combined_context = "\n\n" + "="*50 + "\n\n".join(context_parts) if context_parts else ""
    
    return combined_context, search_metadata

@app.post("/ask")
async def ask_question(
    question: str = Form(...),
    system_prompt: str = Form("You are ASK_GILLU, an AI assistant for SRMU (Shri Ramswaroop Memorial University). Answer questions based on the provided documents and be helpful and accurate."),
    use_web_search: bool = Form(False)
):
    """Answer questions based on documents with optional web search - Enhanced with advanced RAG features"""
    try:
        # Get context from documents and optionally web search with metadata
        context, search_metadata = combine_sources(question, system_prompt, use_web_search)
        
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
        
        # Enhanced response with advanced RAG metadata
        return {
            "answer": response.content,
            "sources_used": {
                "documents": search_metadata.get("documents_found", 0) > 0,
                "web_search": use_web_search,
                "web_search_restricted": len(ALLOWED_WEBSITES) > 0 if use_web_search else False
            },
            "advanced_rag_features": {
                "documents_found": search_metadata.get("documents_found", 0),
                "cache_hit": search_metadata.get("cache_hit", False),
                "semantic_chunks_used": search_metadata.get("semantic_chunks", False),
                "results_reranked": search_metadata.get("reranked", False),
                "response_time_ms": search_metadata.get("response_time_ms", 0)
            }
        }
        
    except Exception as e:
        return {"error": f"Error processing question: {str(e)}"}

# Web Scraping Endpoints

@app.post("/scrape-websites")
async def scrape_websites(
    urls: str = Form(...),  # JSON string of URLs
    update_vectorstore: bool = Form(True),
    scrape_name: str = Form("Custom Scrape")
):
    """
    Scrape websites and optionally add to vector store
    """
    try:
        # Parse URLs from JSON string
        try:
            url_list = json.loads(urls) if isinstance(urls, str) else urls
            if not isinstance(url_list, list):
                raise ValueError("URLs must be provided as a list")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format for URLs")
        
        if len(url_list) > WEB_SCRAPER_CONFIG["max_urls_per_request"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum {WEB_SCRAPER_CONFIG['max_urls_per_request']} URLs allowed per request"
            )
        
        # Initialize scraper
        scraper = WebScraper(delay=WEB_SCRAPER_CONFIG["delay"])
        
        # Scrape all URLs
        print(f"🕷️ Starting web scraping for {len(url_list)} URLs...")
        scraped_data = scraper.scrape_multiple_urls(url_list)
        
        if not scraped_data:
            return {
                "success": False,
                "message": "No content could be scraped from the provided URLs",
                "scraped_count": 0,
                "urls_failed": url_list
            }
        
        # Save scraped data to file
        scrape_id = str(uuid.uuid4())[:8]
        scraped_file = f"scraped_data_{scrape_id}.json"
        scraped_dir = WEB_SCRAPER_CONFIG["scraped_data_dir"]
        os.makedirs(scraped_dir, exist_ok=True)
        scraped_path = os.path.join(scraped_dir, scraped_file)
        
        scraped_metadata = {
            "scrape_id": scrape_id,
            "scrape_name": scrape_name,
            "scraped_at": datetime.now().isoformat(),
            "urls_requested": url_list,
            "urls_successful": [item['url'] for item in scraped_data],
            "urls_failed": [url for url in url_list if url not in [item['url'] for item in scraped_data]],
            "total_words": sum(item['word_count'] for item in scraped_data),
            "data": scraped_data
        }
        
        with open(scraped_path, 'w', encoding='utf-8') as f:
            json.dump(scraped_metadata, f, indent=2, ensure_ascii=False)
        
        # Update vector store if requested
        vectorstore_updated = False
        if update_vectorstore:
            vectorstore_updated = await update_vectorstore_with_scraped_data(scraped_data)
            if vectorstore_updated:
                print(f"✅ Vector store updated with {len(scraped_data)} scraped documents")
            else:
                print("❌ Failed to update vector store")
        
        return {
            "success": True,
            "message": f"Successfully scraped {len(scraped_data)} out of {len(url_list)} URLs",
            "scraped_count": len(scraped_data),
            "failed_count": len(url_list) - len(scraped_data),
            "scrape_id": scrape_id,
            "total_words": scraped_metadata["total_words"],
            "scraped_data_preview": scraped_data[:3],  # Return first 3 items as preview
            "vectorstore_updated": vectorstore_updated,
            "scraped_file": scraped_file
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in scrape_websites: {str(e)}")
        return {
            "success": False,
            "message": f"Error scraping websites: {str(e)}",
            "scraped_count": 0
        }

@app.post("/scrape-single-website")
async def scrape_single_website(
    url: str = Form(...),
    include_links: bool = Form(False),
    max_links: int = Form(10),
    update_vectorstore: bool = Form(True)
):
    """
    Scrape a single website and optionally include linked pages
    """
    try:
        scraper = WebScraper(delay=WEB_SCRAPER_CONFIG["delay"])
        urls_to_scrape = [url]
        
        # If include_links is True, get additional links from the page
        if include_links:
            print(f"🔗 Discovering links from: {url}")
            links = scraper.get_page_links(url, same_domain_only=True)
            urls_to_scrape.extend(links[:max_links])
            print(f"📎 Found {len(links)} links, will scrape {min(len(links), max_links)} additional pages")
        
        # Scrape all URLs
        scraped_data = scraper.scrape_multiple_urls(urls_to_scrape)
        
        if not scraped_data:
            return {
                "success": False,
                "message": "No content could be scraped from the website",
                "scraped_count": 0
            }
        
        # Update vector store if requested
        vectorstore_updated = False
        if update_vectorstore:
            vectorstore_updated = await update_vectorstore_with_scraped_data(scraped_data)
        
        return {
            "success": True,
            "message": f"Successfully scraped {len(scraped_data)} pages from {url}",
            "scraped_count": len(scraped_data),
            "total_words": sum(item['word_count'] for item in scraped_data),
            "scraped_data": scraped_data,
            "vectorstore_updated": vectorstore_updated
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error scraping website: {str(e)}",
            "scraped_count": 0
        }

async def update_vectorstore_with_scraped_data(scraped_data: List[Dict]) -> bool:
    """Add scraped data to the existing vector store"""
    try:
        # Process scraped data
        all_texts = []
        metadatas = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        for item in scraped_data:
            # Create document header with metadata
            header = f"""Source: {item['title']}
URL: {item['url']}
Scraped: {item['scraped_at']}
Word Count: {item['word_count']}
Method: {item.get('method', 'unknown')}

"""
            full_content = header + item['content']
            
            # Split content into chunks
            chunks = text_splitter.split_text(full_content)
            all_texts.extend(chunks)
            
            # Add metadata for each chunk
            for chunk in chunks:
                metadatas.append({
                    'source': item['title'],
                    'url': item['url'],
                    'scraped_at': item['scraped_at'],
                    'word_count': item['word_count'],
                    'method': item.get('method', 'unknown'),
                    'chunk_type': 'scraped_data'
                })
        
        if all_texts:
            # Add new texts to vector store
            success = vector_manager.add_documents(all_texts, metadatas)
            if success:
                print(f"✅ Added {len(all_texts)} new text chunks to {vector_manager.db_type.upper()} vector store from {len(scraped_data)} scraped pages")
                return True
            else:
                print(f"❌ Failed to add documents to {vector_manager.db_type.upper()} vector store")
                return False
        else:
            print("❌ No text chunks to add to vector store")
            return False
            
    except Exception as e:
        print(f"❌ Error updating vector store: {str(e)}")
        return False

@app.get("/scraped-data")
async def get_scraped_data():
    """Get list of all scraped data files"""
    try:
        scraped_dir = WEB_SCRAPER_CONFIG["scraped_data_dir"]
        if not os.path.exists(scraped_dir):
            return {"scraped_files": [], "total_files": 0}
        
        files = [f for f in os.listdir(scraped_dir) if f.endswith('.json')]
        file_info = []
        
        for file in files[:20]:  # Limit to 20 most recent files
            file_path = os.path.join(scraped_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_info.append({
                        "filename": file,
                        "scrape_id": data.get("scrape_id", "unknown"),
                        "scrape_name": data.get("scrape_name", "Unknown"),
                        "scraped_at": data.get("scraped_at", "unknown"),
                        "urls_count": len(data.get("urls_successful", [])),
                        "total_words": data.get("total_words", 0)
                    })
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        
        # Sort by scraped_at date (most recent first)
        file_info.sort(key=lambda x: x["scraped_at"], reverse=True)
        
        return {
            "scraped_files": file_info,
            "total_files": len(files),
            "scraped_data_directory": scraped_dir
        }
        
    except Exception as e:
        return {"error": f"Error retrieving scraped data: {str(e)}"}

@app.delete("/scraped-data/{scrape_id}")
async def delete_scraped_data(scrape_id: str):
    """Delete a specific scraped data file"""
    try:
        scraped_dir = WEB_SCRAPER_CONFIG["scraped_data_dir"]
        file_pattern = f"scraped_data_{scrape_id}.json"
        file_path = os.path.join(scraped_dir, file_pattern)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"Scraped data {scrape_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Scraped data not found")
            
    except Exception as e:
        return {"error": f"Error deleting scraped data: {str(e)}"}

@app.get("/scraper-config")
async def get_scraper_config():
    """Get current web scraper configuration"""
    return {
        "config": WEB_SCRAPER_CONFIG,
        "status": "Web scraper ready",
        "supported_formats": ["HTML", "Articles", "Blog posts", "News articles"],
        "rate_limiting": f"{WEB_SCRAPER_CONFIG['delay']} seconds between requests"
    }

async def auto_scrape_developer_websites():
    """
    Automatically scrape developer-configured websites during initialization
    This function is only called by the system, not accessible to users
    """
    if not AUTO_SCRAPE_CONFIG["enabled"] or not AUTO_SCRAPE_WEBSITES:
        print("[AUTO-SCRAPE] Auto-scraping is disabled or no websites configured")
        return
    
    print("[AUTO-SCRAPE] Starting developer-configured auto-scraping...")
    
    try:
        # Initialize scraper
        scraper = WebScraper(delay=WEB_SCRAPER_CONFIG["delay"])
        
        # Sort websites by priority (1 = highest priority)
        sorted_websites = sorted(AUTO_SCRAPE_WEBSITES, key=lambda x: x.get("priority", 999))
        
        scraped_count = 0
        failed_count = 0
        total_words = 0
        
        for website_config in sorted_websites:
            url = website_config["url"]
            name = website_config.get("name", "Unknown")
            
            print(f"[AUTO-SCRAPE] Auto-scraping: {name} ({url})")
            
            retries = 0
            success = False
            
            while retries < AUTO_SCRAPE_CONFIG["max_retries"] and not success:
                try:
                    result = scraper.scrape_url(url)
                    
                    if result:
                        # Add to vector store immediately
                        success = await update_vectorstore_with_scraped_data([result])
                        if success:
                            scraped_count += 1
                            total_words += result.get("word_count", 0)
                            print(f"   [SUCCESS] Successfully added {name} ({result.get('word_count', 0)} words)")
                        else:
                            print(f"   [WARNING] Scraped {name} but failed to add to vector store")
                            failed_count += 1
                    else:
                        print(f"   [ERROR] Failed to scrape content from {name}")
                        retries += 1
                        
                except Exception as e:
                    print(f"   [ERROR] Error scraping {name}: {str(e)}")
                    retries += 1
                    
                if not success and retries < AUTO_SCRAPE_CONFIG["max_retries"]:
                    print(f"   [RETRY] Retrying {name} (attempt {retries + 1}/{AUTO_SCRAPE_CONFIG['max_retries']})")
                    
            if not success:
                failed_count += 1
        
        # Save auto-scrape metadata
        auto_scrape_metadata = {
            "auto_scrape_completed_at": datetime.now().isoformat(),
            "websites_configured": len(AUTO_SCRAPE_WEBSITES),
            "successfully_scraped": scraped_count,
            "failed_scrapes": failed_count,
            "total_words_added": total_words,
            "scraped_websites": [
                {
                    "url": site["url"],
                    "name": site["name"],
                    "priority": site.get("priority", 999)
                }
                for site in sorted_websites
            ]
        }
        
        # Save metadata file
        os.makedirs(WEB_SCRAPER_CONFIG["scraped_data_dir"], exist_ok=True)
        metadata_file = os.path.join(WEB_SCRAPER_CONFIG["scraped_data_dir"], "auto_scrape_metadata.json")
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(auto_scrape_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"[AUTO-SCRAPE] Auto-scraping completed: {scraped_count}/{len(AUTO_SCRAPE_WEBSITES)} websites successfully added")
        print(f"[AUTO-SCRAPE] Total words added: {total_words}")
        
        if failed_count > 0:
            print(f"[AUTO-SCRAPE] {failed_count} websites failed to scrape - check logs for details")
            
    except Exception as e:
        print(f"[AUTO-SCRAPE] Error during auto-scraping: {str(e)}")

@app.get("/dev/auto-scrape-status")
async def get_auto_scrape_status():
    """
    Get status of developer-configured auto-scraping
    This endpoint is for developers only
    """
    try:
        metadata_file = os.path.join(WEB_SCRAPER_CONFIG["scraped_data_dir"], "auto_scrape_metadata.json")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = None
            
        return {
            "auto_scrape_enabled": AUTO_SCRAPE_CONFIG["enabled"],
            "scrape_on_startup": AUTO_SCRAPE_CONFIG["scrape_on_startup"],
            "configured_websites": len(AUTO_SCRAPE_WEBSITES),
            "websites_list": [
                {
                    "name": site["name"],
                    "url": site["url"],
                    "priority": site.get("priority", 999)
                }
                for site in AUTO_SCRAPE_WEBSITES
            ],
            "last_auto_scrape": metadata,
            "config": AUTO_SCRAPE_CONFIG
        }
    except Exception as e:
        return {"error": f"Error retrieving auto-scrape status: {str(e)}"}

@app.post("/dev/trigger-auto-scrape")
async def trigger_manual_auto_scrape():
    """
    Manually trigger auto-scraping of developer-configured websites
    This endpoint is for developers only
    """
    try:
        await auto_scrape_developer_websites()
        return {
            "success": True,
            "message": "Auto-scraping completed successfully",
            "configured_websites": len(AUTO_SCRAPE_WEBSITES)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Auto-scraping failed: {str(e)}"
        }

# Vector Database Management Endpoints

@app.get("/api/vector-db/current")
async def get_current_vector_db():
    """Get current vector database information"""
    try:
        status = vector_manager.get_status()
        return {
            "success": True,
            "current_database": vector_manager.db_type.upper(),
            "status": status["status"],
            "message": status.get("message", ""),
            "documents_count": status.get("documents_count", 0),
            "available_databases": vector_manager.get_available_databases()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting vector database info: {str(e)}"
        }

@app.post("/api/vector-db/switch")
async def switch_vector_database_endpoint(new_db_type: str = Form(...)):
    """Switch to a different vector database"""
    try:
        if new_db_type.lower() not in ["qdrant", "faiss"]:
            return {
                "success": False,
                "message": f"Invalid database type: {new_db_type}. Must be 'qdrant' or 'faiss'"
            }
        
        # Check if already using the requested database
        if new_db_type.lower() == vector_manager.db_type:
            return {
                "success": True,
                "message": f"Already using {new_db_type.upper()} database",
                "current_database": vector_manager.db_type.upper()
            }
        
        # Attempt to switch
        success = vector_manager.switch_database(new_db_type)
        
        if success:
            # Update environment variable for persistence
            os.environ["VECTOR_DB_TYPE"] = new_db_type.lower()
            
            # Get status of new database
            status = vector_manager.get_status()
            
            return {
                "success": True,
                "message": f"Successfully switched to {new_db_type.upper()} database",
                "current_database": vector_manager.db_type.upper(),
                "status": status["status"],
                "documents_count": status.get("documents_count", 0)
            }
        else:
            return {
                "success": False,
                "message": f"Failed to switch to {new_db_type.upper()} database"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error switching vector database: {str(e)}"
        }

@app.get("/api/vector-db/available")
async def get_available_vector_databases():
    """Get list of available vector database types"""
    try:
        return {
            "success": True,
            "available_databases": vector_manager.get_available_databases(),
            "current_database": vector_manager.db_type.upper()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting available databases: {str(e)}"
        }

@app.get("/api/vector-db/status")
async def get_vector_database_status():
    """Get detailed status of current vector database"""
    try:
        status = vector_manager.get_status()
        return {
            "success": True,
            "database_type": vector_manager.db_type.upper(),
            "detailed_status": status,
            "hybrid_search_enabled": vector_manager.use_hybrid_search,
            "cached_documents": vector_manager.get_document_count()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting vector database status: {str(e)}"
        }

# Enhanced Search and Debugging Endpoints

@app.post("/api/search/explain")
async def explain_search_results(query: str = Form(...), k: int = Form(3)):
    """Get detailed explanation of search results for debugging"""
    try:
        explanation = vector_manager.get_search_explanation(query, k)
        return {
            "success": True,
            "explanation": explanation
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error explaining search: {str(e)}"
        }

@app.post("/api/search/hybrid")
async def hybrid_search_endpoint(
    query: str = Form(...), 
    k: int = Form(3),
    use_hybrid: bool = Form(True)
):
    """Perform search with option to enable/disable hybrid search"""
    try:
        # Get search results
        docs = vector_manager.similarity_search(query, k, use_hybrid=use_hybrid)
        
        # Format results
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return {
            "success": True,
            "query": query,
            "search_type": "hybrid" if use_hybrid else f"{vector_manager.db_type}_only",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in search: {str(e)}"
        }

@app.post("/api/search/weights")
async def update_search_weights(
    bm25_weight: float = Form(...),
    vector_weight: float = Form(...)
):
    """Update hybrid search weights"""
    try:
        if bm25_weight < 0 or vector_weight < 0:
            return {
                "success": False,
                "message": "Weights must be non-negative"
            }
        
        vector_manager.update_hybrid_weights(bm25_weight, vector_weight)
        
        return {
            "success": True,
            "message": f"Updated search weights - BM25: {bm25_weight}, Vector: {vector_weight}",
            "new_weights": {
                "bm25": bm25_weight / (bm25_weight + vector_weight),
                "vector": vector_weight / (bm25_weight + vector_weight)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating weights: {str(e)}"
        }

@app.post("/api/pdf/parse")
async def parse_pdf_endpoint(
    file_name: str = Form(...),
    method: str = Form("hybrid")
):
    """Parse a specific PDF with advanced parser"""
    try:
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        file_path = os.path.join(docs_dir, file_name)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File not found: {file_name}"
            }
        
        text, metadata = vector_manager.parse_pdf_advanced(file_path, method)
        
        return {
            "success": True,
            "file_name": file_name,
            "parsing_method": method,
            "text_length": len(text),
            "text_preview": text[:500] + "..." if len(text) > 500 else text,
            "metadata": metadata
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error parsing PDF: {str(e)}"
        }

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    category: str = Form("uploaded")
):
    """Upload and add a new document to the vector database"""
    try:
        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            return {
                "success": False,
                "message": "Only PDF files are supported"
            }
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(uploads_dir, file.filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File {file.filename} already exists"
            }
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add to vector database using advanced parsing
        success = vector_manager.add_pdf(file_path)
        
        if success:
            # Get updated status
            status = vector_manager.get_status()
            
            return {
                "success": True,
                "message": f"Successfully uploaded and processed {file.filename}",
                "file_name": file.filename,
                "file_size": len(content),
                "database_type": vector_manager.db_type.upper(),
                "total_documents": status.get('documents_count', 'Unknown')
            }
        else:
            # Remove the file if adding to vector store failed
            os.remove(file_path)
            return {
                "success": False,
                "message": f"Failed to process {file.filename}. File was not saved."
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading document: {str(e)}"
        }

@app.post("/api/documents/add-text")
async def add_text_document(
    content: str = Form(...),
    title: str = Form(...),
    source: str = Form("manual_entry"),
    category: str = Form("text")
):
    """Add a text document directly to the vector database"""
    try:
        if not content.strip():
            return {
                "success": False,
                "message": "Document content cannot be empty"
            }
        
        # Prepare metadata
        metadata = {
            "title": title,
            "source": source,
            "category": category,
            "type": "text",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to vector database
        success = vector_manager.add_documents([content], [metadata])
        
        if success:
            # Get updated status
            status = vector_manager.get_status()
            
            return {
                "success": True,
                "message": f"Successfully added text document: {title}",
                "title": title,
                "content_length": len(content),
                "database_type": vector_manager.db_type.upper(),
                "total_documents": status.get('documents_count', 'Unknown')
            }
        else:
            return {
                "success": False,
                "message": "Failed to add text document to vector database"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding text document: {str(e)}"
        }

# Advanced RAG Feature Endpoints

@app.post("/api/feedback")
async def submit_feedback(
    question: str = Form(...),
    answer_id: str = Form(None),
    rating: int = Form(...),  # 1-5 scale
    feedback_type: str = Form("rating"),  # rating, correction, suggestion
    comment: str = Form(""),
    was_helpful: bool = Form(True)
):
    """Submit user feedback for query responses"""
    try:
        feedback_result = vector_manager.submit_feedback(
            question=question,
            answer_id=answer_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            was_helpful=was_helpful
        )
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_result.get("feedback_id"),
            "total_feedback_count": feedback_result.get("total_count", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error submitting feedback: {str(e)}"
        }

@app.get("/api/analytics/performance")
async def get_performance_analytics():
    """Get system performance analytics and metrics"""
    try:
        analytics = vector_manager.get_performance_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving analytics: {str(e)}"
        }

@app.get("/api/analytics/feedback")
async def get_feedback_analytics():
    """Get user feedback analytics and insights"""
    try:
        feedback_analytics = vector_manager.get_feedback_analytics()
        
        return {
            "success": True,
            "feedback_analytics": feedback_analytics
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving feedback analytics: {str(e)}"
        }

@app.get("/api/recommendations")
async def get_system_recommendations():
    """Get system improvement recommendations based on analytics"""
    try:
        recommendations = vector_manager.get_improvement_recommendations()
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating recommendations: {str(e)}"
        }

@app.post("/api/cache/clear")
async def clear_response_cache():
    """Clear the response cache (admin function)"""
    try:
        cache_stats = vector_manager.clear_cache()
        
        return {
            "success": True,
            "message": "Response cache cleared successfully",
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error clearing cache: {str(e)}"
        }

@app.get("/api/cache/stats")
async def get_cache_statistics():
    """Get response cache statistics"""
    try:
        cache_stats = vector_manager.get_cache_statistics()
        
        return {
            "success": True,
            "cache_statistics": cache_stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving cache statistics: {str(e)}"
        }

@app.post("/api/settings/advanced-rag")
async def configure_advanced_rag(
    enable_semantic_chunking: bool = Form(True),
    enable_reranking: bool = Form(True),
    enable_caching: bool = Form(True),
    enable_feedback_tracking: bool = Form(True),
    reranking_strategy: str = Form("rrf"),  # rrf, semantic, diversity, contextual
    cache_ttl_hours: int = Form(24)
):
    """Configure advanced RAG features"""
    try:
        config_result = vector_manager.configure_advanced_features(
            semantic_chunking=enable_semantic_chunking,
            reranking=enable_reranking,
            caching=enable_caching,
            feedback_tracking=enable_feedback_tracking,
            reranking_strategy=reranking_strategy,
            cache_ttl_hours=cache_ttl_hours
        )
        
        return {
            "success": True,
            "message": "Advanced RAG configuration updated successfully",
            "configuration": config_result
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error configuring advanced RAG: {str(e)}"
        }
