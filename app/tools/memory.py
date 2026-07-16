from __future__ import annotations

from agents import function_tool

from app.memory.db import MongoMemoryStore
from app.memory.embedder import Embedder
from config import settings

# Shared singletons (initialised once per process)
_embedder = Embedder()
_store = MongoMemoryStore()


@function_tool
def save_memory(content: str, tags: list[str]) -> str:
    """
    Embed and save a piece of information to long-term memory.

    Use this whenever the user shares new information they want you to remember.
    Classify the memory with one or more descriptive tags. You may create any
    tags that fit the content, but common ones are:

    - "knowledge"     : general facts or new information
    - "command"       : instructions or behavioural rules the user sets
    - "personal_info" : personal details about the user (name, job, etc.)
    - "preference"    : things the user likes or dislikes
    - "other"         : anything that does not fit the above categories

    Args:
        content: The text content to remember (in the user's language).
        tags:    One or more descriptive tags for classifying this memory.
                 Example: ["personal_info", "preference"]
    """
    embedding = _embedder.embed(content)
    _store.save(
        content=content,
        tags=tags,
        embedding=embedding,
        embedding_model=settings.OLLAMA_EMBED_MODEL,
    )
    tag_display = ", ".join(tags)
    return f"✅ บันทึกความจำเรียบร้อยแล้วนะคะ (tags: {tag_display})"


@function_tool
def recall_memory(query: str) -> str:
    """
    Search long-term memory for information relevant to the query.

    Call this before formulating a response whenever the user's message may
    relate to something they told you in a previous session, to provide a
    context-aware and personalised reply.

    Args:
        query: A natural-language description of what to look for in memory.

    Returns:
        A formatted list of the most relevant memories, or a message
        indicating that nothing relevant was found.
    """
    embedding = _embedder.embed(query)
    results = _store.search(embedding, top_k=3)

    if not results:
        return "ไม่พบข้อมูลที่เกี่ยวข้องในความจำ"

    lines: list[str] = []
    for doc in results:
        tags_str = ", ".join(doc.get("tags", []))
        lines.append(f"- [{tags_str}] {doc['content']}")

    return "ข้อมูลที่พบในความจำ:\n" + "\n".join(lines)
