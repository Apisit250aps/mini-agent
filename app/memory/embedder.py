from __future__ import annotations

from openai import OpenAI

from config import settings


class Embedder:
    """Wrapper around Ollama embeddings API."""

    def __init__(self) -> None:
        self._client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key=settings.OLLAMA_API_KEY,
        )
        self._model = settings.OLLAMA_EMBED_MODEL

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text."""
        response = self._client.embeddings.create(model=self._model, input=text)
        return response.data[0].embedding
