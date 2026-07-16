from __future__ import annotations

import math
from datetime import datetime, timezone

from pymongo import MongoClient

from config import settings


class MongoMemoryStore:
    """MongoDB-backed memory store with cosine-similarity search."""

    def __init__(self) -> None:
        self._client: MongoClient = MongoClient(settings.MONGODB_URI)
        self._collection = (
            self._client[settings.MONGODB_DB][settings.MONGODB_MEMORY_COLLECTION]
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(
        self,
        content: str,
        tags: list[str],
        embedding: list[float],
        embedding_model: str,
    ) -> None:
        """Insert a memory document into the collection."""
        doc = {
            "content": content,
            "tags": tags,
            "embedding": embedding,
            "embedding_model": embedding_model,
            "source": "agent",
            "created_at": datetime.now(timezone.utc),
        }
        self._collection.insert_one(doc)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        filter_tags: list[str] | None = None,
    ) -> list[dict]:
        """
        Return the top-k most similar documents using cosine similarity.

        Args:
            query_embedding: The embedding vector to compare against.
            top_k: Maximum number of results to return.
            filter_tags: If provided, only consider documents whose 'tags'
                         field contains at least one of the given tags.
        """
        mongo_filter: dict = {}
        if filter_tags:
            mongo_filter["tags"] = {"$in": filter_tags}

        projection = {"_id": 0, "embedding": 1, "content": 1, "tags": 1, "created_at": 1}
        docs = list(self._collection.find(mongo_filter, projection))

        if not docs:
            return []

        scored = [
            (_cosine_similarity(query_embedding, doc["embedding"]), doc)
            for doc in docs
            if doc.get("embedding")
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
