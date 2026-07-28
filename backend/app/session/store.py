"""Session/conversation state persistence.

Abstracted behind an interface so the in-memory implementation used for
development can be swapped for Redis/a database without touching the
ConversationManager that depends on it.
"""

from abc import ABC, abstractmethod

from app.schemas.conversation import ConversationState


class SessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> ConversationState | None:
        """Fetch existing conversation state, or None if unknown."""

    @abstractmethod
    def save(self, state: ConversationState) -> None:
        """Persist (create or update) conversation state."""


class InMemorySessionStore(SessionStore):
    """Process-local store. Fine for local dev; not shared across workers.

    TODO: replace with a Redis-backed implementation for multi-worker /
    multi-instance deployments.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get(self, session_id: str) -> ConversationState | None:
        return self._sessions.get(session_id)

    def save(self, state: ConversationState) -> None:
        self._sessions[state.session_id] = state
