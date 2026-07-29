"""Business-level summary schemas that ride alongside an Itinerary inside
ChatResponse — a frontend's "what happened" panel, without exposing tool
arguments, raw timings, or retry-sleep mechanics.
"""

from pydantic import BaseModel, Field

from app.schemas.common import ActionStatus, ToolName
from app.schemas.validation import ValidationStatus


class ExecutionSummary(BaseModel):
    """Roll-up of how the ExecutionPlan ran."""

    total_tools: int
    successful_tools: int
    failed_tools: int
    total_execution_time_ms: float


class ToolResultSummary(BaseModel):
    """Per-tool outcome, business-level: what was searched, how many
    results came back, whether it needed a retry — not the raw arguments
    or payload."""

    tool_name: ToolName
    display_name: str
    status: ActionStatus
    items_found: int
    recovered: bool = False


class ValidationSummary(BaseModel):
    overall_status: ValidationStatus
    issues_count: int
    warnings_count: int


class FallbackSummary(BaseModel):
    fallback_triggered: bool
    tools_recovered: list[ToolName] = Field(default_factory=list)
    tools_unavailable: list[ToolName] = Field(default_factory=list)
    total_retry_attempts: int = 0
