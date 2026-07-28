"""Schemas for the final itinerary the agent assembles for the user."""

from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.tools import CarRentalOption, FlightOption, HotelOption


class Itinerary(BaseModel):
    itinerary_id: str = Field(default_factory=lambda: str(uuid4()))
    summary: str | None = None
    flights: list[FlightOption] = []
    hotels: list[HotelOption] = []
    car_rentals: list[CarRentalOption] = []
    estimated_total_cost: float | None = None
    currency: str = "USD"
