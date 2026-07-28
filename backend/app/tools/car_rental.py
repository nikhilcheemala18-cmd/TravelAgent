"""Car rental search tool.

Mock implementation. Swap the body of `execute` for a real call to a car
rental provider API (e.g. Rentalcars, Hertz) when ready.
"""

from app.schemas.common import ToolName
from app.schemas.tools import (
    CarRentalOption,
    CarRentalSearchInput,
    CarRentalSearchOutput,
)
from app.tools.base import BaseTool


class CarRentalSearchTool(BaseTool):
    name = ToolName.CAR_RENTAL_SEARCH

    def execute(self, tool_input: CarRentalSearchInput) -> CarRentalSearchOutput:
        # TODO: replace with a real car rental provider API call.
        return CarRentalSearchOutput(
            success=True,
            options=[
                CarRentalOption(
                    provider="Mock Rentals",
                    car_type="Economy",
                    price_per_day=45.0,
                )
            ],
        )
