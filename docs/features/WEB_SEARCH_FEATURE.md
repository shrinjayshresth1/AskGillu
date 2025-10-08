# Web Search Feature Test

## Test Cases

### 1. Document-only search (web search OFF)
- Question: "What is SRMU?"
- Expected: Answer based only on university documents

### 2. Web search enabled (web search ON)  
- Question: "What is artificial intelligence?"
- Expected: Answer combining web search results with document context

### 3. Mixed search (web search ON)
- Question: "What courses does SRMU offer in AI?"
- Expected: Answer combining SRMU documents with current web information

## Usage Instructions

1. **Document Search Only**: Keep the "Include Web Search" toggle OFF
   - Searches only SRMU documents
   - Faster response
   - University-specific information

2. **Web Search Enabled**: Turn the "Include Web Search" toggle ON
   - Searches both SRMU documents AND the internet
   - More comprehensive answers
   - Current information from web

## Features Added

✅ **Web Search Toggle**: Easy on/off switch for web search
✅ **DuckDuckGo Integration**: Privacy-focused search engine
✅ **Combined Results**: Merges document and web search results
✅ **Source Indication**: AI indicates which sources were used
✅ **Secure**: No additional API keys required for DuckDuckGo
✅ **Markdown Support**: Results formatted with proper markdown

## How It Works

1. **User asks a question** with web search enabled
2. **Backend searches** both SRMU documents and the web
3. **LLM combines** information from both sources
4. **AI provides** a comprehensive answer with source indication

## Future Enhancements

- Add Tavily Search API for more professional results
- Add SerpAPI for Google search results
- Add search result caching
- Add source link references
- Add search result filtering
