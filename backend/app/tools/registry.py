"""Registry mapping ToolName -> tool instance.

The ToolExecutor looks up tools here by name rather than importing concrete
tool classes directly, so adding a new tool (or swapping a mock for a real
provider-backed implementation) never requires touching the executor.
"""

from app.schemas.common import ToolName
from app.tools.base import BaseTool
from app.tools.car_rental import CarRentalSearchTool
from app.tools.flight_search import FlightSearchTool
from app.tools.hotel_search import HotelSearchTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[ToolName, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, tool_name: ToolName) -> BaseTool:
        if tool_name not in self._tools:
            raise KeyError(f"No tool registered for '{tool_name}'")
        return self._tools[tool_name]

    def list_tools(self) -> list[ToolName]:
        return list(self._tools.keys())


def build_default_registry() -> ToolRegistry:
    """Wires up the mock tool implementations available today.

    Replace individual tool instances with real-provider-backed ones as
    they become available — callers only depend on this factory / the
    ToolRegistry interface, not on which concrete tools it contains.
    """
    registry = ToolRegistry()
    registry.register(FlightSearchTool())
    registry.register(HotelSearchTool())
    registry.register(CarRentalSearchTool())
    return registry
