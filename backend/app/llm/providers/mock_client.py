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

Deliberately limited: it recognizes ISO dates plus a small set of
evaluation-friendly relative dates ("tomorrow", "next Friday", "in two
weeks") against the prompt's reference date. Use a real provider
(LLM_PROVIDER=openai, ...) to exercise broader natural-language
understanding.
"""

import json
import re
from datetime import date, timedelta

from app.llm.base import LLMClient
from app.tools.mock_data import SUPPORTED_DESTINATIONS

_USER_MESSAGE_MARKER = "User message:\n"
_TODAY_RE = re.compile(r"Today's date:\s*(\d{4}-\d{2}-\d{2})")
_KNOWN_DETAILS_MARKER = "Trip details already collected (JSON):\n"

_ROUTE_RE = re.compile(
    r"\bfrom\s+(?P<origin>[a-zA-Z\s]+?)\s+to\s+(?P<destination>[a-zA-Z\s]+?)"
    r"(?=[.,!?]|\s+(?:on|for|with|departing|leaving|returning|from|budget|tomorrow|next|in)\b|$)",
    re.IGNORECASE,
)
_LEAVING_FOR_RE = re.compile(
    r"\b(?:leaving|departing|flying\s+from)\s+(?P<origin>[a-zA-Z\s]+?)\s+for\s+"
    r"(?P<destination>[a-zA-Z\s]+?)"
    r"(?=[.,!?]|\s+(?:on|with|returning|return|budget|tomorrow|next|in)\b|$)",
    re.IGNORECASE,
)
_BARE_ROUTE_RE = re.compile(
    r"\b(?P<origin>[a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+to\s+"
    r"(?P<destination>[a-zA-Z]+(?:\s+[a-zA-Z]+)?)"
    r"(?=[.,!?]|\s+(?:on|for|with|departing|leaving|returning|return|budget|tomorrow|next|in)\b|$)",
    re.IGNORECASE,
)
_ORIGIN_ONLY_RE = re.compile(
    r"\b(?:from|flying\s+from|leaving\s+from|departing\s+from)\s+"
    r"(?P<origin>[a-zA-Z\s]+?)"
    r"(?=[.,!?]|\s+(?:to|on|for|with|departing|leaving|returning|return|budget)\b|$)",
    re.IGNORECASE,
)
_DESTINATION_ONLY_RE = re.compile(
    r"\b(?:to|towards|for)\s+(?P<destination>[a-zA-Z\s]+?)"
    r"(?=[.,!?]|\s+(?:instead|on|for|with|departing|leaving|returning|return|budget|tomorrow|next|in)\b|$)",
    re.IGNORECASE,
)
_DESTINATION_FIELD_RE = re.compile(
    r"\b(?:change|set|update|switch|make)\s+(?:my\s+|the\s+)?destination\s+"
    r"(?:to\s+)?(?P<destination>[a-zA-Z\s]+?)(?=[.,!?]|$)",
    re.IGNORECASE,
)
_GO_TO_INSTEAD_RE = re.compile(
    r"\b(?:go|travel|fly)\s+to\s+(?P<destination>[a-zA-Z\s]+?)\s+instead\b",
    re.IGNORECASE,
)
_CHANGE_CITY_TO_CITY_RE = re.compile(
    r"\bchange\s+[a-zA-Z\s]+?\s+to\s+(?P<destination>[a-zA-Z\s]+?)(?=[.,!?]|$)",
    re.IGNORECASE,
)
_MAKE_IT_DESTINATION_RE = re.compile(
    r"\b(?:actually\s+)?make\s+it\s+(?P<destination>[a-zA-Z\s]+?)(?=[.,!?]|$)",
    re.IGNORECASE,
)
_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_RETURN_DATE_INTENT_RE = re.compile(
    r"\b(?:return|come\s+back|coming\s+back|back)\b", re.IGNORECASE
)
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
_NON_CITY_CANDIDATES = frozenset({"book", "fly", "go", "travel", "trip", "vacation"})
_KNOWN_CITY_ORIGIN_NAMES = frozenset(
    {city.lower() for city in SUPPORTED_DESTINATIONS}
    | {"bangalore", "bombay", "madras", "calcutta"}
)


class MockLLMClient(LLMClient):
    """Regex-backed stand-in for a real LLM. Good enough for local dev and
    tests; not natural-language understanding, just enough to keep the
    Planner's happy and clarification paths both exercisable offline.
    """

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        message = self._extract_user_message(user_prompt)
        reference_date = self._extract_reference_date(user_prompt)
        known_details = self._extract_known_details(user_prompt)
        return json.dumps(self._extract_fields(message, reference_date, known_details))

    @staticmethod
    def _extract_user_message(user_prompt: str) -> str:
        marker_index = user_prompt.find(_USER_MESSAGE_MARKER)
        if marker_index == -1:
            return user_prompt
        return user_prompt[marker_index + len(_USER_MESSAGE_MARKER) :].rsplit(
            "\n\nReturn only", 1
        )[0].strip()

    @staticmethod
    def _extract_reference_date(user_prompt: str) -> date:
        match = _TODAY_RE.search(user_prompt)
        if not match:
            return date.today()
        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return date.today()

    @staticmethod
    def _extract_known_details(user_prompt: str) -> dict:
        marker_index = user_prompt.find(_KNOWN_DETAILS_MARKER)
        if marker_index == -1:
            return {}
        payload = user_prompt[marker_index + len(_KNOWN_DETAILS_MARKER) :].split(
            "\n\nUser message:", 1
        )[0]
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _extract_fields(
        message: str, reference_date: date | None = None, known_details: dict | None = None
    ) -> dict:
        extracted: dict = {}
        reference_date = reference_date or date.today()
        known_details = known_details or {}

        route_match = _ROUTE_RE.search(message) or _LEAVING_FOR_RE.search(message)
        if not route_match:
            bare_route_match = _BARE_ROUTE_RE.search(message)
            if bare_route_match and MockLLMClient._looks_like_known_city(
                bare_route_match.group("origin")
            ):
                route_match = bare_route_match
        if route_match:
            origin = MockLLMClient._clean_city(route_match.group("origin"))
            destination = MockLLMClient._clean_city(route_match.group("destination"))
            if origin:
                extracted["origin"] = origin
            if destination:
                extracted["destination"] = destination
        else:
            origin_match = _ORIGIN_ONLY_RE.search(message)
            if origin_match:
                origin = MockLLMClient._clean_city(origin_match.group("origin"))
                if origin:
                    extracted["origin"] = origin

            destination_match = (
                _DESTINATION_FIELD_RE.search(message)
                or _GO_TO_INSTEAD_RE.search(message)
                or _CHANGE_CITY_TO_CITY_RE.search(message)
            )
            if not destination_match and known_details.get("destination"):
                destination_match = _MAKE_IT_DESTINATION_RE.search(message)
            if not destination_match:
                destination_match = _DESTINATION_ONLY_RE.search(message)
            if destination_match:
                destination = MockLLMClient._clean_city(destination_match.group("destination"))
                if destination:
                    extracted["destination"] = destination

        relative_date = MockLLMClient._extract_relative_date(message, reference_date)
        dates = _DATE_RE.findall(message)
        if len(dates) >= 2:
            extracted["departure_date"] = dates[0]
            extracted["return_date"] = dates[1]
        else:
            explicit_date = dates[0] if dates else relative_date
            if explicit_date and _RETURN_DATE_INTENT_RE.search(message):
                extracted["return_date"] = explicit_date
            elif explicit_date:
                extracted["departure_date"] = explicit_date

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

    @staticmethod
    def _clean_city(value: str) -> str | None:
        city = value.strip().title()
        return None if city.lower() in _NON_CITY_CANDIDATES else city

    @staticmethod
    def _looks_like_known_city(value: str) -> bool:
        city = MockLLMClient._clean_city(value)
        return bool(city) and city.lower() in _KNOWN_CITY_ORIGIN_NAMES

    @staticmethod
    def _extract_relative_date(message: str, reference_date: date) -> str | None:
        lowered = message.lower()
        if "tomorrow" in lowered:
            return (reference_date + timedelta(days=1)).isoformat()

        next_weekday_match = re.search(
            r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            lowered,
        )
        if next_weekday_match:
            weekday_index = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }[next_weekday_match.group(1)]
            days_ahead = (weekday_index - reference_date.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (reference_date + timedelta(days=days_ahead)).isoformat()

        in_weeks_match = re.search(r"\bin\s+(\d+)\s+weeks?\b", lowered)
        if in_weeks_match:
            return (reference_date + timedelta(weeks=int(in_weeks_match.group(1)))).isoformat()

        return None
