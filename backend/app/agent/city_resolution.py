"""Deterministic city resolution for extracted travel slots.

The LLM extracts raw city names from natural language. This module turns
those raw strings into canonical mock-inventory city names before the
Planner builds tool calls. Known aliases are applied silently; likely
typos are surfaced as session-aware confirmations.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
import string

from app.tools.mock_data import SUPPORTED_DESTINATIONS

CITY_FIELDS = frozenset({"origin", "destination"})

_ALIASES: dict[str, str] = {
    "bangalore": "Bengaluru",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "calcutta": "Kolkata",
}
_DISPLAY_ALIAS_BY_CANONICAL: dict[str, str] = {
    "Bengaluru": "Bangalore",
    "Mumbai": "Bombay",
    "Chennai": "Madras",
    "Kolkata": "Calcutta",
}
_YES_RE = re.compile(r"^\s*(yes|yeah|yep|correct|right|that's right|that is right)\s*[.!]?\s*$", re.I)
_NO_RE = re.compile(r"^\s*(no|nope|nah)\b", re.I)
_REPLACEMENT_RE = re.compile(
    r"\b(?:meant|mean|instead|city is|it is|it's|to|from)\s+([a-zA-Z\s]+?)(?=[.,!?]|$)",
    re.I,
)
_TRIM_CHARS = string.whitespace + string.punctuation


@dataclass(frozen=True)
class CityResolution:
    field: str
    raw_value: str
    status: str
    canonical_value: str | None = None
    suggested_value: str | None = None


def canonical_display(value: str) -> str:
    alias = _DISPLAY_ALIAS_BY_CANONICAL.get(value)
    return f"{value} ({alias})" if alias else value


def is_affirmative(message: str) -> bool:
    return bool(_YES_RE.match(message))


def is_negative(message: str) -> bool:
    return bool(_NO_RE.match(message))


def extract_replacement_city(message: str) -> str | None:
    match = _REPLACEMENT_RE.search(message)
    if match:
        return _clean_raw(match.group(1))

    cleaned = _clean_raw(re.sub(_NO_RE, "", message, count=1))
    words = cleaned.split()
    return cleaned if 1 <= len(words) <= 3 else None


def resolve_city(field: str, raw_value: str) -> CityResolution:
    cleaned = _clean_raw(raw_value)
    normalized = _normalize(cleaned)

    canonical_by_norm = {_normalize(city): city for city in SUPPORTED_DESTINATIONS}
    if normalized in canonical_by_norm:
        return CityResolution(field, cleaned, "accepted", canonical_by_norm[normalized])

    alias_target = _ALIASES.get(normalized)
    if alias_target and alias_target in SUPPORTED_DESTINATIONS:
        return CityResolution(field, cleaned, "accepted", alias_target)

    suggestion = _suggest_city(normalized, canonical_by_norm)
    if suggestion:
        return CityResolution(field, cleaned, "confirm", suggested_value=suggestion)

    return CityResolution(field, cleaned, "unsupported")


def resolve_city_updates(updates: dict) -> tuple[dict, CityResolution | None]:
    resolved = dict(updates)
    for field in ("origin", "destination"):
        value = updates.get(field)
        if value is None:
            continue

        result = resolve_city(field, str(value))
        if result.status == "accepted":
            resolved[field] = result.canonical_value
            continue
        resolved.pop(field, None)
        return resolved, result

    return resolved, None


def _suggest_city(normalized: str, canonical_by_norm: dict[str, str]) -> str | None:
    candidates = dict(canonical_by_norm)
    for alias, canonical in _ALIASES.items():
        if canonical in SUPPORTED_DESTINATIONS:
            candidates[alias] = canonical

    scored = sorted(
        (
            (SequenceMatcher(None, normalized, candidate).ratio(), canonical)
            for candidate, canonical in candidates.items()
        ),
        reverse=True,
    )
    if not scored or scored[0][0] < 0.78:
        return None
    if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.04:
        return None
    return scored[0][1]


def _clean_raw(value: str) -> str:
    return value.strip(_TRIM_CHARS).title()


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())
