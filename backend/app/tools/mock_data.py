"""Shared reference data for the mock flight/hotel providers.

Centralizing "which cities this demo dataset knows about" here means both
tools stay consistent with each other, and anything that needs to explain
supported destinations to the user reads the same list rather than a
second hardcoded copy. This is entirely mock-specific — a real provider
integration wouldn't need this module at all, since a real API already
knows its own route/inventory coverage; that's why this logic lives here
and not in Planner/Validator/FallbackManager/ItineraryBuilder.

Known simplification: matching is exact (case/whitespace-insensitive)
against this list — common aliases (e.g. "Bangalore" vs "Bengaluru")
aren't reconciled. Acceptable for a demo dataset; a real geocoding-backed
provider wouldn't have this limitation.
"""

SUPPORTED_DESTINATIONS: tuple[str, ...] = (
    "New York",
    "Los Angeles",
    "Chicago",
    "San Francisco",
    "Toronto",
    "London",
    "Paris",
    "Rome",
    "Barcelona",
    "Amsterdam",
    "Dubai",
    "Singapore",
    "Bangkok",
    "Tokyo",
    "Sydney",
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Goa",
)

_NORMALIZED_DESTINATIONS: frozenset[str] = frozenset(
    city.strip().lower() for city in SUPPORTED_DESTINATIONS
)


def is_supported_destination(city: str | None) -> bool:
    return bool(city) and city.strip().lower() in _NORMALIZED_DESTINATIONS


def is_same_city(city_a: str | None, city_b: str | None) -> bool:
    if not city_a or not city_b:
        return False
    return city_a.strip().lower() == city_b.strip().lower()


def format_supported_destinations() -> str:
    return ", ".join(SUPPORTED_DESTINATIONS)


def unsupported_destination_message() -> str:
    return (
        "I'm currently running on demo travel data, so I can only generate "
        "itineraries for destinations available in my mock database. "
        f"Currently supported destinations include: {format_supported_destinations()}. "
        "Please try one of the supported destinations, and I'll be happy to help."
    )


def unsupported_route_message() -> str:
    return (
        "Your origin and destination look like the same place, so there's no "
        "route to search. Could you double-check your destination?"
    )
