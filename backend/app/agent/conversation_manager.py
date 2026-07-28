"""Conversation Manager.

Owns conversation state: retrieving/creating sessions, appending messages,
and updating extracted trip context (slots). Deliberately dumb — it does
not decide *what* to do about a message, only records the conversation and
exposes it. Deciding what to do is the AgentPlanner's job.
"""

from app.schemas.common import MessageRole
from app.schemas.conversation import ConversationState, Message, TripContextSlots
from app.session.store import SessionStore


class ConversationManager:
    def __init__(self, session_store: SessionStore) -> None:
        self._session_store = session_store

    def get_or_create_session(self, session_id: str | None) -> ConversationState:
        if session_id:
            existing = self._session_store.get(session_id)
            if existing is not None:
                return existing

        state = ConversationState() if session_id is None else ConversationState(session_id=session_id)
        self._session_store.save(state)
        return state

    def add_user_message(self, state: ConversationState, content: str) -> None:
        state.messages.append(Message(role=MessageRole.USER, content=content))
        self._session_store.save(state)

    def add_assistant_message(self, state: ConversationState, content: str) -> None:
        state.messages.append(Message(role=MessageRole.ASSISTANT, content=content))
        self._session_store.save(state)

    def update_context(self, state: ConversationState, updates: dict) -> None:
        """Merge extracted slot values (origin, destination, dates, ...) into state.

        TODO: called today with an empty/placeholder dict. Once the planner
        performs real slot extraction, pass its output through here.
        """
        state.context = TripContextSlots(**{**state.context.model_dump(), **updates})
        self._session_store.save(state)

    def get_history(self, state: ConversationState) -> list[Message]:
        return state.messages
