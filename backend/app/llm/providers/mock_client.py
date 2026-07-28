"""Deterministic offline LLM client.

Used when LLM_PROVIDER=mock (the default) so the whole agent runs
end-to-end without any API credentials — the same role MOCK_MODE already
plays for app/tools/*. It makes no network calls.

It only knows how to answer the one prompt shape the agent currently
sends (see app/agent/prompts/extraction.py): given "trip details already
collected" + "user message", pull out any newly mentioned trip details
with the same regex heuristics Phase 2's RegexSlotExtractor used, and
return them as a JSON object — mimicking exactly what a real LLM is
instructed to return, so it's a valid stand-in for local dev/tests.
"""

import json
import re

from app.llm.base import LLMClient

_USER_MESSAGE_MARKER = "User message:\n"

_ROUTE_RE = re.compile(
    r"\bfrom\s+(?P<origin>[a-zA-Z\s]+?)\s+to\s+(?P<destination>[a-zA-Z\s]+?)"
    r"(?=[.,!?]|\s+(?:on|for|with|departing|leaving|returning|from|budget)\b|$)",
    re.IGNORECASE,
)
_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_PASSENGERS_RE = re.compile(
    r"\b(\d+)\s*(?:passengers?|people|travelers?|adults?|pax)\b", re.IGNORECASE
)
_BUDGET_RE = re.compile(
    r"(?:budget(?:\s+of)?\s+\$?|\$)\s?(\d[\d,]*(?:\.\d+)?)\s*(?:dollars|usd)?",
    re.IGNORECASE,
)
_HOTEL_RATING_RE = re.compile(r"\b(\d(?:\.\d)?)\s*[- ]?star\b", re.IGNORECASE)


class MockLLMClient(LLMClient):
    """Regex-backed stand-in for a real LLM. Good enough for local dev and
    tests; not natural-language understanding, just enough to keep the
    Planner's happy and clarification paths both exercisable offline.
    """

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        message = self._extract_user_message(user_prompt)
        return json.dumps(self._extract_fields(message))

    @staticmethod
    def _extract_user_message(user_prompt: str) -> str:
        marker_index = user_prompt.find(_USER_MESSAGE_MARKER)
        if marker_index == -1:
            return user_prompt
        return user_prompt[marker_index + len(_USER_MESSAGE_MARKER) :].rsplit(
            "\n\nReturn only", 1
        )[0].strip()

    @staticmethod
    def _extract_fields(message: str) -> dict:
        extracted: dict = {}

        route_match = _ROUTE_RE.search(message)
        if route_match:
            extracted["origin"] = route_match.group("origin").strip().title()
            extracted["destination"] = route_match.group("destination").strip().title()

        # Heuristic: first ISO date mentioned is departure, second is return.
        dates = _DATE_RE.findall(message)
        if len(dates) >= 1:
            extracted["departure_date"] = dates[0]
        if len(dates) >= 2:
            extracted["return_date"] = dates[1]

        passengers_match = _PASSENGERS_RE.search(message)
        if passengers_match:
            extracted["passengers"] = int(passengers_match.group(1))

        budget_match = _BUDGET_RE.search(message)
        if budget_match:
            extracted["budget"] = float(budget_match.group(1).replace(",", ""))

        hotel_match = _HOTEL_RATING_RE.search(message)
        if hotel_match:
            extracted["hotel_rating"] = float(hotel_match.group(1))

        return extracted
