"""Itinerary Builder.

Turns a finished pipeline run — the FallbackManager's recovered
ToolExecutionResults, the Validator's report, and the traveler's
TravelSession — into a single presentation-layer Itinerary: business-level
travel data organized into sections a frontend can render directly, with
no internal execution detail (tool arguments, timings, retry mechanics)
leaking through. This is the last stop before the API response — it never
re-executes, retries, or re-validates anything; it only presents what
already happened.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel

from app.schemas.common import ActionStatus, ToolName
from app.schemas.fallback import FallbackOutcome
from app.schemas.itinerary import Itinerary, TravelerInformation, TripSummary, UnavailableService
from app.schemas.tool_execution import ToolExecutionResult
from app.schemas.tools import CarRentalOption, FlightOption, HotelOption
from app.schemas.travel_session import TravelSession
from app.schemas.validation import ValidationIssue, ValidationResult
from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class _SectionSpec:
    tool_name: ToolName
    display_name: str
    option_model: type[BaseModel]
    attribute: str


# The single registration point for a searchable travel category. Adding a
# new one (weather, attractions, visa info, transport, restaurants, ...)
# means: a new ToolName + tool implementation, a matching *Option schema,
# a new Itinerary list field, and one entry here — nothing else in this
# class changes.
_SECTION_SPECS: tuple[_SectionSpec, ...] = (
    _SectionSpec(ToolName.FLIGHT_SEARCH, "Flights", FlightOption, "flight_options"),
    _SectionSpec(ToolName.HOTEL_SEARCH, "Hotels", HotelOption, "hotel_options"),
    _SectionSpec(ToolName.CAR_RENTAL_SEARCH, "Car rentals", CarRentalOption, "car_rental_options"),
)


class ItineraryBuilder(ABC):
    @abstractmethod
    def build(
        self,
        results: list[ToolExecutionResult],
        validation: ValidationResult,
        fallback: FallbackOutcome,
        travel_session: TravelSession,
    ) -> Itinerary:
        """Assemble the final presentation-layer Itinerary.

        `results` should be the FallbackManager's recovered set
        (FallbackOutcome.results), not the ToolExecutor's raw output —
        already-successful results untouched, retried tools reflecting
        whatever the retry produced.
        """


class DefaultItineraryBuilder(ItineraryBuilder):
    """Section-registry-driven builder — see _SECTION_SPECS.

    TODO: smarter recommendation ranking (multi-factor: price, rating,
    layovers, ...) once real provider data is available; today's picks are
    simple cheapest/best-rated heuristics.
    """

    def build(
        self,
        results: list[ToolExecutionResult],
        validation: ValidationResult,
        fallback: FallbackOutcome,
        travel_session: TravelSession,
    ) -> Itinerary:
        results_by_tool = {result.tool_name: result for result in results}
        issues_by_tool: dict[ToolName, list[ValidationIssue]] = {
            validated.tool_name: validated.issues for validated in validation.validated_results
        }
        recovered_tools = {attempt.tool_name for attempt in fallback.retry_attempts if attempt.succeeded}

        sections: dict[str, list] = {}
        unavailable: list[UnavailableService] = []
        notices: list[str] = []
        warnings: list[str] = [issue.message for issue in validation.warnings]

        for spec in _SECTION_SPECS:
            result = results_by_tool.get(spec.tool_name)
            if result is None:
                continue  # this trip never planned/needed this tool

            if result.status == ActionStatus.SUCCESS:
                options = self._parse_options(result, spec)
                sections[spec.attribute] = options
                if spec.tool_name in recovered_tools and options:
                    notices.append(
                        f"{spec.display_name} results were temporarily delayed but recovered successfully."
                    )
                continue

            unavailable.append(
                UnavailableService(
                    service=spec.display_name,
                    reason=self._failure_reason(spec.tool_name, issues_by_tool, result),
                )
            )
            if spec.tool_name in fallback.unresolved_tools:
                notices.append(
                    f"We tried again, but {spec.display_name.lower()} results are still unavailable."
                )

        flight_options = sections.get("flight_options", [])
        hotel_options = sections.get("hotel_options", [])
        car_rental_options = sections.get("car_rental_options", [])

        trip_summary = self._build_trip_summary(
            travel_session, flight_options, hotel_options, car_rental_options
        )
        recommendations = self._build_recommendations(travel_session, flight_options, hotel_options)

        if trip_summary.total_estimated_cost and travel_session.budget:
            if trip_summary.total_estimated_cost > travel_session.budget:
                warnings.append(
                    f"Estimated cost (~{trip_summary.total_estimated_cost:.2f} "
                    f"{trip_summary.currency}) exceeds your budget of "
                    f"{travel_session.budget:.2f} {trip_summary.currency}."
                )

        itinerary = Itinerary(
            traveler_information=self._build_traveler_information(travel_session),
            flight_options=flight_options,
            hotel_options=hotel_options,
            car_rental_options=car_rental_options,
            trip_summary=trip_summary,
            recommendations=recommendations,
            unavailable_services=unavailable,
            warnings=warnings,
            notices=notices,
            is_partial=bool(unavailable),
            overview=self._build_overview(trip_summary, unavailable),
        )

        if itinerary.is_partial:
            logger.info(
                "Built partial itinerary %s — unavailable: %s",
                itinerary.itinerary_id,
                [service.service for service in unavailable],
            )
        else:
            logger.info("Built itinerary %s", itinerary.itinerary_id)

        return itinerary

    # -- section parsing ----------------------------------------------------

    @staticmethod
    def _parse_options(result: ToolExecutionResult, spec: _SectionSpec) -> list[BaseModel]:
        raw_options = (result.returned_data or {}).get("options", [])
        parsed: list[BaseModel] = []
        for raw in raw_options:
            try:
                parsed.append(spec.option_model.model_validate(raw))
            except Exception:  # noqa: BLE001 - one bad entry shouldn't drop the rest
                logger.debug("Skipping malformed %s option: %r", spec.tool_name, raw)
        return parsed

    @staticmethod
    def _failure_reason(
        tool_name: ToolName,
        issues_by_tool: dict[ToolName, list[ValidationIssue]],
        result: ToolExecutionResult,
    ) -> str:
        issues = issues_by_tool.get(tool_name) or []
        if issues:
            return issues[0].message
        return result.error_message or "Temporarily unavailable."

    # -- derived sections -----------------------------------------------------

    @staticmethod
    def _build_traveler_information(session: TravelSession) -> TravelerInformation:
        return TravelerInformation(
            origin=session.origin,
            destination=session.destination,
            departure_date=session.departure_date,
            return_date=session.return_date,
            passengers=session.passengers,
            budget=session.budget,
            hotel_rating=session.hotel_rating,
        )

    @staticmethod
    def _duration_nights(session: TravelSession) -> int | None:
        if not session.departure_date or not session.return_date:
            return None
        try:
            nights = (
                date.fromisoformat(session.return_date) - date.fromisoformat(session.departure_date)
            ).days
        except ValueError:
            return None
        return nights if nights > 0 else None

    def _build_trip_summary(
        self,
        session: TravelSession,
        flights: list[FlightOption],
        hotels: list[HotelOption],
        car_rentals: list[CarRentalOption],
    ) -> TripSummary:
        nights = self._duration_nights(session)
        passengers = session.passengers or 1
        currency = flights[0].currency if flights else (hotels[0].currency if hotels else "USD")

        total = 0.0
        has_cost = False
        if flights:
            total += min(flight.price for flight in flights) * passengers
            has_cost = True
        if hotels and nights:
            total += min(hotel.price_per_night for hotel in hotels) * nights
            has_cost = True
        if car_rentals and nights:
            total += min(car.price_per_day for car in car_rentals) * nights
            has_cost = True

        return TripSummary(
            destination=session.destination,
            duration_nights=nights,
            total_estimated_cost=round(total, 2) if has_cost else None,
            currency=currency,
            flights_found=len(flights),
            hotels_found=len(hotels),
            car_rentals_found=len(car_rentals),
        )

    @staticmethod
    def _build_recommendations(
        session: TravelSession, flights: list[FlightOption], hotels: list[HotelOption]
    ) -> list[str]:
        recommendations: list[str] = []

        if flights:
            cheapest = min(flights, key=lambda flight: flight.price)
            recommendations.append(
                f"Best value flight: {cheapest.airline} {cheapest.flight_number} "
                f"for {cheapest.price:.2f} {cheapest.currency}."
            )

        if hotels:
            eligible = [
                hotel
                for hotel in hotels
                if session.hotel_rating is None or hotel.star_rating >= session.hotel_rating
            ]
            pool = eligible or hotels
            best = max(pool, key=lambda hotel: hotel.star_rating)
            recommendations.append(
                f"Recommended hotel: {best.name} ({best.star_rating}-star) at "
                f"{best.price_per_night:.2f} {best.currency}/night."
            )

        return recommendations

    @staticmethod
    def _build_overview(trip_summary: TripSummary, unavailable: list[UnavailableService]) -> str:
        parts = []
        if trip_summary.flights_found:
            parts.append(f"{trip_summary.flights_found} flight option(s)")
        if trip_summary.hotels_found:
            parts.append(f"{trip_summary.hotels_found} hotel option(s)")
        if trip_summary.car_rentals_found:
            parts.append(f"{trip_summary.car_rentals_found} car rental option(s)")

        if not parts:
            return "I couldn't find any options for your trip yet."

        destination = f" for {trip_summary.destination}" if trip_summary.destination else ""
        overview = f"Found {', '.join(parts)}{destination}."
        if unavailable:
            missing = ", ".join(service.service for service in unavailable)
            overview += f" ({missing} unavailable right now.)"
        return overview
