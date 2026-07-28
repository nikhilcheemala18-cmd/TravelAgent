"""Itinerary Builder.

Assembles validated tool results into a single Itinerary the user can
review/book. Kept separate from the Validator so "is this data usable" and
"how do we present it" remain independently changeable.
"""

from abc import ABC, abstractmethod

from app.schemas.common import ActionStatus, ToolName
from app.schemas.itinerary import Itinerary
from app.schemas.tool_execution import ToolExecutionResult
from app.schemas.tools import CarRentalOption, FlightOption, HotelOption


class ItineraryBuilder(ABC):
    @abstractmethod
    def build(self, results: list[ToolExecutionResult]) -> Itinerary:
        """Turn successful tool results into an Itinerary."""


class DefaultItineraryBuilder(ItineraryBuilder):
    """Placeholder builder — flattens successful tool outputs into an Itinerary.

    TODO: real ranking/selection logic (cheapest, best-rated, closest match
    to budget) instead of taking every option verbatim; cost aggregation
    across currencies; conflict detection between flights/hotels/cars.
    """

    def build(self, results: list[ToolExecutionResult]) -> Itinerary:
        itinerary = Itinerary()

        for result in results:
            if result.status != ActionStatus.SUCCESS or not result.returned_data:
                continue

            if result.tool_name == ToolName.FLIGHT_SEARCH:
                itinerary.flights.extend(
                    FlightOption(**opt) for opt in result.returned_data.get("options", [])
                )
            elif result.tool_name == ToolName.HOTEL_SEARCH:
                itinerary.hotels.extend(
                    HotelOption(**opt) for opt in result.returned_data.get("options", [])
                )
            elif result.tool_name == ToolName.CAR_RENTAL_SEARCH:
                itinerary.car_rentals.extend(
                    CarRentalOption(**opt) for opt in result.returned_data.get("options", [])
                )

        itinerary.summary = "Draft itinerary (placeholder builder — no ranking/selection applied yet)."
        return itinerary
