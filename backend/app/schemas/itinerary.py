"""Schemas for the final presentation-layer Itinerary.

Business-level travel data organized for a frontend to render directly —
no internal execution detail (tool arguments, timings, retry mechanics)
belongs here. Built by app/agent/itinerary_builder.py from the
FallbackManager's recovered results, the Validator's report, and the
traveler's TravelSession.
"""

from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.tools import CarRentalOption, FlightOption, HotelOption


class TravelerInformation(BaseModel):
    """Trip parameters as confirmed by the traveler.

    A presentation-layer mirror of TravelSession, not a re-export of it,
    so the API contract doesn't couple directly to the planning-layer
    model — they're free to evolve independently.
    """

    origin: str | None = None
    destination: str | None = None
    departure_date: str | None = None
    return_date: str | None = None
    passengers: int | None = None
    budget: float | None = None
    hotel_rating: float | None = None


class TripSummary(BaseModel):
    destination: str | None = None
    duration_nights: int | None = None
    total_estimated_cost: float | None = None
    currency: str = "USD"
    flights_found: int = 0
    hotels_found: int = 0
    car_rentals_found: int = 0


class UnavailableService(BaseModel):
    """A travel service the agent could not retrieve, so the traveler
    knows what's missing rather than silently assuming it was never
    searched for."""

    service: str
    reason: str


class Itinerary(BaseModel):
    itinerary_id: str = Field(default_factory=lambda: str(uuid4()))
    overview: str | None = None

    traveler_information: TravelerInformation
    flight_options: list[FlightOption] = Field(default_factory=list)
    hotel_options: list[HotelOption] = Field(default_factory=list)
    car_rental_options: list[CarRentalOption] = Field(default_factory=list)
    trip_summary: TripSummary

    recommendations: list[str] = Field(default_factory=list)
    unavailable_services: list[UnavailableService] = Field(default_factory=list)

    # `warnings` = something's degraded (empty results, over budget).
    # `notices` = neutral/positive disclosures (e.g. recovered after a
    # retry). Kept separate so a frontend can style "we recovered your
    # flights" differently from an actual problem.
    warnings: list[str] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)

    is_partial: bool = False
