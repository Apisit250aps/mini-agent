from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Iterable

from openai import OpenAI
from pymongo import MongoClient


DEFAULT_OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
DEFAULT_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
DEFAULT_MONGODB_URI = os.getenv(
    "MONGODB_URI", "mongodb://root:rootpassword@localhost:27017/?authSource=admin")
DEFAULT_MONGODB_DB = os.getenv("MONGODB_DB", "mini_agent")
DEFAULT_MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "embeddings")


def build_client() -> OpenAI:
    return OpenAI(
        base_url=DEFAULT_OLLAMA_BASE_URL,
        api_key=DEFAULT_OLLAMA_API_KEY,
    )


def get_embedding(client: OpenAI, text: str, model: str) -> list[float]:
    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding


def iter_texts(args: argparse.Namespace) -> Iterable[str]:
    if args.text:
        return args.text

    return [
        "Ollama makes local model inference simple.",
        "MongoDB stores embeddings for semantic search and retrieval.",
        "This script turns text into vectors and persists them with pymongo.",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create embeddings with Ollama and store them in MongoDB.")
    parser.add_argument(
        "text",
        nargs="*",
        help="Text to embed. If omitted, the script uses built-in sample text.",
    )
    parser.add_argument(
        "--source",
        default="cli",
        help="Source label to store with each record.",
    )
    args = parser.parse_args()

    client = build_client()
    mongo_client = MongoClient(DEFAULT_MONGODB_URI)
    collection = mongo_client[DEFAULT_MONGODB_DB][DEFAULT_MONGODB_COLLECTION]

    documents = []
    for index, text in enumerate(iter_texts(args), start=1):
        embedding = get_embedding(client, text, DEFAULT_EMBED_MODEL)
        document = {
            "text": text,
            "embedding": embedding,
            "embedding_model": DEFAULT_EMBED_MODEL,
            "source": args.source,
            "sequence": index,
            "created_at": datetime.now(timezone.utc),
        }
        documents.append(document)

    if documents:
        result = collection.insert_many(documents)
        print(
            f"Inserted {len(result.inserted_ids)} documents into {DEFAULT_MONGODB_DB}.{DEFAULT_MONGODB_COLLECTION}")


if __name__ == "__main__":
    main()
