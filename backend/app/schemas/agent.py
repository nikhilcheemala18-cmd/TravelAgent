"""Schemas describing the Agent Planner's output.

The plan is the contract between the Planner and the ToolExecutor: the
planner decides *what* to do, the executor decides *how* to run it.
"""

from pydantic import BaseModel

from app.schemas.common import IntentType, ToolName


class PlannedAction(BaseModel):
    tool_name: ToolName
    tool_input: dict
    rationale: str | None = None


class AgentPlan(BaseModel):
    intent: IntentType
    actions: list[PlannedAction] = []
    needs_clarification: bool = False
    clarification_question: str | None = None
