"""Flight search tool.

Mock implementation that simulates a realistic flight-search API response:
a spread of airlines, departure times, stop counts, and cabin classes,
with prices that plausibly correlate with both stops and cabin class —
enough variation for downstream ranking/recommendation logic to have
something meaningful to choose between. It also behaves like a real API
would for a route it doesn't serve or a search that matches nothing: it
returns success with an empty list and a conversational `empty_reason`,
never a fabricated result and never an exception. Swap the body of
`execute` for a real provider call (e.g. Amadeus Self-Service, Duffel,
Skyscanner) when ready — the FlightSearchInput/Output contract (and the
FlightOption fields) are provider-agnostic and shouldn't need to change
for a typical REST provider.
"""

import random

from app.schemas.common import ToolName
from app.schemas.tools import CabinClass, FlightOption, FlightSearchInput, FlightSearchOutput
from app.tools.base import BaseTool
from app.tools.mock_data import (
    is_same_city,
    is_supported_destination,
    unsupported_destination_message,
    unsupported_route_message,
)

_AIRLINES: tuple[tuple[str, str], ...] = (
    ("SkyLine Airways", "SL"),
    ("Horizon Air", "HZ"),
    ("BlueWing Airlines", "BW"),
    ("Pacific Route Air", "PC"),
    ("Northern Star Airlines", "NX"),
    ("Coastal Jet", "CJ"),
    ("Summit Airlines", "ST"),
    ("Zenith Air", "ZE"),
    ("Alpine Airways", "AL"),
    ("Continental Express", "CN"),
)

# Weighted so most results look like a real search page — mostly economy,
# mostly nonstop/one-stop — with a realistic minority of premium options.
_CABIN_CLASS_WEIGHTS: tuple[tuple[CabinClass, float], ...] = (
    (CabinClass.ECONOMY, 0.55),
    (CabinClass.PREMIUM_ECONOMY, 0.22),
    (CabinClass.BUSINESS, 0.16),
    (CabinClass.FIRST, 0.07),
)
_CABIN_CLASS_PRICE_MULTIPLIER: dict[CabinClass, float] = {
    CabinClass.ECONOMY: 1.0,
    CabinClass.PREMIUM_ECONOMY: 1.6,
    CabinClass.BUSINESS: 3.2,
    CabinClass.FIRST: 5.5,
}
_STOPS_WEIGHTS: tuple[tuple[int, float], ...] = ((0, 0.4), (1, 0.45), (2, 0.15))

_MIN_OPTIONS = 8
_MAX_OPTIONS = 10


class FlightSearchTool(BaseTool):
    name = ToolName.FLIGHT_SEARCH

    def execute(self, tool_input: FlightSearchInput) -> FlightSearchOutput:
        # TODO: replace with a real flight provider API call.
        parsed = FlightSearchInput.model_validate(tool_input)

        if is_same_city(parsed.origin, parsed.destination):
            return FlightSearchOutput(success=True, options=[], empty_reason=unsupported_route_message())

        if not is_supported_destination(parsed.origin) or not is_supported_destination(parsed.destination):
            return FlightSearchOutput(
                success=True, options=[], empty_reason=unsupported_destination_message()
            )

        count = random.randint(_MIN_OPTIONS, _MAX_OPTIONS)
        options = [self._generate_option() for _ in range(count)]

        if parsed.max_price is not None:
            options = [option for option in options if option.price <= parsed.max_price]
            if not options:
                return FlightSearchOutput(
                    success=True,
                    options=[],
                    empty_reason=(
                        f"I couldn't find any flights within a budget of {parsed.max_price:.0f}. "
                        "Try increasing your budget, or checking nearby travel dates."
                    ),
                )

        options.sort(key=lambda option: option.price)
        return FlightSearchOutput(success=True, options=options)

    def _generate_option(self) -> FlightOption:
        airline, code = random.choice(_AIRLINES)
        stops = _weighted_choice(_STOPS_WEIGHTS)
        cabin_class = _weighted_choice(_CABIN_CLASS_WEIGHTS)

        departure_minutes = random.randint(5 * 60, 22 * 60)  # 05:00-22:00
        base_flight_minutes = random.randint(90, 240)  # 1h30m-4h base airtime
        layover_minutes = sum(random.randint(45, 150) for _ in range(stops))
        total_minutes = base_flight_minutes + layover_minutes
        arrival_minutes = (departure_minutes + total_minutes) % (24 * 60)

        base_price = max(60.0, random.uniform(120, 320) - stops * random.uniform(0, 20))
        price = base_price * _CABIN_CLASS_PRICE_MULTIPLIER[cabin_class] + random.uniform(-15, 15)

        return FlightOption(
            airline=airline,
            flight_number=f"{code}{random.randint(100, 999)}",
            departure_time=_format_clock(departure_minutes),
            arrival_time=_format_clock(arrival_minutes),
            duration=_format_duration(total_minutes),
            price=round(max(price, 45.0), 2),
            cabin_class=cabin_class,
            stops=stops,
        )


def _weighted_choice(weighted_options: tuple[tuple, ...]):
    values, weights = zip(*weighted_options)
    return random.choices(values, weights=weights, k=1)[0]


def _format_clock(total_minutes: int) -> str:
    hours, minutes = divmod(total_minutes % (24 * 60), 60)
    return f"{hours:02d}:{minutes:02d}"


def _format_duration(total_minutes: int) -> str:
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes:02d}m" if minutes else f"{hours}h"
