"""Schemas describing FallbackManager output.

Kept separate from schemas/validation.py because a FallbackOutcome is a
recovery report, not a verification report — it describes what
FallbackManager *did* about a ValidationResult, not what the Validator
observed.
"""

from pydantic import BaseModel, Field

from app.schemas.common import ToolName
from app.schemas.tool_execution import ToolExecutionResult


class RetryAttempt(BaseModel):
    """Record of one retry attempt against a single previously-failed tool."""

    tool_name: ToolName
    attempt_number: int
    succeeded: bool
    error_message: str | None = None


class FallbackOutcome(BaseModel):
    """Structured result of FallbackManager.handle_validation_result().

    `results` is the final set of ToolExecutionResults the ItineraryBuilder
    should consume: every originally-successful result untouched, plus
    whatever a retry produced for tools that were retried, plus the
    still-failed result for anything that couldn't be recovered — the
    ItineraryBuilder already skips non-SUCCESS results on its own.

    `resolved` is True when at least one usable (SUCCESS) result exists
    after recovery — i.e. there's something worth building an itinerary
    from, even if it's partial.
    """

    fallback_triggered: bool
    resolved: bool
    results: list[ToolExecutionResult] = Field(default_factory=list)
    retry_attempts: list[RetryAttempt] = Field(default_factory=list)
    unresolved_tools: list[ToolName] = Field(default_factory=list)
    message: str | None = None
