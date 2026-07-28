"""Shared enums and base types used across schema modules."""

from enum import StrEnum


class ToolName(StrEnum):
    FLIGHT_SEARCH = "flight_search"
    HOTEL_SEARCH = "hotel_search"
    CAR_RENTAL_SEARCH = "car_rental_search"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(StrEnum):
    BOOK_TRIP = "book_trip"
    SEARCH_FLIGHTS = "search_flights"
    SEARCH_HOTELS = "search_hotels"
    SEARCH_CAR_RENTAL = "search_car_rental"
    MODIFY_ITINERARY = "modify_itinerary"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


class ActionStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
