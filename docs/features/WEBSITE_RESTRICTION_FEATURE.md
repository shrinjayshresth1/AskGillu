# Website Restriction Feature

The ASK_GILLU system now supports restricting web searches to only specific, trusted websites. This feature ensures that when web search is enabled, the AI only retrieves information from reliable, authoritative sources.

## How It Works

The system maintains a configurable list of allowed websites in the `backend/main.py` file. When web search is enabled:

1. **If `ALLOWED_WEBSITES` is empty**: The system searches all websites on the internet (unrestricted mode)
2. **If `ALLOWED_WEBSITES` contains domains**: The system only searches from those specific websites

## Configuration

### Adding Trusted Websites

Edit the `ALLOWED_WEBSITES` list in `backend/main.py`:

```python
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
    
    # Add more trusted websites here
    # "your-trusted-site.com",
]
```

### Domain Matching Rules

- **Exact domain**: `"wikipedia.org"` matches only Wikipedia
- **Top-level domain**: `"edu"` matches any .edu domain (universities)
- **Subdomain**: `"scholar.google.com"` matches Google Scholar specifically
- **Government**: `"gov"` matches any .gov domain (government sites)

### Disabling Restrictions

To allow searching all websites, simply empty the list:

```python
ALLOWED_WEBSITES = []
```

## Benefits

### ✅ Advantages of Restricted Search

1. **Reliability**: Only trusted, authoritative sources
2. **Academic Quality**: Educational and scholarly sources prioritized
3. **Reduced Misinformation**: Filters out unreliable websites
4. **Institutional Compliance**: Meets academic standards
5. **Faster Results**: Smaller search space means quicker responses

### ⚠️ Considerations

1. **Limited Scope**: May miss some relevant information from non-listed sites
2. **Maintenance**: List needs periodic review and updates
3. **Context Dependent**: Different topics may need different trusted sources

## Pre-configured Trusted Sources

The system comes pre-configured with these categories of trusted websites:

### 📚 Educational & Academic
- Wikipedia (general knowledge)
- All .edu domains (universities)
- Google Scholar (academic papers)
- ResearchGate (research publications)
- arXiv (scientific preprints)
- IEEE (engineering & technology)
- ACM (computer science)

### 📰 News & Media
- BBC (international news)
- Reuters (news agency)
- Nature (scientific journal)
- Science.org (AAAS publications)

### 🏛️ Government & Official
- All .gov domains (government sites)
- WHO (World Health Organization)
- UN (United Nations)

### 💻 Technology & Documentation
- Stack Overflow (programming Q&A)
- GitHub (code repositories)
- Python documentation
- Mozilla Developer Network

## Usage Examples

### For University-specific Questions
```
Question: "What is the admission process for SRMU?"
Result: Searches SRMU documents + trusted educational websites only
```

### For General Academic Topics
```
Question: "Explain machine learning algorithms"
Result: Searches SRMU documents + Wikipedia, .edu sites, academic journals
```

### For Current Events (Academic Context)
```
Question: "Latest developments in AI research"
Result: Searches SRMU documents + BBC, Nature, academic sources
```

## Monitoring and Feedback

The frontend displays the restriction status:
- 🔒 "Web search is restricted to X trusted websites" (when restricted)
- 🌐 "Web search is unrestricted" (when not restricted)

Search results include a note about restrictions:
```
[Search limited to trusted websites: wikipedia.org, edu, scholar.google.com...]
```

## Best Practices

1. **Regular Review**: Periodically review and update the allowed websites list
2. **Subject-specific Lists**: Consider different lists for different academic subjects
3. **Quality Control**: Verify new websites before adding them to the list
4. **Documentation**: Keep track of why specific websites were added
5. **Testing**: Test search results after configuration changes

## Technical Implementation

The restriction is implemented at two levels:

1. **Query Construction**: Adds `site:domain.com` restrictions to the search query
2. **Result Filtering**: Double-checks results to ensure they're from allowed domains

This dual approach ensures maximum reliability and prevents any bypassing of restrictions.

## Customization for Different Institutions

Other institutions can easily customize this for their needs:

```python
# Example: Medical School Configuration
ALLOWED_WEBSITES = [
    "pubmed.ncbi.nlm.nih.gov",
    "who.int",
    "cdc.gov",
    "nih.gov",
    "bmj.com",
    "thelancet.com",
    "nejm.org",
    "edu"  # Medical schools
]

# Example: Engineering College Configuration
ALLOWED_WEBSITES = [
    "ieee.org",
    "acm.org",
    "github.com",
    "stackoverflow.com",
    "arxiv.org",
    "edu",
    "asme.org",
    "techcrunch.com"
]
```

This feature ensures that your AI assistant provides reliable, trustworthy information while maintaining the flexibility to search the broader internet when needed.
