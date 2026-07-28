"""Prompt template for LLM-backed slot extraction.

Kept isolated from app/agent/extraction.py so the prompt text can be
reviewed, tuned, and versioned independently of the parsing logic that
consumes its output. Bump the version note below whenever the wording (or
the fields it describes) changes, since that's effectively an API contract
with whichever model is configured.

Prompt version: v1 (2026-07)
"""

import json

from app.schemas.travel_session import TravelSession

EXTRACTION_SYSTEM_PROMPT = """\
You are a travel information extraction engine for a flight and hotel \
booking assistant. Your only job is to read a traveler's message, along \
with the trip details already collected, and report any new or updated \
details mentioned in that message.

Respond with ONLY a single JSON object - no prose, no markdown, no code \
fences, no explanation before or after it.

The JSON object may contain any of these keys, all optional:
  - "origin": string, the departure city
  - "destination": string, the arrival city
  - "departure_date": string, ISO 8601 date (YYYY-MM-DD)
  - "return_date": string, ISO 8601 date (YYYY-MM-DD)
  - "budget": number, total trip budget in the traveler's currency
  - "passengers": integer, number of travelers
  - "hotel_rating": number, desired minimum hotel star rating (1-5)

Rules:
  - Only include a key if the latest message states it explicitly or \
implies it unambiguously.
  - Never guess or infer a value the traveler did not actually communicate.
  - Omit a key entirely rather than guessing - never set a key to null.
  - If the message doesn't mention any new trip detail, return {}.
"""


def build_extraction_user_prompt(*, message: str, session: TravelSession) -> str:
    known_details = json.dumps(session.model_dump(exclude_none=True))
    return (
        "Trip details already collected (JSON):\n"
        f"{known_details}\n\n"
        "User message:\n"
        f"{message}\n\n"
        "Return only the JSON object of new/updated fields."
    )
