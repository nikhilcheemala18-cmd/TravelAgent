"""Validator.

Checks tool results (and, in future, the plan/user input) against business
rules before they are used to build an itinerary — e.g. dates make sense,
prices are within budget, required fields are present. Kept independent of
the ToolExecutor and ItineraryBuilder so rules can evolve without touching
either.
"""

from abc import ABC, abstractmethod

from app.schemas.tools import ToolCallResult
from app.schemas.validation import ValidationResult


class Validator(ABC):
    @abstractmethod
    def validate(self, results: list[ToolCallResult]) -> ValidationResult:
        """Validate a batch of tool results, returning aggregated issues."""


class PassThroughValidator(Validator):
    """Placeholder validator — accepts anything that isn't a hard failure.

    TODO: add real rules, e.g.:
      - required fields present per tool type
      - price/date sanity checks
      - budget constraints from ConversationState.travel_session
    """

    def validate(self, results: list[ToolCallResult]) -> ValidationResult:
        from app.schemas.common import ActionStatus
        from app.schemas.validation import ValidationIssue, ValidationSeverity

        issues = [
            ValidationIssue(
                field=result.tool_name,
                message=result.error_message or "Tool call failed.",
                severity=ValidationSeverity.ERROR,
            )
            for result in results
            if result.status == ActionStatus.FAILED
        ]
        return ValidationResult(is_valid=not issues, issues=issues)
