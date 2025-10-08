# 🕷️ Web Scraping Feature Documentation

## Overview

The ASK_GILLU web scraping feature allows you to scrape content from websites and automatically add it to the AI's knowledge base. This enables the AI to answer questions using information from any website you specify, in addition to the pre-loaded university documents.

## 🚀 **How It Works**

1. **Input URLs**: Provide a list of website URLs to scrape
2. **Content Extraction**: The system scrapes text content from each website
3. **Vector Store Integration**: Scraped content is processed and added to the vector database
4. **Enhanced Answers**: The AI can now reference scraped content when answering questions

## 📋 **Features**

### **✅ Smart Content Extraction**
- **Newspaper3k Integration**: Optimized for articles and blog posts
- **BeautifulSoup Fallback**: Handles any website structure
- **Content Filtering**: Automatically removes navigation, ads, and irrelevant content
- **Metadata Extraction**: Captures titles, publication dates, authors, and summaries

### **✅ Multiple Scraping Methods**
- **Bulk Scraping**: Submit multiple URLs at once
- **Single Website + Links**: Scrape a website and discover related pages
- **Rate Limiting**: Respectful scraping with delays between requests
- **Error Handling**: Graceful handling of failed URLs

### **✅ Vector Store Integration**
- **Automatic Chunking**: Content split into optimal sizes for AI processing
- **Metadata Preservation**: URL, title, and scraping date included with each chunk
- **Seamless Integration**: Scraped content merged with existing documents
- **Immediate Availability**: New content available for questions immediately

### **✅ Data Management**
- **Scrape History**: Track all scraping sessions
- **Preview Mode**: See sample content before full processing
- **Named Datasets**: Organize scraped content with custom names
- **Performance Metrics**: Word counts, success rates, and timing information

## 🎯 **Using the Web Scraping Interface**

### **Step 1: Access the Scraping Interface**
1. Start ASK_GILLU application
2. Look for the "🌐 Web Scraping & Knowledge Base Management" section
3. Click to expand the interface

### **Step 2: Prepare Your URLs**
```
https://example.com/article1
https://another-site.com/research-paper
https://university.edu/course-catalog
https://news-site.com/latest-tech-trends
```

**URL Requirements:**
- Must start with `http://` or `https://`
- One URL per line OR comma-separated
- Maximum 20 URLs per scraping session

### **Step 3: Configure Scraping**
- **URLs**: Paste your list of URLs
- **Scrape Name**: Give your dataset a meaningful name (e.g., "AI Research Papers", "Company Documentation")
- **Vector Store Update**: Automatically enabled to add content to knowledge base

### **Step 4: Execute Scraping**
1. Click "🌐 Scrape & Add to Knowledge Base"
2. Wait for processing (typically 1-3 minutes for 5-10 URLs)
3. Review results and success/failure statistics

### **Step 5: Test Your New Knowledge**
Ask questions that reference the scraped content:
```
"What are the latest trends in [topic from scraped content]?"
"How does [company] approach [topic]?"
"Compare SRMU's approach to [topic from scraped content]"
```

## 🔧 **API Endpoints**

### **Bulk Website Scraping**
```http
POST /scrape-websites
Content-Type: multipart/form-data

urls: ["https://example.com", "https://another.com"]
update_vectorstore: true
scrape_name: "Custom Dataset"
```

### **Single Website + Links**
```http
POST /scrape-single-website
Content-Type: multipart/form-data

url: "https://example.com"
include_links: true
max_links: 10
update_vectorstore: true
```

### **View Scraped Data**
```http
GET /scraped-data
```

### **Delete Scraped Data**
```http
DELETE /scraped-data/{scrape_id}
```

## 📊 **Response Format**

### **Successful Scraping Response**
```json
{
  "success": true,
  "message": "Successfully scraped 8 out of 10 URLs",
  "scraped_count": 8,
  "failed_count": 2,
  "scrape_id": "abc12345",
  "total_words": 15420,
  "scraped_data_preview": [
    {
      "title": "AI Trends in 2024",
      "url": "https://example.com/ai-trends",
      "summary": "Latest developments in artificial intelligence...",
      "word_count": 1250,
      "scraped_at": "2024-07-11T10:30:00Z"
    }
  ],
  "vectorstore_updated": true
}
```

## 💡 **Best Practices**

### **URL Selection**
- ✅ Choose authoritative, well-structured websites
- ✅ Focus on content-rich pages (articles, documentation, research)
- ✅ Avoid pages with heavy JavaScript or dynamic content
- ✅ Test individual URLs before bulk scraping

### **Content Quality**
- ✅ Scrape recent, relevant content
- ✅ Choose websites with clear, readable text
- ✅ Avoid heavily advertisement-laden sites
- ✅ Focus on domain-specific knowledge for your use case

### **Organization**
- ✅ Use descriptive names for scrape sessions
- ✅ Group related content together
- ✅ Document your data sources
- ✅ Regularly update with fresh content

### **Performance Optimization**
- ✅ Scrape in batches of 5-10 URLs for best performance
- ✅ Allow time between large scraping sessions
- ✅ Monitor success rates and adjust URL selection
- ✅ Remove or replace failed URLs

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Scraping Fails**
```
❌ Failed to scrape: https://example.com
```
**Solutions:**
- Check if URL is accessible in your browser
- Ensure URL starts with http:// or https://
- Try the URL individually first
- Some websites block automated scraping

#### **No Content Extracted**
```
✅ Scraped successfully but 0 words extracted
```
**Solutions:**
- Website might be JavaScript-heavy
- Content might be behind login/paywall
- Try a different page from the same site
- Check if content is in images/videos (not scrapable)

#### **Timeout Errors**
```
❌ Request timed out
```
**Solutions:**
- Reduce number of URLs per batch
- Try scraping individual URLs
- Check internet connection
- Some websites are slow to respond

#### **Vector Store Update Failed**
```
✅ Scraped successfully but ❌ Vector store not updated
```
**Solutions:**
- Check backend logs for errors
- Ensure adequate disk space
- Restart backend if necessary
- Try with fewer URLs first

### **Debug Mode**
Check browser console (F12) for detailed error messages:
```javascript
console.log('Scraping response:', response);
```

## 🎯 **Use Cases**

### **Academic Research**
```
URLs:
- https://arxiv.org/abs/2301.12345
- https://ieeexplore.ieee.org/document/9876543
- https://scholar.google.com/citations?view_op=view_citation&hl=en&user=ABC123

Name: "AI Research Papers 2024"
```

### **Industry Documentation**
```
URLs:
- https://company.com/api-documentation
- https://company.com/best-practices
- https://company.com/case-studies

Name: "Company Technical Docs"
```

### **News and Trends**
```
URLs:
- https://techcrunch.com/category/artificial-intelligence/
- https://www.nature.com/subjects/machine-learning
- https://ai.googleblog.com/

Name: "Latest AI News"
```

### **Educational Content**
```
URLs:
- https://coursera.org/learn/machine-learning
- https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/
- https://www.edx.org/course/introduction-to-artificial-intelligence

Name: "Online Course Materials"
```

## 🔐 **Security & Ethics**

### **Responsible Scraping**
- ✅ Respect robots.txt files
- ✅ Use reasonable delays between requests
- ✅ Don't overload websites with requests
- ✅ Only scrape publicly available content

### **Legal Considerations**
- ✅ Ensure you have permission to scrape content
- ✅ Respect copyright and terms of service
- ✅ Use scraped content for personal/educational purposes
- ✅ Attribute sources when appropriate

### **Data Privacy**
- ✅ Don't scrape personal or sensitive information
- ✅ Be cautious with user-generated content
- ✅ Consider data retention policies
- ✅ Respect privacy settings and restrictions

## 📈 **Performance Metrics**

The system tracks:
- **Success Rate**: Percentage of URLs successfully scraped
- **Content Volume**: Total words and chunks extracted
- **Processing Time**: Time taken for scraping and vector store updates
- **Error Patterns**: Common failure reasons for optimization

## 🚀 **Advanced Configuration**

### **Backend Configuration** (backend/main.py)
```python
WEB_SCRAPER_CONFIG = {
    "delay": 1.0,                    # Delay between requests (seconds)
    "max_urls_per_request": 20,      # Maximum URLs per batch
    "max_content_length": 50000,     # Maximum content length per page
    "timeout": 30,                   # Request timeout (seconds)
    "scraped_data_dir": "scraped_data"  # Storage directory
}
```

### **Content Chunking Settings**
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Size of each text chunk
    chunk_overlap=200,      # Overlap between chunks
    length_function=len
)
```

This comprehensive web scraping feature transforms ASK_GILLU into a dynamic knowledge base that can incorporate any web content you specify, making it an incredibly powerful and flexible AI assistant! 🎉
