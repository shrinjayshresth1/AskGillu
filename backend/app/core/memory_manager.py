"""
AskGillu 2.0 — Stateful Vector Memory Engine
=============================================
Provides persistent, per-user long-term memory by storing Q&A pairs as
dense vectors in a *dedicated* Qdrant collection (srmu_user_memories) that
is completely isolated from the trusted SRMU documents index.

Architecture
------------
  save_memory(user_id, query, response)
      → Compresses the exchange into a memory text block
      → Embeds it with the same MiniLM encoder used site-wide
      → Upserts into the memory collection tagged with {user_id, timestamp}

  retrieve_memory(user_id, current_query, k=3)
      → Embeds the current query
      → Filters results by user_id metadata (exact match)
      → Returns the top-k most contextually relevant past exchanges

  get_proactive_suggestion(user_id)
      → Fetches the most recent memory vectors for the user
      → Returns structured data: last topics, last_seen timestamp

FAISS Fallback
--------------
When Qdrant is unavailable the engine falls back to an in-memory FAISS
index per user_id stored in a Python dict.  The fallback is volatile
(lost on restart) but guarantees the API still functions.
"""

import os
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ── Shared encoder (same model used by UnifiedVectorManager) ─────────────────
_ENCODER = None

def _get_encoder() -> HuggingFaceEmbeddings:
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("[MemoryManager] Encoder initialised (all-MiniLM-L6-v2)")
    return _ENCODER


# ─────────────────────────────────────────────────────────────────────────────
# Helper: build the text block that gets embedded into a single memory vector
# ─────────────────────────────────────────────────────────────────────────────
def _build_memory_text(query: str, response: str) -> str:
    """Produce a compact semantic representation of one Q&A exchange."""
    # Truncate response so a single memory chunk stays ≤ 400 tokens
    preview = response[:800] if len(response) > 800 else response
    return (
        f"Student asked: {query.strip()}\n"
        f"AskGillu answered: {preview.strip()}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# MemoryManager
# ─────────────────────────────────────────────────────────────────────────────
class MemoryManager:
    """
    Manages per-user long-term vector memory for AskGillu 2.0.

    Parameters
    ----------
    qdrant_url      : Qdrant server URL (cloud or local).  If None the engine
                      attempts to read QDRANT_URL from the environment.
    qdrant_api_key  : API key for Qdrant Cloud.  Falls back to QDRANT_API_KEY.
    collection_name : Name of the dedicated memory collection.
    vector_size     : Dimensionality of MiniLM embeddings (384).
    """

    COLLECTION = "srmu_user_memories"
    VECTOR_SIZE = 384  # all-MiniLM-L6-v2

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = COLLECTION,
        vector_size: int = VECTOR_SIZE,
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.encoder = _get_encoder()
        self._qdrant_client = None
        self._faiss_fallbacks: Dict[str, Any] = {}  # user_id → FAISS index
        self._faiss_docs: Dict[str, List[Document]] = {}  # user_id → doc list
        self._mode = "uninitialised"

        qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "")
        qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY", "")

        if qdrant_url:
            self._init_qdrant(qdrant_url, qdrant_api_key)
        else:
            logger.warning(
                "[MemoryManager] QDRANT_URL not set — using volatile in-memory FAISS fallback."
            )
            self._mode = "faiss"

    # ── Qdrant initialisation ─────────────────────────────────────────────────
    def _init_qdrant(self, url: str, api_key: str):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            kwargs: Dict[str, Any] = {"url": url, "timeout": 10}
            if api_key:
                kwargs["api_key"] = api_key

            client = QdrantClient(**kwargs)

            # Create collection if it doesn't exist yet
            existing = [c.name for c in client.get_collections().collections]
            if self.collection_name not in existing:
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(
                    f"[MemoryManager] Created Qdrant collection '{self.collection_name}'"
                )
            else:
                logger.info(
                    f"[MemoryManager] Connected to existing collection '{self.collection_name}'"
                )

            self._qdrant_client = client
            self._mode = "qdrant"

        except Exception as exc:
            logger.warning(
                f"[MemoryManager] Qdrant init failed ({exc}). Switching to FAISS fallback."
            )
            self._mode = "faiss"

    # ── Public API ─────────────────────────────────────────────────────────────
    def save_memory(self, user_id: str, query: str, response: str) -> bool:
        """
        Persist one Q&A exchange as a memory vector tagged to *user_id*.

        Returns True on success.
        """
        if not user_id or not query or not response:
            return False

        memory_text = _build_memory_text(query, response)
        vector = self.encoder.embed_query(memory_text)

        metadata = {
            "user_id": user_id,
            "query": query[:300],
            "response_preview": response[:300],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "unix_ts": time.time(),
        }

        try:
            if self._mode == "qdrant":
                return self._qdrant_save(memory_text, vector, metadata)
            else:
                return self._faiss_save(user_id, memory_text, metadata)
        except Exception as exc:
            logger.error(f"[MemoryManager] save_memory error: {exc}")
            return False

    def retrieve_memory(
        self, user_id: str, current_query: str, k: int = 3
    ) -> List[Document]:
        """
        Fetch the top-*k* past exchanges most relevant to *current_query*
        for the given *user_id*.

        Returns a list of LangChain Document objects whose `page_content`
        is the original memory text block.
        """
        if not user_id or not current_query:
            return []

        query_vector = self.encoder.embed_query(current_query)

        try:
            if self._mode == "qdrant":
                return self._qdrant_retrieve(user_id, query_vector, k)
            else:
                return self._faiss_retrieve(user_id, current_query, k)
        except Exception as exc:
            logger.error(f"[MemoryManager] retrieve_memory error: {exc}")
            return []

    def get_proactive_suggestion(self, user_id: str, k: int = 5) -> Dict[str, Any]:
        """
        Return structured data for the /welcome endpoint:
          - recent_topics: list of short query strings from last k memories
          - last_seen:     ISO timestamp of the most recent memory
          - memory_count:  total memories stored for this user
        """
        if not user_id:
            return {"recent_topics": [], "last_seen": None, "memory_count": 0}

        try:
            if self._mode == "qdrant":
                return self._qdrant_recent(user_id, k)
            else:
                return self._faiss_recent(user_id, k)
        except Exception as exc:
            logger.error(f"[MemoryManager] get_proactive_suggestion error: {exc}")
            return {"recent_topics": [], "last_seen": None, "memory_count": 0}

    # ── Qdrant internals ──────────────────────────────────────────────────────
    def _qdrant_save(
        self, memory_text: str, vector: List[float], metadata: Dict
    ) -> bool:
        from qdrant_client.models import PointStruct
        import uuid as _uuid

        point_id = str(_uuid.uuid4())
        self._qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={**metadata, "memory_text": memory_text},
                )
            ],
        )
        logger.debug(
            f"[MemoryManager] Saved memory for user '{metadata['user_id']}' → {point_id}"
        )
        return True

    def _qdrant_retrieve(
        self, user_id: str, query_vector: List[float], k: int
    ) -> List[Document]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        results = self._qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id", match=MatchValue(value=user_id)
                    )
                ]
            ),
            with_payload=True,
        )

        docs = []
        for hit in results:
            payload = hit.payload or {}
            docs.append(
                Document(
                    page_content=payload.get("memory_text", ""),
                    metadata={
                        "user_id": payload.get("user_id", user_id),
                        "timestamp": payload.get("timestamp", ""),
                        "score": hit.score,
                    },
                )
            )
        return docs

    def _qdrant_recent(self, user_id: str, k: int) -> Dict[str, Any]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Scroll to get all points for this user (up to 500) then sort by ts
        records, _ = self._qdrant_client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=500,
            with_payload=True,
        )

        if not records:
            return {"recent_topics": [], "last_seen": None, "memory_count": 0}

        sorted_records = sorted(
            records,
            key=lambda r: r.payload.get("unix_ts", 0),
            reverse=True,
        )

        recent_topics = [
            r.payload.get("query", "")
            for r in sorted_records[:k]
            if r.payload.get("query")
        ]
        last_seen = sorted_records[0].payload.get("timestamp")

        return {
            "recent_topics": recent_topics,
            "last_seen": last_seen,
            "memory_count": len(records),
        }

    # ── FAISS fallback internals ───────────────────────────────────────────────
    def _faiss_save(self, user_id: str, memory_text: str, metadata: Dict) -> bool:
        """Volatile in-memory FAISS index per user."""
        from langchain_community.vectorstores import FAISS

        doc = Document(page_content=memory_text, metadata=metadata)

        if user_id not in self._faiss_fallbacks:
            # Bootstrap a new per-user FAISS index
            self._faiss_fallbacks[user_id] = FAISS.from_documents(
                [doc], self.encoder
            )
            self._faiss_docs[user_id] = [doc]
        else:
            self._faiss_fallbacks[user_id].add_documents([doc])
            self._faiss_docs[user_id].append(doc)

        logger.debug(f"[MemoryManager][FAISS] Saved memory for user '{user_id}'")
        return True

    def _faiss_retrieve(
        self, user_id: str, query: str, k: int
    ) -> List[Document]:
        if user_id not in self._faiss_fallbacks:
            return []
        index = self._faiss_fallbacks[user_id]
        return index.similarity_search(query, k=k)

    def _faiss_recent(self, user_id: str, k: int) -> Dict[str, Any]:
        docs = self._faiss_docs.get(user_id, [])
        if not docs:
            return {"recent_topics": [], "last_seen": None, "memory_count": 0}

        sorted_docs = sorted(
            docs,
            key=lambda d: d.metadata.get("unix_ts", 0),
            reverse=True,
        )
        recent_topics = [
            d.metadata.get("query", "") for d in sorted_docs[:k] if d.metadata.get("query")
        ]
        last_seen = sorted_docs[0].metadata.get("timestamp")
        return {
            "recent_topics": recent_topics,
            "last_seen": last_seen,
            "memory_count": len(docs),
        }


# ── Singleton factory (mirrors the pattern used by other core modules) ────────
_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Return the singleton MemoryManager instance, creating it if needed."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance
