# 🔧 Developer-Controlled Auto-Scraping Feature

## Overview

The ASK_GILLU system now includes a **developer-controlled auto-scraping feature** that automatically scrapes and adds content from pre-configured websites to the knowledge base during system initialization. This feature is **completely hidden from users** and can only be configured by developers.

## 🎯 **Key Benefits**

- ✅ **Developer Control**: Only developers can configure which websites to scrape
- ✅ **Automatic Updates**: Content is scraped during server startup
- ✅ **Enhanced Knowledge**: AI has access to additional curated web content
- ✅ **User Transparency**: Users see enhanced answers without knowing the source
- ✅ **Priority System**: Important websites are scraped first
- ✅ **Error Handling**: Robust retry mechanism for failed scrapes

## 🛠️ **Configuration**

### **1. Configure Websites to Auto-Scrape**

Edit the `AUTO_SCRAPE_WEBSITES` list in `backend/main.py`:

```python
AUTO_SCRAPE_WEBSITES = [
    # University-related content (Priority 1 - Most Important)
    {
        "url": "https://srmu.ac.in/placement-overview",
        "name": "SRMU Placement Overview",
        "priority": 1
    },
    {
        "url": "https://srmu.ac.in/academics/courses",
        "name": "SRMU Course Catalog", 
        "priority": 1
    },
    
    # Educational resources (Priority 2 - Medium)
    {
        "url": "https://en.wikipedia.org/wiki/Data_science",
        "name": "Data Science Overview",
        "priority": 2
    },
    {
        "url": "https://en.wikipedia.org/wiki/Machine_learning",
        "name": "Machine Learning Overview", 
        "priority": 2
    },
    
    # Industry content (Priority 3 - Low)
    {
        "url": "https://example.com/industry-trends",
        "name": "Industry Trends",
        "priority": 3
    }
    
    # Add more websites here as needed
]
```

### **2. Configure Auto-Scraping Behavior**

```python
AUTO_SCRAPE_CONFIG = {
    "enabled": True,                    # Enable/disable auto-scraping
    "scrape_on_startup": True,          # Scrape during server startup
    "update_interval_hours": 24,        # Re-scrape interval (0 = never)
    "max_retries": 3,                   # Retries for failed URLs
    "timeout_per_url": 30,              # Timeout per URL (seconds)
}
```

## 📋 **Website Configuration Fields**

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `url` | ✅ | Full URL to scrape | `"https://example.com/page"` |
| `name` | ✅ | Descriptive name for the content | `"University Admissions Guide"` |
| `priority` | ❌ | Scraping priority (1=high, 2=medium, 3=low) | `1` |

## 🔄 **How It Works**

### **During Server Startup:**

1. **Document Initialization**: PDF documents are loaded first
2. **Auto-Scraping Trigger**: If enabled, auto-scraping begins
3. **Priority Processing**: Websites are scraped in priority order (1, 2, 3...)
4. **Content Extraction**: Each website's content is extracted and cleaned
5. **Vector Store Integration**: Content is immediately added to the knowledge base
6. **Retry Logic**: Failed scrapes are retried up to `max_retries` times
7. **Metadata Logging**: Results are saved for developer review

### **Processing Flow:**

```
Server Starts
     ↓
Load PDF Documents
     ↓
Check AUTO_SCRAPE_CONFIG.enabled
     ↓
Sort websites by priority
     ↓
For each website:
  - Scrape content
  - Add to vector store
  - Log results
     ↓
Save metadata file
     ↓
Server Ready
```

## 🚀 **Developer API Endpoints**

### **Check Auto-Scraping Status**
```http
GET /dev/auto-scrape-status
```

**Response:**
```json
{
  "auto_scrape_enabled": true,
  "scrape_on_startup": true,
  "configured_websites": 4,
  "websites_list": [
    {
      "name": "SRMU Placement Overview",
      "url": "https://srmu.ac.in/placement-overview",
      "priority": 1
    }
  ],
  "last_auto_scrape": {
    "auto_scrape_completed_at": "2024-07-11T10:30:00Z",
    "successfully_scraped": 3,
    "failed_scrapes": 1,
    "total_words_added": 5420
  }
}
```

### **Manually Trigger Auto-Scraping**
```http
POST /dev/trigger-auto-scrape
```

**Response:**
```json
{
  "success": true,
  "message": "Auto-scraping completed successfully",
  "configured_websites": 4
}
```

## 📊 **Monitoring & Logging**

### **Auto-Scrape Metadata File**
Located at: `scraped_data/auto_scrape_metadata.json`

```json
{
  "auto_scrape_completed_at": "2024-07-11T10:30:00Z",
  "websites_configured": 4,
  "successfully_scraped": 3,
  "failed_scrapes": 1,
  "total_words_added": 5420,
  "scraped_websites": [
    {
      "url": "https://srmu.ac.in/placement-overview",
      "name": "SRMU Placement Overview",
      "priority": 1
    }
  ]
}
```

### **Console Logging**
```
🕷️ Starting developer-configured auto-scraping...
🔍 Auto-scraping: SRMU Placement Overview (https://srmu.ac.in/placement-overview)
   ✅ Successfully added SRMU Placement Overview (1250 words)
🔍 Auto-scraping: Data Science Overview (https://en.wikipedia.org/wiki/Data_science)
   ✅ Successfully added Data Science Overview (2170 words)
🎉 Auto-scraping completed: 3/4 websites successfully added
📊 Total words added: 5420
```

## 🎯 **Use Cases**

### **University Enhancement**
```python
AUTO_SCRAPE_WEBSITES = [
    {"url": "https://srmu.ac.in/admissions", "name": "Admissions Info", "priority": 1},
    {"url": "https://srmu.ac.in/courses", "name": "Course Catalog", "priority": 1},
    {"url": "https://srmu.ac.in/campus-life", "name": "Campus Life", "priority": 2},
    {"url": "https://srmu.ac.in/research", "name": "Research Programs", "priority": 2}
]
```

### **Academic Subject Enhancement**
```python
AUTO_SCRAPE_WEBSITES = [
    # Computer Science
    {"url": "https://en.wikipedia.org/wiki/Computer_science", "name": "CS Overview", "priority": 1},
    {"url": "https://stackoverflow.com/questions/tagged/python", "name": "Python Q&A", "priority": 2},
    
    # Data Science
    {"url": "https://en.wikipedia.org/wiki/Data_science", "name": "Data Science", "priority": 1},
    {"url": "https://kaggle.com/learn", "name": "Kaggle Learn", "priority": 2}
]
```

### **Industry Knowledge**
```python
AUTO_SCRAPE_WEBSITES = [
    # AI/ML Industry
    {"url": "https://openai.com/blog", "name": "OpenAI Blog", "priority": 1},
    {"url": "https://ai.googleblog.com", "name": "Google AI Blog", "priority": 1},
    {"url": "https://techcrunch.com/category/artificial-intelligence", "name": "AI News", "priority": 2}
]
```

## ⚙️ **Configuration Best Practices**

### **1. Priority Assignment**
- **Priority 1**: Critical university/institutional content
- **Priority 2**: Important educational/academic content  
- **Priority 3**: Supplementary industry/news content

### **2. URL Selection**
- ✅ Choose stable, well-maintained websites
- ✅ Select content-rich pages with valuable information
- ✅ Avoid pages with heavy JavaScript or dynamic content
- ✅ Test URLs manually before adding to configuration

### **3. Performance Optimization**
- ✅ Limit to 10-15 websites for optimal startup time
- ✅ Set reasonable timeouts (30 seconds per URL)
- ✅ Use retry logic for unreliable sources
- ✅ Monitor success rates and remove problematic URLs

### **4. Content Quality**
- ✅ Focus on authoritative sources
- ✅ Choose educational/academic content
- ✅ Avoid frequently changing content
- ✅ Select content relevant to your users' needs

## 🔒 **Security & Privacy**

### **Developer Control Only**
- ❌ Users cannot see auto-scraping configuration
- ❌ Users cannot modify auto-scrape websites
- ❌ Users cannot trigger auto-scraping
- ✅ Only developers have access to configuration and monitoring

### **Responsible Scraping**
- ✅ Respect robots.txt files
- ✅ Use reasonable delays between requests
- ✅ Only scrape publicly available content
- ✅ Follow website terms of service

## 🛠️ **Troubleshooting**

### **Auto-Scraping Not Working**
1. Check `AUTO_SCRAPE_CONFIG.enabled = True`
2. Verify `AUTO_SCRAPE_CONFIG.scrape_on_startup = True`
3. Check server logs for error messages
4. Test individual URLs manually

### **Some Websites Failing**
1. Check URL accessibility in browser
2. Verify website allows automated access
3. Increase timeout values
4. Check for JavaScript-heavy content

### **Performance Issues**
1. Reduce number of configured websites
2. Increase delays between requests
3. Check server resources during startup
4. Consider reducing content volume per page

## 📈 **Performance Impact**

### **Startup Time**
- **Without Auto-Scraping**: ~5-10 seconds
- **With 5 Websites**: ~15-25 seconds
- **With 10 Websites**: ~30-45 seconds
- **With 15+ Websites**: 60+ seconds

### **Memory Usage**
- Each scraped page adds ~1-5MB to vector store
- 10 pages typically add ~20-50MB
- Monitor disk space in `vectorstore/` directory

## 🔄 **Maintenance**

### **Regular Tasks**
1. **Review Success Rates**: Check auto-scrape metadata monthly
2. **Update URLs**: Replace broken or outdated links
3. **Content Quality**: Verify scraped content remains relevant
4. **Performance Monitoring**: Track startup times and success rates

### **Updating Configuration**
1. Edit `AUTO_SCRAPE_WEBSITES` in `backend/main.py`
2. Restart the backend server
3. Check logs for successful auto-scraping
4. Test AI responses with new content

This developer-controlled auto-scraping feature ensures your AI assistant has access to curated, up-to-date web content while maintaining complete control over data sources and user privacy! 🎉
