import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json
from datetime import datetime

class WebScraper:
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape a single URL and return structured content"""
        try:
            print(f"🕷️ Scraping: {url}")
            
            # Try newspaper3k first for better article extraction
            try:
                from newspaper import Article
                article = Article(url)
                article.download()
                article.parse()
                
                if article.text and len(article.text.strip()) > 100:
                    return {
                        'url': url,
                        'title': article.title or self._extract_title_from_url(url),
                        'content': article.text,
                        'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                        'authors': article.authors,
                        'summary': article.summary[:500] if article.summary else None,
                        'scraped_at': datetime.now().isoformat(),
                        'word_count': len(article.text.split()),
                        'method': 'newspaper3k'
                    }
            except ImportError:
                print("📰 newspaper3k not available, using BeautifulSoup fallback")
            except Exception as e:
                print(f"📰 newspaper3k failed for {url}: {e}")
            
            # Fallback to BeautifulSoup
            return self._scrape_with_bs4(url)
                
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def _scrape_with_bs4(self, url: str) -> Optional[Dict]:
        """Fallback scraping method using BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'sidebar', 'advertisement', 'aside']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else self._extract_title_from_url(url)
            
            # Extract main content using various selectors
            content_selectors = [
                'article', 'main', '.content', '.post-content', 
                '.entry-content', '.article-content', '.post-body',
                '.article-body', '.story-body', '.news-content',
                '.blog-content', '.page-content', '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # If no specific content area found, get body text
            if not content or len(content.strip()) < 50:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # Clean up content
            content = ' '.join(content.split())
            
            if len(content.strip()) < 100:
                return None
                
            return {
                'url': url,
                'title': title,
                'content': content,
                'publish_date': None,
                'authors': [],
                'summary': content[:500] + '...' if len(content) > 500 else content,
                'scraped_at': datetime.now().isoformat(),
                'word_count': len(content.split()),
                'method': 'beautifulsoup'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title from URL if no title is found"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if path:
            return path.replace('-', ' ').replace('_', ' ').title()
        return parsed.netloc
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs with rate limiting"""
        results = []
        
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_url(url)
            if result:
                results.append(result)
                print(f"✅ Successfully scraped: {result['title'][:50]}... ({result['word_count']} words)")
            else:
                print(f"❌ Failed to scrape: {url}")
            
            # Rate limiting
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        return results
    
    def discover_urls_from_sitemap(self, domain: str) -> List[str]:
        """Try to discover URLs from sitemap"""
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/robots.txt"
        ]
        
        discovered_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    if 'sitemap' in sitemap_url:
                        # Parse XML sitemap
                        soup = BeautifulSoup(response.content, 'xml')
                        urls = soup.find_all('loc')
                        discovered_urls.extend([url.get_text() for url in urls])
                    else:
                        # Parse robots.txt
                        lines = response.text.split('\n')
                        for line in lines:
                            if line.startswith('Sitemap:'):
                                sitemap_url = line.split(':', 1)[1].strip()
                                discovered_urls.append(sitemap_url)
                break
            except Exception as e:
                print(f"Failed to access {sitemap_url}: {e}")
                continue
        
        return discovered_urls[:50]  # Limit to 50 URLs

    def get_page_links(self, url: str, same_domain_only: bool = True) -> List[str]:
        """Extract links from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            base_domain = urlparse(url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if same_domain_only:
                    if urlparse(full_url).netloc == base_domain:
                        links.append(full_url)
                else:
                    links.append(full_url)
            
            # Remove duplicates and sort
            return list(set(links))[:100]  # Limit to 100 links
            
        except Exception as e:
            print(f"Failed to get links from {url}: {e}")
            return []
