"""Schemas describing Planner output.

The Planner produces exactly one of two things:
  - a ClarificationAction, when required trip details are still missing
  - an ExecutionPlan, once enough is known to search for options

The Planner only ever builds these; it never executes anything. Executing
an ExecutionPlan's steps is the ToolExecutor's job.
"""

from pydantic import BaseModel, Field

from app.schemas.common import ToolName
from app.schemas.travel_session import TravelSession


class ExecutionStep(BaseModel):
    """A single tool invocation for the ToolExecutor to perform.

    `priority` defines execution order (lower runs first); it does not
    imply steps run in parallel or depend on one another.
    """

    tool_name: ToolName
    arguments: dict
    priority: int = 0


class ExecutionPlan(BaseModel):
    """A ready-to-execute plan, produced once every required TravelSession
    slot is filled."""

    session: TravelSession
    steps: list[ExecutionStep] = Field(default_factory=list)

    def ordered_steps(self) -> list[ExecutionStep]:
        return sorted(self.steps, key=lambda step: step.priority)


class ClarificationAction(BaseModel):
    """Returned when required trip details are still missing.

    `session` is the TravelSession with anything successfully extracted
    from the latest message already merged in, so callers persist it even
    though no ExecutionPlan was produced yet.
    """

    session: TravelSession
    missing_slots: list[str]
    question: str
