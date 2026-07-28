"""Hotel search tool.

Mock implementation. Swap the body of `execute` for a real call to a hotel
provider API (e.g. Booking.com, Expedia Rapid API) when ready.
"""

from app.schemas.common import ToolName
from app.schemas.tools import HotelOption, HotelSearchInput, HotelSearchOutput
from app.tools.base import BaseTool


class HotelSearchTool(BaseTool):
    name = ToolName.HOTEL_SEARCH

    def execute(self, tool_input: HotelSearchInput) -> HotelSearchOutput:
        # TODO: replace with a real hotel provider API call.
        return HotelSearchOutput(
            success=True,
            options=[
                HotelOption(
                    name="Mock Grand Hotel",
                    star_rating=4.0,
                    price_per_night=120.0,
                )
            ],
        )
