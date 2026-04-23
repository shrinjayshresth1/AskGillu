# AskGillu 2.0 - Mermaid Diagrams

These are the raw Mermaid code blocks for all the diagrams used in the project report. You can copy the code inside each block and paste it directly into the [Mermaid Live Editor](https://mermaid.live/) to generate images for your LaTeX document.

---

### Figure 3.1: High-Level System Architecture of AskGillu 2.0

```mermaid
graph TB
    subgraph "Presentation Layer - React Frontend"
        A[User Browser]
        B[React App.js]
        C[ChatMessage Component]
        D[VectorDatabaseToggle]
        E[HomePage + TeamSection]
    end

    subgraph "Logic Layer - FastAPI Backend"
        F[FastAPI Server :8000]
        G[POST /ask - Standard RAG]
        H[POST /ask-agentic - Agentic RAG]
        I[POST /ask-image - Vision RAG]
        J[POST /reindex - Re-Ingestion]
        K[POST /api/vector-db/switch]
        L[Translator Module hi↔en]
        M[Context Relevance Gate]
        N[Prompt Builder]
    end

    subgraph "AI / ML Layer"
        O[LLaMA-3.3-70B via Groq API]
        P[LLaMA-3.2-11B Vision via Groq]
        Q[all-MiniLM-L6-v2 Embeddings]
        R[Tavily Web Search API]
        S[DuckDuckGo Fallback]
    end

    subgraph "Data Layer"
        T[UnifiedVectorManager]
        U[Qdrant Cloud - Primary]
        V[FAISS Local Index - Fallback]
        W[docs/ PDF Store]
        X[Hybrid Search Engine BM25+Vector]
        Y[Response Cache]
        Z[Feedback Loop]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --HTTP POST--> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    G --> L
    H --> L
    L --> M
    M --> N
    N --> O
    G --> T
    H --> T
    T --> X
    X --> U
    X --> V
    X --> Y
    T --> Z
    J --> W
    W --> Q
    Q --> U
    Q --> V
    O --> F
    H --> R
    R --> S
    I --> P
```

---

### Figure 3.2: Standard (Non-Agentic) RAG Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant React as React Frontend
    participant API as FastAPI /ask
    participant Trans as Translator
    participant Gate as Context Gate
    participant Vec as UnifiedVectorManager
    participant Tavily as Tavily Web Search
    participant LLM as LLaMA-3.3-70B (Groq)

    User->>React: Types Question (EN or HI)
    React->>API: POST /ask {question, system_prompt, use_web_search, language}
    API->>Trans: translate_query_to_english(q, lang)
    Trans-->>API: processed_question (always EN)
    API->>Vec: similarity_search(question, k=5)
    Vec-->>API: (docs: List[Document], metadata: {documents_found: N})
    
    alt use_web_search == True
        API->>Tavily: search(query, include_domains=["srmu.ac.in"])
        Tavily-->>API: Web context snippets
    end

    API->>Gate: documents_found == 0 AND no_web_context?
    
    alt Context Empty → Gate BLOCKS
        Gate-->>React: Canned Refusal Message
    else Context Found → Gate PASSES
        Gate->>LLM: full_prompt (system_prompt + strict_rules + context + question)
        Note over LLM: temperature=0.0, model=llama-3.3-70b
        LLM-->>API: Grounded Answer
        API->>Trans: translate_response_to_hindi (if lang==hi)
        API-->>React: {answer, sources_used, rag_features, language}
    end
    React-->>User: Renders formatted Markdown answer
```

---

### Figure 3.3: Agentic RAG Pipeline with Tool Dispatch

```mermaid
sequenceDiagram
    participant User
    participant React as React Frontend (Agentic Toggle ON)
    participant API as FastAPI /ask-agentic
    participant IC as Intent Classifier
    participant TR as Tool Registry
    participant RAG as Standard RAG Pipeline
    participant LLM as LLaMA-3.3-70B (Groq)

    User->>React: Toggle Agentic ON; Ask Question
    React->>API: POST /ask-agentic {question, system_prompt, language}
    API->>IC: classify_intent(question, llm)
    
    Note over IC: LLM classifies intent:<br/>web_search | rag_only | schedule_query | etc.

    alt Intent == tool (e.g. web_search)
        IC-->>API: {intent: "web_search", args: {query: "..."}}
        API->>TR: execute_tool("web_search", args)
        TR-->>API: tool_result: {message: "...", data: {...}}
    else Intent == "rag_only"
        IC-->>API: {intent: "rag_only", args: {}}
    end

    API->>RAG: combine_sources(question, use_web_search=False)
    RAG-->>API: (context, {documents_found: N})

    alt intent=="rag_only" AND docs_found==0
        API-->>React: Canned Refusal
    else Context or Tool Result Available
        API->>LLM: full_prompt (context + tool_result + strict rules)
        LLM-->>API: Grounded Answer
        API-->>React: {answer, agent_action, intent, sources_used}
    end

    React-->>User: Answer + Agent Action Card displayed
```

---

### Figure 3.4: UnifiedVectorManager Component Architecture

```mermaid
classDiagram
    class UnifiedVectorManager {
        +db_type: str
        +use_hybrid_search: bool
        +enable_semantic_chunking: bool
        +enable_response_caching: bool
        +enable_feedback_tracking: bool
        +embeddings: HuggingFaceEmbeddings
        +vector_store: QdrantManager | FAISS
        +hybrid_retriever: HybridSearchRetriever
        +semantic_chunker: SemanticChunker
        +response_cache: ResponseCache
        +feedback_loop: FeedbackLoop
        +documents_cache: List[Document]

        +similarity_search(query, k) Tuple
        +add_documents(texts, metadatas) bool
        +switch_database(new_db_type) bool
        +get_status() Dict
        +clear_database() bool
        +bulk_add_documents(docs, batch_size) bool
        +rechunk_documents(method) Dict
        +get_performance_metrics() Dict
    }

    class HuggingFaceEmbeddings {
        +model_name: "all-MiniLM-L6-v2"
        +device: "cpu"
        +normalize_embeddings: True
        +encode(texts) List[float]
    }

    class QdrantManager {
        +url: str
        +api_key: str
        +collection_name: "askgillu_documents"
        +vector_size: 384
        +similarity_search(query, k) List[Document]
        +add_documents(texts, metadatas) bool
        +delete_collection() bool
        +create_collection() bool
        +health_check() Tuple[bool, str]
    }

    class FAISSIndex {
        +index_path: "./vectorstore/db_faiss"
        +similarity_search(query, k) List[Document]
        +add_texts(texts, metadatas) bool
        +save_local(path) void
    }

    class HybridSearchRetriever {
        +bm25_weight: 0.3
        +vector_weight: 0.7
        +fit(documents) void
        +search(query, k, use_advanced_rerank) List[Document]
        +update_weights(bm25, vector) void
    }

    class SemanticChunker {
        +max_chunk_size: 2000
        +min_chunk_size: 100
        +overlap_sentences: 2
        +chunk_document(text, metadata) List[Document]
    }

    class ResponseCache {
        +max_cache_size: 1000
        +default_ttl_hours: 24
        +similarity_threshold: 0.85
        +get(query, k) Optional[Tuple]
        +put(query, docs, k, metadata) void
    }

    class FeedbackLoop {
        +retention_days: 90
        +record_feedback(query, docs, type) str
        +get_feedback_summary(days) Dict
    }

    UnifiedVectorManager --> HuggingFaceEmbeddings
    UnifiedVectorManager --> QdrantManager
    UnifiedVectorManager --> FAISSIndex
    UnifiedVectorManager --> HybridSearchRetriever
    UnifiedVectorManager --> SemanticChunker
    UnifiedVectorManager --> ResponseCache
    UnifiedVectorManager --> FeedbackLoop
```

---

### Figure 3.5: Hybrid Search Engine Architecture (BM25 + Vector)

```mermaid
graph TD
    Q[User Query] --> VE[Vector Embedding\n all-MiniLM-L6-v2]
    Q --> BM[BM25 Tokenizer\n Term Frequency]

    VE --> VS{Vector Store\nQdrant or FAISS}
    VS --> VR[Vector Results\n Top-K by cosine similarity]

    BM --> BR[BM25 Results\n Top-K by TF-IDF score]

    VR --> RRF[Reciprocal Rank Fusion\n RRF Score = Σ 1/(k + rank_i)]
    BR --> RRF

    RRF --> AR[Advanced Re-Ranker]
    AR --> |strategy: rrf / semantic / diversity| FR[Final Top-5 Documents]

    FR --> CTX[Context Assembly\n UNIVERSITY DOCUMENTS: ...]
```

---

### Figure 3.6: Context Relevance Gating Mechanism

```mermaid
flowchart TD
    A[Query Received] --> B[Vector Similarity Search\n k=5 documents]
    B --> C{documents_found > 0?}
    C -- No --> D{Web Search\n Enabled?}
    D -- No --> E["⛔ GATE BLOCKS\nReturn: Sorry, I don't have\nenough information..."]
    D -- Yes --> F[Tavily Search\n restricted to srmu.ac.in]
    F --> G{Web results\nfound?}
    G -- No --> E
    G -- Yes --> H[✅ GATE PASSES\nContext = Web Results]
    C -- Yes --> H
    H --> I[Build Full Prompt\n system_prompt + rules + context]
    I --> J[LLaMA-3.3-70B\n temperature=0.0]
    J --> K[Grounded Answer]
```

---

### Figure 3.7: Document Ingestion and Chunking Pipeline

```mermaid
flowchart LR
    A[PDF Document\n in /docs/] --> B[Advanced PDF Parser\n hybrid: pypdf + pdfminer]
    B --> C{Table\nExtraction?}
    C -- Yes --> D[Table Text Serialization]
    C -- No --> E[Plain Text Extraction]
    D --> F[Raw Text]
    E --> F
    F --> G[RecursiveCharacterTextSplitter\nchunk_size=8000\nchunk_overlap=1200]
    G --> H[Text Chunks\n List of str]
    H --> I[HuggingFace Embeddings\n all-MiniLM-L6-v2\n 384-dim vectors]
    I --> J{Target DB?}
    J -- Qdrant --> K[Qdrant Cloud\n collection: askgillu_documents]
    J -- FAISS --> L[FAISS Index\n ./vectorstore/db_faiss]
    K --> M[Metadata: source, chunk_id, processed_at]
    L --> M
```

---

### Figure 3.8: Level-0 Data Flow Diagram

```mermaid
flowchart LR
    U([Student / Faculty\nUser]) -- Query + Language --> S[AskGillu 2.0\nSystem]
    S -- Grounded Answer + Sources --> U
    A([University Admin]) -- New PDF Documents --> S
    S -- Indexed Knowledge Base --> DB[(SRMU\nKnowledge Base)]
    DB -- Retrieved Context --> S
    W([SRMU Website\nsrmu.ac.in]) -- Web Content\n via Tavily --> S
```

---

### Figure 3.9: Level-1 Data Flow Diagram (RAG Pipeline)

```mermaid
flowchart TD
    U([User]) --> P1[1.0\nQuery\nProcessing]
    P1 --> P2[2.0\nContext\nRetrieval]
    P1 --> P3[3.0\nWeb Search\nOptional]
    P2 --> P4[4.0\nContext\nGating]
    P3 --> P4
    P4 --> P5[5.0\nPrompt\nConstruction]
    P5 --> P6[6.0\nLLM\nInference]
    P6 --> P7[7.0\nTranslation\nOptional]
    P7 --> U

    P1 -.->|Translated Query EN| DS1[(Translation\nCache)]
    P2 -.->|Search| DS2[(Qdrant Cloud /\nFAISS Index)]
    DS2 -.->|Documents| P2
    P3 -.->|API Call| DS3[(Tavily\nsrmu.ac.in)]
    DS3 -.->|Web Results| P3
    P4 -.->|Gate Decision| DS4[(Audit Log)]
    P6 -.->|Cache Entry| DS5[(Response\nCache)]
```

---

### Figure 3.10: REST API Endpoint Map

```mermaid
graph LR
    subgraph "Core Query Endpoints"
        A[POST /ask]
        B[POST /ask-agentic]
        C[POST /ask-image]
    end

    subgraph "Knowledge Base Management"
        D[POST /reindex]
        E[POST /ingest]
        F[POST /api/documents/upload]
        G[POST /api/documents/add-text]
    end

    subgraph "Vector DB Control"
        H[GET /api/vector-db/current]
        I[POST /api/vector-db/switch]
        J[GET /api/vector-db/status]
    end

    subgraph "Web Scraping"
        K[POST /scrape-websites]
        L[POST /scrape-single-website]
        M[GET /scraped-data]
    end

    subgraph "Analytics & Monitoring"
        N[GET /api/analytics/performance]
        O[GET /api/analytics/feedback]
        P[POST /api/feedback]
        Q[GET /api/cache/stats]
        R[POST /api/cache/clear]
    end

    subgraph "System"
        S[GET /status]
        T[GET /watcher-status]
    end
```

---

### Figure 3.11: Qdrant Collection and FAISS Index Schema

```mermaid
erDiagram
    QDRANT_COLLECTION {
        uuid id PK
        vector float384 "384-dim MiniLM embedding"
        string page_content "Document text chunk"
        string source "srmu_documents"
        int chunk_id "Sequential chunk index"
        datetime processed_at "Ingestion timestamp"
        string chunk_type "realtime_ingest or pdf"
    }

    FAISS_INDEX {
        int faiss_id PK "Internal FAISS index"
        vector float384 "384-dim MiniLM embedding"
        string page_content "Document text chunk"
        string source "File name"
    }

    RESPONSE_CACHE {
        string query_hash PK "SHA256 of query"
        string query "Original query text"
        json documents "Cached document list"
        float relevance_score
        datetime expires_at "TTL: created + 24h"
        int hit_count
    }

    FEEDBACK_LOG {
        uuid feedback_id PK
        string query "User's original question"
        string feedback_type "relevant|irrelevant|correction"
        float relevance_score "0.0 to 1.0"
        float response_quality "0.0 to 1.0"
        datetime created_at
        string user_session "Optional session ID"
    }

    QDRANT_COLLECTION ||--o{ RESPONSE_CACHE : "query results cached in"
    QDRANT_COLLECTION ||--o{ FEEDBACK_LOG : "search produces feedback for"
```

---

### Figure 3.12: React Component Tree

```mermaid
graph TD
    A["index.js\n(Entry Point)"] --> B["App.js\n(Root Component)\nState: messages, isLoading,\nuseWebSearch, isAgentic,\ncurrentLanguage, dbType"]

    B --> C["HomePage.js\n(Main Chat Interface)"]
    B --> D["Navbar.js\n(Top Navigation)"]
    B --> E["Footer.js\n(Version Badge)"]

    C --> F["ChatMessage.js\n(Per-Message Card)\nProps: role, content, timestamp"]
    C --> G["VectorDatabaseToggle.js\n(DB Switcher)\nState: currentDb, isLoading, docCount"]
    C --> H["Language Toggle\n(EN / HI switcher)"]
    C --> I["Agentic Toggle\n(Standard / Agentic)"]
    C --> J["Web Search Toggle\n(Globe Icon + Domain Badge)"]
    C --> K["Input Area\n(Textarea + Send + Attach)"]

    style B fill:#1a1a3e,color:#fff
    style C fill:#2d2d5e,color:#fff
    style G fill:#3d1a5e,color:#fff
```

---

### Figure 3.13: Anti-Hallucination Layer Architecture

```mermaid
flowchart TD
    A[User Query] --> L1

    subgraph L1["Layer 1: Domain Restriction"]
        B[Web search restricted to srmu.ac.in only\nvia Tavily include_domains parameter]
    end

    L1 --> L2

    subgraph L2["Layer 2: Context Relevance Gate"]
        C{documents_found > 0\nOR web context found?}
        C -- No --> D[⛔ Return canned refusal\nNEVER call LLM]
        C -- Yes --> E[Proceed to LLM]
    end

    L2 --> L3

    subgraph L3["Layer 3: Strict Prompt Grounding"]
        F["IMPORTANT RULES:
        1. Answer ONLY using provided CONTEXT
        2. NEVER fabricate facts, statistics, dates
        3. If unsure, say 'I don't know'
        4. Reference source when possible"]
    end

    L3 --> L4

    subgraph L4["Layer 4: Deterministic LLM Config"]
        G[Model: llama-3.3-70b-versatile\ntemperature = 0.0\n70B parameters for instruction-following]
    end

    L4 --> H[Grounded, Verifiable Answer]

    style D fill:#8b0000,color:#fff
    style H fill:#006400,color:#fff
```
