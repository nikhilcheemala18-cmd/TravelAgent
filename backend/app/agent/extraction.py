"""Slot extraction for the Planner.

Turns free-form user text into a partial set of TravelSession field values.
Isolated behind the SlotExtractor interface so today's regex-based
heuristic can be replaced with an LLM-backed extractor later without the
Planner (or anything downstream of it) changing.
"""

import re
from abc import ABC, abstractmethod
from typing import Any


class SlotExtractor(ABC):
    @abstractmethod
    def extract(self, message: str) -> dict[str, Any]:
        """Return the TravelSession field values found in `message`.

        Fields that weren't mentioned must be omitted from the returned
        dict (not set to None), so callers can tell "not mentioned" apart
        from "explicitly cleared".
        """


class RegexSlotExtractor(SlotExtractor):
    """Rule-based extractor using regular expressions.

    Deliberately conservative: it recognizes a handful of common phrasings
    (ISO dates, "from X to Y", "N passengers", "$N budget", "N star
    hotel") and skips anything it isn't confident about rather than
    guessing.

    TODO: replace with an LLM-backed SlotExtractor for robust natural
    language understanding (relative dates, city name normalization,
    multi-turn corrections, etc.) — the SlotExtractor interface should not
    need to change.
    """

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

    def extract(self, message: str) -> dict[str, Any]:
        extracted: dict[str, Any] = {}

        route_match = self._ROUTE_RE.search(message)
        if route_match:
            extracted["origin"] = route_match.group("origin").strip().title()
            extracted["destination"] = route_match.group("destination").strip().title()

        # Heuristic: first ISO date mentioned is departure, second is return.
        dates = self._DATE_RE.findall(message)
        if len(dates) >= 1:
            extracted["departure_date"] = dates[0]
        if len(dates) >= 2:
            extracted["return_date"] = dates[1]

        passengers_match = self._PASSENGERS_RE.search(message)
        if passengers_match:
            extracted["passengers"] = int(passengers_match.group(1))

        budget_match = self._BUDGET_RE.search(message)
        if budget_match:
            extracted["budget"] = float(budget_match.group(1).replace(",", ""))

        hotel_match = self._HOTEL_RATING_RE.search(message)
        if hotel_match:
            extracted["hotel_rating"] = float(hotel_match.group(1))

        return extracted
