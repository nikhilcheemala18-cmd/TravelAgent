"""Schemas describing the outcome of verifying ToolExecutionResults.

Produced by the Validator (app/agent/validator.py) and consumed by the
FallbackManager (app/agent/fallback_manager.py). The Validator only ever
reports what's wrong with a result — deciding what to do about it lives
entirely in FallbackManager.
"""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import ToolName, ValidationSeverity
from app.schemas.tool_execution import ToolExecutionResult


class FailureReason(StrEnum):
    """Why a single tool result failed validation.

    This is what lets FallbackManager decide retryability without
    re-inspecting error strings itself: EXECUTION_FAILED and TIMEOUT are
    treated as transient (worth a retry); MISSING_TOOL and MALFORMED_DATA
    are structural and won't change on a retry with the same arguments.
    EMPTY_RESPONSE is reported as a warning, not an error, so it never
    reaches the retry path at all.
    """

    MISSING_TOOL = "missing_tool"
    EXECUTION_FAILED = "execution_failed"
    TIMEOUT = "timeout"
    EMPTY_RESPONSE = "empty_response"
    MALFORMED_DATA = "malformed_data"
    INCOMPLETE_DATA = "incomplete_data"


class ValidationStatus(StrEnum):
    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    FAILED = "failed"


class ValidationIssue(BaseModel):
    tool_name: ToolName | None = None
    field: str | None = None
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    reason: FailureReason | None = None


class ValidatedToolResult(BaseModel):
    """One ToolExecutionResult plus the Validator's judgment about it."""

    tool_name: ToolName
    is_valid: bool
    result: ToolExecutionResult
    issues: list[ValidationIssue] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Structured validation report for a full ExecutionPlan run.

    `passed` is a convenience flag (True unless overall_status is FAILED);
    prefer `overall_status` when the passed/warnings distinction matters,
    e.g. to decide whether recovery should even be attempted.
    """

    overall_status: ValidationStatus
    passed: bool
    failed_tools: list[ToolName] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    validated_results: list[ValidatedToolResult] = Field(default_factory=list)
