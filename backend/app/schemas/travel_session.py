"""TravelSession — the trip-planning slot state the agent builds up over a
conversation.

Pure data: it holds whatever has been confirmed so far and nothing else.
Deciding which fields are required, merging in new values, and checking
completeness are ConversationManager's job (app/agent/conversation_manager.py),
not this model's.
"""

from pydantic import BaseModel


class TravelSession(BaseModel):
    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    budget: float | None = None
    passengers: int | None = None
    hotel_rating: float | None = None
