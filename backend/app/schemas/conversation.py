"""Request/response schemas for the conversational surface of the agent.

Note: these model the *interface* the agent exposes to a client. The
orchestration behind it (planning, tool execution, validation, itinerary
building) is what makes this an agent rather than a chatbot — see
app/agent/orchestrator.py.
"""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.common import MessageRole
from app.schemas.itinerary import Itinerary
from app.schemas.travel_session import TravelSession


class Message(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = Field(default_factory=list)
    travel_session: TravelSession = Field(default_factory=TravelSession)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    requires_clarification: bool = False
    missing_slots: list[str] | None = None
    itinerary: Itinerary | None = None
