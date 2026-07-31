"""Validator.

Verifies ToolExecutionResults before they're trusted enough to build an
itinerary from: did each tool actually run, did it return the shape of
data the rest of the agent expects, and is anything conspicuously empty
or malformed. It only inspects results that already happened — it never
re-runs a tool, never changes the ExecutionPlan that produced them, and
never decides what to do about a bad result (that's FallbackManager's
job, one stage downstream) or presents anything to the user (that's
ItineraryBuilder's).
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ValidationError

from app.schemas.common import ActionStatus, ToolName
from app.schemas.tool_execution import ToolExecutionResult
from app.schemas.tools import CarRentalOption, FlightOption, HotelOption
from app.schemas.validation import (
    FailureReason,
    ValidatedToolResult,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    ValidationStatus,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

# The shape a SUCCESS result's returned_data must have to be usable
# downstream: an "options" list whose entries validate against the
# matching tool's option schema (app/schemas/tools.py).
_OPTION_MODEL_BY_TOOL: dict[ToolName, type[BaseModel]] = {
    ToolName.FLIGHT_SEARCH: FlightOption,
    ToolName.HOTEL_SEARCH: HotelOption,
    ToolName.CAR_RENTAL_SEARCH: CarRentalOption,
}

_MISSING_TOOL_MARKER = "no tool registered for"
_TIMEOUT_MARKER = "timeout"


class Validator(ABC):
    @abstractmethod
    def validate(self, results: list[ToolExecutionResult]) -> ValidationResult:
        """Verify a batch of tool results, returning a structured report."""


class DefaultValidator(Validator):
    """Rule-based validator.

    For each result: if the tool execution failed, classify *why* (so
    FallbackManager can judge retryability without re-parsing error
    strings itself). If it succeeded, check `returned_data` has the
    expected "options" list and that every entry in it validates against
    that tool's option schema; an empty list is flagged as a warning, not
    a failure.
    """

    def validate(self, results: list[ToolExecutionResult]) -> ValidationResult:
        validated_results: list[ValidatedToolResult] = []
        failed_tools: list[ToolName] = []
        warnings: list[ValidationIssue] = []
        has_failures = False

        for result in results:
            issues = self._validate_one(result)
            is_valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)

            if not is_valid:
                has_failures = True
                failed_tools.append(result.tool_name)
                logger.warning(
                    "Validation failed for %s: %s",
                    result.tool_name,
                    "; ".join(issue.message for issue in issues) or "unknown reason",
                )

            warnings.extend(issue for issue in issues if issue.severity == ValidationSeverity.WARNING)
            validated_results.append(
                ValidatedToolResult(
                    tool_name=result.tool_name,
                    is_valid=is_valid,
                    result=result,
                    issues=issues,
                )
            )

        if has_failures:
            overall_status = ValidationStatus.FAILED
        elif warnings:
            overall_status = ValidationStatus.PASSED_WITH_WARNINGS
        else:
            overall_status = ValidationStatus.PASSED

        return ValidationResult(
            overall_status=overall_status,
            passed=overall_status != ValidationStatus.FAILED,
            failed_tools=failed_tools,
            warnings=warnings,
            validated_results=validated_results,
        )

    def _validate_one(self, result: ToolExecutionResult) -> list[ValidationIssue]:
        if result.status == ActionStatus.FAILED:
            return [self._classify_failure(result)]
        return self._validate_success(result)

    @staticmethod
    def _classify_failure(result: ToolExecutionResult) -> ValidationIssue:
        message = result.error_message or "Tool execution failed with no error detail."
        lowered = message.lower()

        if _MISSING_TOOL_MARKER in lowered:
            reason = FailureReason.MISSING_TOOL
        elif _TIMEOUT_MARKER in lowered:
            reason = FailureReason.TIMEOUT
        else:
            reason = FailureReason.EXECUTION_FAILED

        return ValidationIssue(
            tool_name=result.tool_name,
            message=message,
            severity=ValidationSeverity.ERROR,
            reason=reason,
        )

    def _validate_success(self, result: ToolExecutionResult) -> list[ValidationIssue]:
        if not result.returned_data or "options" not in result.returned_data:
            return [
                ValidationIssue(
                    tool_name=result.tool_name,
                    message=f"{result.tool_name} succeeded but returned no recognizable data.",
                    severity=ValidationSeverity.ERROR,
                    reason=FailureReason.INCOMPLETE_DATA,
                )
            ]

        options = result.returned_data["options"]

        if not options:
            # The tool itself is in the best position to explain *why* —
            # e.g. an unsupported destination or nothing within budget —
            # so relay that verbatim rather than a generic templated
            # message when it provided one. Validator doesn't need to
            # understand the reason, only pass it along.
            message = result.returned_data.get("empty_reason") or f"{result.tool_name} returned no options."
            return [
                ValidationIssue(
                    tool_name=result.tool_name,
                    message=message,
                    severity=ValidationSeverity.WARNING,
                    reason=FailureReason.EMPTY_RESPONSE,
                )
            ]

        option_model = _OPTION_MODEL_BY_TOOL.get(result.tool_name)
        if option_model is None:
            return []

        issues: list[ValidationIssue] = []
        for index, option in enumerate(options):
            try:
                option_model.model_validate(option)
            except ValidationError as exc:
                issues.append(
                    ValidationIssue(
                        tool_name=result.tool_name,
                        field=f"options[{index}]",
                        message=f"Malformed option data: {exc}",
                        severity=ValidationSeverity.ERROR,
                        reason=FailureReason.MALFORMED_DATA,
                    )
                )
        return issues
