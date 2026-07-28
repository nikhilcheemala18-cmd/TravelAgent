"""Conversation Manager.

Owns two things: (1) ConversationState lifecycle — loading/creating a
session and recording message history — and (2) the TravelSession slot
state that lives inside it: merging newly extracted values in, reporting
which required slots are still missing, checking completeness, and
resetting the slots for a fresh search.

This module never calls a tool and never calls an LLM. Deciding *what* to
extract from a message, or *what* to do once slots are missing/complete,
is the Planner's job (app/agent/planner.py) — this module only stores and
reports state.
"""

from app.schemas.common import MessageRole
from app.schemas.conversation import ConversationState, Message
from app.schemas.travel_session import TravelSession
from app.session.store import SessionStore

# Slots that must be filled before an ExecutionPlan can be built.
# budget and hotel_rating are optional preferences, not required to plan.
REQUIRED_TRAVEL_SLOTS: tuple[str, ...] = (
    "origin",
    "destination",
    "departure_date",
    "return_date",
    "passengers",
)


class ConversationManager:
    def __init__(self, session_store: SessionStore) -> None:
        self._session_store = session_store

    # -- ConversationState / message lifecycle ---------------------------

    def get_or_create_session(self, session_id: str | None) -> ConversationState:
        if session_id:
            existing = self._session_store.get(session_id)
            if existing is not None:
                return existing

        state = (
            ConversationState()
            if session_id is None
            else ConversationState(session_id=session_id)
        )
        self._session_store.save(state)
        return state

    def add_user_message(self, state: ConversationState, content: str) -> None:
        state.messages.append(Message(role=MessageRole.USER, content=content))
        self._session_store.save(state)

    def add_assistant_message(self, state: ConversationState, content: str) -> None:
        state.messages.append(Message(role=MessageRole.ASSISTANT, content=content))
        self._session_store.save(state)

    def get_history(self, state: ConversationState) -> list[Message]:
        return state.messages

    # -- TravelSession (slot) state ---------------------------------------

    def update_session(self, session: TravelSession, updates: dict) -> TravelSession:
        """Merge newly extracted values into a TravelSession.

        Only keys with a non-None value overwrite existing data, so a
        message that doesn't mention e.g. budget never erases a
        previously captured budget.
        """
        changes = {key: value for key, value in updates.items() if value is not None}
        return session.model_copy(update=changes)

    def get_missing_slots(self, session: TravelSession) -> list[str]:
        return [
            field for field in REQUIRED_TRAVEL_SLOTS if getattr(session, field) is None
        ]

    def is_complete(self, session: TravelSession) -> bool:
        return not self.get_missing_slots(session)

    def clear_session(self, session_id: str) -> None:
        """Reset the trip details collected for a session (e.g. to start a
        new search). Message history is left intact. No-op if the session
        doesn't exist.
        """
        state = self._session_store.get(session_id)
        if state is None:
            return
        state.travel_session = TravelSession()
        self._session_store.save(state)
