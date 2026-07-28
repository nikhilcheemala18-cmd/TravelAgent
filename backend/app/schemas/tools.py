"""Schemas for tool inputs/outputs.

Each tool in app/tools/ consumes one *Input model and produces one *Output
model. Keeping these separate from the tool implementation means a real
provider integration can replace the implementation without touching the
contract the rest of the agent depends on.
"""

from pydantic import BaseModel

from app.schemas.common import ActionStatus, ToolName


class ToolInput(BaseModel):
    """Base class for all tool inputs."""


class ToolOutput(BaseModel):
    """Base class for all tool outputs."""

    success: bool
    error_message: str | None = None


class FlightSearchInput(ToolInput):
    origin: str
    destination: str
    departure_date: str
    return_date: str | None = None
    travelers: int = 1


class FlightOption(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    currency: str = "USD"


class FlightSearchOutput(ToolOutput):
    options: list[FlightOption] = []


class HotelSearchInput(ToolInput):
    destination: str
    check_in_date: str
    check_out_date: str
    guests: int = 1


class HotelOption(BaseModel):
    name: str
    star_rating: float
    price_per_night: float
    currency: str = "USD"


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


class ToolCallResult(BaseModel):
    """Uniform envelope the ToolExecutor returns for every tool invocation,
    regardless of which concrete *Input/*Output pair was used."""

    tool_name: ToolName
    status: ActionStatus
    input: dict
    output: dict | None = None
    error_message: str | None = None
