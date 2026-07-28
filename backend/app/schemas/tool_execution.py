"""Schemas describing the outcome of running an ExecutionPlan.

Separate from app/schemas/tools.py (the per-tool *Input/*Output contracts)
because ToolExecutionResult is the ToolExecutor's own output envelope — it
wraps whatever a tool returned with the bookkeeping (status, timing) that
callers downstream of execution actually need, without caring which
concrete tool produced it.
"""

from pydantic import BaseModel

from app.schemas.common import ActionStatus, ToolName


class ToolExecutionResult(BaseModel):
    """Uniform result of running a single ExecutionStep.

    `returned_data` holds the tool's raw ToolOutput, serialized to a dict —
    the ToolExecutor doesn't know or care about a specific tool's output
    shape, only that it succeeded or failed.
    """

    tool_name: ToolName
    status: ActionStatus
    arguments: dict
    returned_data: dict | None = None
    error_message: str | None = None
    execution_time_ms: float
