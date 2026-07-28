"""Flight search tool.

Mock implementation. Swap the body of `execute` for a real call to a flight
provider API (e.g. Amadeus Self-Service, Duffel, Skyscanner) when ready —
the FlightSearchInput/Output contract should not need to change for a
typical REST provider.
"""

from app.schemas.common import ToolName
from app.schemas.tools import FlightOption, FlightSearchInput, FlightSearchOutput
from app.tools.base import BaseTool


class FlightSearchTool(BaseTool):
    name = ToolName.FLIGHT_SEARCH

    def execute(self, tool_input: FlightSearchInput) -> FlightSearchOutput:
        # TODO: replace with a real flight provider API call.
        return FlightSearchOutput(
            success=True,
            options=[
                FlightOption(
                    airline="Mock Airlines",
                    flight_number="MA101",
                    departure_time="08:00",
                    arrival_time="11:00",
                    price=199.99,
                )
            ],
        )
