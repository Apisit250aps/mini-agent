from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Iterable

from openai import OpenAI
from pymongo import MongoClient

from config import settings

DEFAULT_OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
DEFAULT_OLLAMA_API_KEY = settings.OLLAMA_API_KEY
DEFAULT_EMBED_MODEL = settings.OLLAMA_EMBED_MODEL
DEFAULT_MONGODB_URI = settings.MONGODB_URI
DEFAULT_MONGODB_DB = settings.MONGODB_DB
DEFAULT_MONGODB_COLLECTION = settings.MONGODB_COLLECTION


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
