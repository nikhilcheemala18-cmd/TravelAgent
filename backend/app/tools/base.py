"""Base interface every travel tool must implement.

A "tool" is a single capability the agent can invoke (search flights,
search hotels, ...). Implementations here are mocks; each is the single
place a real provider integration (Amadeus, Skyscanner, Booking.com, etc.)
will plug in later — the rest of the agent only ever talks to this
interface, never to a concrete provider SDK.
"""

from abc import ABC, abstractmethod

from app.schemas.common import ToolName
from app.schemas.tools import ToolInput, ToolOutput


class BaseTool(ABC):
    name: ToolName

    @abstractmethod
    def execute(self, tool_input: ToolInput) -> ToolOutput:
        """Run the tool synchronously and return a structured output.

        Implementations should not raise for expected failure modes (no
        results, provider error) — encode that in ToolOutput.success /
        error_message instead. Let unexpected exceptions propagate; the
        ToolExecutor is responsible for catching those.
        """
