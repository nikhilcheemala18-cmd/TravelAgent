"""Fallback Manager.

Decides what happens after validation finds a problem: whether recovery is
even worth attempting, retries the specific tools whose failure looks
transient (bounded — never infinite), and reports a structured outcome.
It never plans, never talks to an LLM, never builds an itinerary, and the
only "execution" it triggers is re-running an already-planned step through
the injected ToolExecutor — it does not call a tool implementation itself.

Also still handles the pre-validation failure paths the orchestrator has
always needed (the Planner raising, or tool execution raising outright) —
those produce a plain user-facing message rather than a FallbackOutcome,
since there's no ToolExecutionResult to recover in either case.
"""

import time
from abc import ABC, abstractmethod

from app.agent.tool_executor import ToolExecutor
from app.schemas.agent import ExecutionStep
from app.schemas.common import ActionStatus, ToolName
from app.schemas.fallback import FallbackOutcome, RetryAttempt
from app.schemas.tool_execution import ToolExecutionResult
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

# Only these are worth retrying: EXECUTION_FAILED/TIMEOUT plausibly reflect
# a one-off glitch. MISSING_TOOL and MALFORMED_DATA are structural — the
# same tool called with the same arguments will fail the same way again.
_RETRYABLE_REASONS = frozenset({FailureReason.EXECUTION_FAILED, FailureReason.TIMEOUT})


class FallbackManager(ABC):
    @abstractmethod
    def handle_validation_result(self, validation: ValidationResult) -> FallbackOutcome:
        """Attempt recovery for a validated batch of tool results."""

    @abstractmethod
    def handle_planning_failure(self, error: Exception) -> str:
        """Return a user-facing message when the planner raises."""

    @abstractmethod
    def handle_execution_failure(self, error: Exception) -> str:
        """Return a user-facing message when tool execution raises unexpectedly."""


class DefaultFallbackManager(FallbackManager):
    """Retry-capable fallback strategy.

    Retry policy (max attempts / delay) is injected rather than hardcoded
    — see Settings.fallback_max_retries / fallback_retry_delay_ms.
    """

    def __init__(self, tool_executor: ToolExecutor, max_retries: int, retry_delay_ms: int) -> None:
        self._tool_executor = tool_executor
        self._max_retries = max(0, max_retries)
        self._retry_delay_ms = max(0, retry_delay_ms)

    def handle_validation_result(self, validation: ValidationResult) -> FallbackOutcome:
        if validation.overall_status != ValidationStatus.FAILED:
            # Nothing failed — PASSED or PASSED_WITH_WARNINGS both flow
            # straight through untouched, no recovery needed.
            return FallbackOutcome(
                fallback_triggered=False,
                resolved=True,
                results=[validated.result for validated in validation.validated_results],
            )

        logger.warning(
            "Validation failed for tools %s — attempting recovery.", validation.failed_tools
        )
        return self._attempt_recovery(validation.validated_results)

    def handle_planning_failure(self, error: Exception) -> str:
        return "I'm having trouble understanding that request right now. Could you rephrase it?"

    def handle_execution_failure(self, error: Exception) -> str:
        return "Something went wrong while looking that up. Please try again in a moment."

    # -- Recovery ---------------------------------------------------------

    def _attempt_recovery(self, validated_results: list[ValidatedToolResult]) -> FallbackOutcome:
        final_results: list[ToolExecutionResult] = []
        retry_attempts: list[RetryAttempt] = []
        unresolved_tools: list[ToolName] = []

        for validated in validated_results:
            if validated.is_valid:
                final_results.append(validated.result)
                continue

            reason = self._primary_error_reason(validated.issues)

            if reason not in _RETRYABLE_REASONS:
                logger.warning(
                    "Not retrying %s: reason '%s' is not transient.",
                    validated.tool_name,
                    reason.value if reason else "unknown",
                )
                final_results.append(validated.result)
                unresolved_tools.append(validated.tool_name)
                continue

            recovered = self._retry_tool(validated.result, retry_attempts)
            final_results.append(recovered)
            if recovered.status != ActionStatus.SUCCESS:
                unresolved_tools.append(validated.tool_name)

        resolved = any(result.status == ActionStatus.SUCCESS for result in final_results)
        message = self._build_message(unresolved_tools, resolved)

        if resolved:
            logger.info(
                "Fallback recovery complete: %d/%d tools usable, unresolved=%s",
                len(final_results) - len(unresolved_tools),
                len(final_results),
                unresolved_tools,
            )
        else:
            logger.warning("Fallback recovery failed — no usable results for any tool.")

        return FallbackOutcome(
            fallback_triggered=True,
            resolved=resolved,
            results=final_results,
            retry_attempts=retry_attempts,
            unresolved_tools=unresolved_tools,
            message=message,
        )

    def _retry_tool(
        self, failed_result: ToolExecutionResult, retry_attempts: list[RetryAttempt]
    ) -> ToolExecutionResult:
        step = ExecutionStep(
            tool_name=failed_result.tool_name, arguments=failed_result.arguments, priority=0
        )
        latest_result = failed_result

        for attempt_number in range(1, self._max_retries + 1):
            if self._retry_delay_ms > 0:
                time.sleep(self._retry_delay_ms / 1000)

            logger.info("Retrying %s (attempt %d/%d)", step.tool_name, attempt_number, self._max_retries)
            latest_result = self._tool_executor.execute_step(step)
            retry_attempts.append(
                RetryAttempt(
                    tool_name=step.tool_name,
                    attempt_number=attempt_number,
                    succeeded=latest_result.status == ActionStatus.SUCCESS,
                    error_message=latest_result.error_message,
                )
            )

            if latest_result.status == ActionStatus.SUCCESS:
                logger.info("Retry succeeded for %s after %d attempt(s).", step.tool_name, attempt_number)
                return latest_result

        if self._max_retries > 0:
            logger.warning(
                "Retry exhausted for %s after %d attempt(s).", step.tool_name, self._max_retries
            )
        return latest_result

    @staticmethod
    def _primary_error_reason(issues: list[ValidationIssue]) -> FailureReason | None:
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR and issue.reason is not None:
                return issue.reason
        return None

    @staticmethod
    def _build_message(unresolved_tools: list[ToolName], resolved: bool) -> str | None:
        if not unresolved_tools:
            return None

        tool_list = ", ".join(sorted({tool.value for tool in unresolved_tools}))
        if resolved:
            return f"I found some options, but couldn't get results for: {tool_list}."
        return f"I couldn't retrieve results for: {tool_list}. Please try again in a moment."
