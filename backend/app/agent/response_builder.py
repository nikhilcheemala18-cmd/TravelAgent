"""Response Builder.

Assembles the final ChatResponse for a completed pipeline run: the
Itinerary from ItineraryBuilder, plus business-level summaries of what
happened during execution/validation/fallback — never raw internals (tool
arguments, timings, retry-sleep mechanics). Kept separate from
ItineraryBuilder so "what's the travel data" and "what's the API envelope
around it" can change independently; this class builds no travel data of
its own; it only reads what ItineraryBuilder, Validator, and
FallbackManager already produced.
"""

from app.schemas.common import ActionStatus, ToolName
from app.schemas.conversation import ChatResponse
from app.schemas.fallback import FallbackOutcome
from app.schemas.itinerary import Itinerary
from app.schemas.response import ExecutionSummary, FallbackSummary, ToolResultSummary, ValidationSummary
from app.schemas.tool_execution import ToolExecutionResult
from app.schemas.validation import ValidationResult
from app.utils.logging import get_logger

logger = get_logger(__name__)

_DISPLAY_NAMES: dict[ToolName, str] = {
    ToolName.FLIGHT_SEARCH: "Flights",
    ToolName.HOTEL_SEARCH: "Hotels",
    ToolName.CAR_RENTAL_SEARCH: "Car rentals",
}


class ResponseBuilder:
    def build_response(
        self,
        session_id: str,
        itinerary: Itinerary,
        results: list[ToolExecutionResult],
        validation: ValidationResult,
        fallback: FallbackOutcome,
    ) -> ChatResponse:
        """Build the ChatResponse for a run that reached ItineraryBuilder.

        Works whether the run was a full success, a partial success, or a
        total failure (an empty itinerary with everything listed under
        unavailable_services) — `success` reflects whether the itinerary
        actually contains anything bookable, not whether every tool
        happened to succeed.
        """
        response = ChatResponse(
            session_id=session_id,
            reply=itinerary.overview or "Here's what I found.",
            itinerary=itinerary,
            execution_summary=self._build_execution_summary(results),
            tool_results_summary=self._build_tool_results_summary(results, fallback),
            validation_summary=self._build_validation_summary(validation),
            fallback_summary=self._build_fallback_summary(fallback),
            warnings=itinerary.warnings,
            success=bool(
                itinerary.flight_options or itinerary.hotel_options or itinerary.car_rental_options
            ),
        )
        logger.info(
            "Response generated for session %s (success=%s, partial=%s)",
            session_id,
            response.success,
            itinerary.is_partial,
        )
        return response

    @staticmethod
    def _build_execution_summary(results: list[ToolExecutionResult]) -> ExecutionSummary:
        successful = sum(1 for result in results if result.status == ActionStatus.SUCCESS)
        return ExecutionSummary(
            total_tools=len(results),
            successful_tools=successful,
            failed_tools=len(results) - successful,
            total_execution_time_ms=round(sum(result.execution_time_ms for result in results), 2),
        )

    @staticmethod
    def _build_tool_results_summary(
        results: list[ToolExecutionResult], fallback: FallbackOutcome
    ) -> list[ToolResultSummary]:
        recovered_tools = {attempt.tool_name for attempt in fallback.retry_attempts if attempt.succeeded}
        summaries = []
        for result in results:
            items_found = len((result.returned_data or {}).get("options", []))
            summaries.append(
                ToolResultSummary(
                    tool_name=result.tool_name,
                    display_name=_DISPLAY_NAMES.get(result.tool_name, result.tool_name.value),
                    status=result.status,
                    items_found=items_found,
                    recovered=result.tool_name in recovered_tools,
                )
            )
        return summaries

    @staticmethod
    def _build_validation_summary(validation: ValidationResult) -> ValidationSummary:
        issues_count = sum(len(validated.issues) for validated in validation.validated_results)
        return ValidationSummary(
            overall_status=validation.overall_status,
            issues_count=issues_count,
            warnings_count=len(validation.warnings),
        )

    @staticmethod
    def _build_fallback_summary(fallback: FallbackOutcome) -> FallbackSummary:
        recovered = sorted({attempt.tool_name for attempt in fallback.retry_attempts if attempt.succeeded})
        return FallbackSummary(
            fallback_triggered=fallback.fallback_triggered,
            tools_recovered=recovered,
            tools_unavailable=fallback.unresolved_tools,
            total_retry_attempts=len(fallback.retry_attempts),
        )
