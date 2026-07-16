from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pymongo import MongoClient

from config import settings

if TYPE_CHECKING:
    from agents import RunResult


class ChatLogger:
    """
    Logs per-turn chat metrics to MongoDB.

    Schema (one document per turn):
    {
        "session_id":   str,       # UUID7 — shared for the whole chat session
        "user_content": str,       # raw message the user sent
        "duration_ms":  int,       # wall-clock time for Runner.run() in milliseconds
        "token_in":     int,       # total input tokens across all LLM calls in the turn
        "token_out":    int,       # total output tokens across all LLM calls in the turn
        "timestamp":    datetime,  # UTC time this turn was logged
    }
    """

    def __init__(self) -> None:
        self._client: MongoClient = MongoClient(settings.MONGODB_URI)
        self._collection = (
            self._client[settings.MONGODB_DB][settings.MONGODB_CHAT_COLLECTION]
        )
        self.session_id: str = str(uuid.uuid7())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_turn(
        self,
        user_content: str,
        result: RunResult,
        duration_ms: int,
        model_name: str,
        output_content: str,
    ) -> None:
        """
        Persist a single chat turn to MongoDB.

        Args:
            user_content:   The user's raw message text.
            result:         The RunResult returned by Runner.run().
            duration_ms:    Wall-clock processing time in milliseconds.
            model_name:     The LLM model name used for this turn.
            output_content: The final reply text from the agent.
        """
        token_in, token_out = self._extract_tokens(result)

        doc = {
            "session_id": self.session_id,
            "model_name": model_name,
            "user_content": user_content,
            "output_content": output_content,
            "duration_ms": duration_ms,
            "token_in": token_in,
            "token_out": token_out,
            "timestamp": datetime.now(timezone.utc),
        }
        self._collection.insert_one(doc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_tokens(result: RunResult) -> tuple[int, int]:
        """Sum up input/output tokens across all raw LLM responses in a turn."""
        token_in = sum(
            r.usage.input_tokens
            for r in result.raw_responses
            if r.usage and r.usage.input_tokens
        )
        token_out = sum(
            r.usage.output_tokens
            for r in result.raw_responses
            if r.usage and r.usage.output_tokens
        )
        return token_in, token_out
