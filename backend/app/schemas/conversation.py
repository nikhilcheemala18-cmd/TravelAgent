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


class Message(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TripContextSlots(BaseModel):
    """Structured info the agent has extracted/confirmed from the conversation.

    Populated incrementally by the planner/conversation manager as the user
    provides details. Left mostly empty until slot-filling logic exists.
    """

    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    travelers: int | None = None
    budget: float | None = None
    currency: str | None = None
    needs_hotel: bool | None = None
    needs_car_rental: bool | None = None


class ConversationState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = Field(default_factory=list)
    context: TripContextSlots = Field(default_factory=TripContextSlots)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    requires_clarification: bool = False
    itinerary: Itinerary | None = None
