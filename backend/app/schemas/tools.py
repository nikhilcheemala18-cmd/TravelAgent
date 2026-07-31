"""Schemas for tool inputs/outputs.

Each tool in app/tools/ consumes one *Input model and produces one *Output
model. Keeping these separate from the tool implementation means a real
provider integration can replace the implementation without touching the
contract the rest of the agent depends on.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class CabinClass(StrEnum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class HotelType(StrEnum):
    HOTEL = "hotel"
    RESORT = "resort"
    BOUTIQUE = "boutique"
    HOSTEL = "hostel"
    APARTMENT = "apartment"
    GUESTHOUSE = "guesthouse"


class ToolInput(BaseModel):
    """Base class for all tool inputs."""


class ToolOutput(BaseModel):
    """Base class for all tool outputs."""

    success: bool
    error_message: str | None = None
    # Set when `options` (once serialized) is empty on an otherwise
    # successful call, explaining *why* in conversational terms (e.g.
    # "no destinations matched", "nothing within that budget"). Generic
    # consumers (Validator, ItineraryBuilder) just relay this verbatim —
    # they don't need to know why it's empty, only that the tool does.
    empty_reason: str | None = None


class FlightSearchInput(ToolInput):
    origin: str
    destination: str
    departure_date: str
    return_date: str | None = None
    travelers: int = 1
    # Optional search filter — a real flight API would take an equivalent
    # price-ceiling query parameter.
    max_price: float | None = None


class FlightOption(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    currency: str = "USD"
    cabin_class: CabinClass
    stops: int = Field(ge=0)


class FlightSearchOutput(ToolOutput):
    options: list[FlightOption] = []


class HotelSearchInput(ToolInput):
    destination: str
    check_in_date: str
    # Optional: an open-ended/one-way trip has no checkout date yet.
    check_out_date: str | None = None
    guests: int = 1
    # Optional search filter — a real hotel API would take an equivalent
    # minimum-star-rating query parameter.
    min_rating: float | None = None


class HotelOption(BaseModel):
    name: str
    star_rating: float
    price_per_night: float
    currency: str = "USD"
    amenities: list[str] = Field(default_factory=list)
    location: str
    review_score: float
    hotel_type: HotelType


class HotelSearchOutput(ToolOutput):
    options: list[HotelOption] = []


class CarRentalSearchInput(ToolInput):
    destination: str
    pickup_date: str
    dropoff_date: str


class CarRentalOption(BaseModel):
    provider: str
    car_type: str
    price_per_day: float
    currency: str = "USD"


class CarRentalSearchOutput(ToolOutput):
    options: list[CarRentalOption] = []
