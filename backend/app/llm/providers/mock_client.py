"""Deterministic offline LLM client.

Used when LLM_PROVIDER=mock (the default) so the whole agent runs
end-to-end without any API credentials — the same role MOCK_MODE already
plays for app/tools/*. It makes no network calls.

It only knows how to answer the one prompt shape the agent currently
sends (see app/agent/prompts/extraction.py): given "trip details already
collected" + "user message", pull out any newly mentioned trip details
with regex heuristics, and return them as a JSON object — mimicking what
a real LLM is instructed to return, so it's a valid stand-in for local
dev/tests.

Deliberately limited: it recognizes explicit ISO dates (YYYY-MM-DD) but
NOT relative expressions like "next Friday" or "15th August" — resolving
those against "today" is exactly the kind of reasoning this mock exists
to avoid reimplementing. Use a real provider (LLM_PROVIDER=openai, ...)
to exercise that behavior.
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
_PASSENGERS_DIGIT_RE = re.compile(
    r"\b(\d+)\s*(?:passengers?|people|travelers?|adults?|pax)\b", re.IGNORECASE
)
_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
_PASSENGERS_WORD_RE = re.compile(
    r"\b(" + "|".join(_NUMBER_WORDS) + r")\s*(?:passengers?|people|travelers?|adults?)\b",
    re.IGNORECASE,
)
# "budget" followed by up to 20 non-digit characters (covers "of", "is
# around", "is roughly", ...) then the amount; falls back to a bare
# "$<amount>" if the word "budget" isn't used at all.
_BUDGET_KEYWORD_RE = re.compile(r"\bbudget\b[^\d]{0,20}(\d[\d,]*(?:\.\d+)?)", re.IGNORECASE)
_BUDGET_DOLLAR_RE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)")
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

        passengers_match = _PASSENGERS_DIGIT_RE.search(message)
        if passengers_match:
            extracted["passengers"] = int(passengers_match.group(1))
        else:
            word_match = _PASSENGERS_WORD_RE.search(message)
            if word_match:
                extracted["passengers"] = _NUMBER_WORDS[word_match.group(1).lower()]

        budget_match = _BUDGET_KEYWORD_RE.search(message) or _BUDGET_DOLLAR_RE.search(message)
        if budget_match:
            extracted["budget"] = float(budget_match.group(1).replace(",", ""))

        hotel_match = _HOTEL_RATING_RE.search(message)
        if hotel_match:
            extracted["hotel_rating"] = float(hotel_match.group(1))

        return extracted
