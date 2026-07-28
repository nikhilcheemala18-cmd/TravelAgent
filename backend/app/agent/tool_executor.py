"""Tool Executor.

Runs an ExecutionPlan: for each ExecutionStep, in priority order, look the
tool up in the ToolRegistry and run it, recording a ToolExecutionResult.
That's the entire job. This module does not decide what to run (Planner),
does not judge whether results are good enough (Validator), does not
decide what to do about a failure beyond recording it (FallbackManager),
and does not assemble a user-facing itinerary (ItineraryBuilder) — those
all consume its output but live elsewhere.

Tool lookup always goes through ToolRegistry.get_tool, never a per-tool
if/elif — adding a new tool means registering it, not branching here.
"""

import time

from app.schemas.agent import ExecutionPlan, ExecutionStep
from app.schemas.common import ActionStatus
from app.schemas.tool_execution import ToolExecutionResult
from app.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute_plan(self, plan: ExecutionPlan) -> list[ToolExecutionResult]:
        """Run every step of `plan` in priority order and collect results.

        A single step failing does not stop the remaining steps — each
        step's outcome is captured independently in its own result.
        """
        return [self.execute_step(step) for step in plan.ordered_steps()]

    def execute_step(self, step: ExecutionStep) -> ToolExecutionResult:
        started_at = time.perf_counter()

        try:
            tool = self._registry.get_tool(step.tool_name)
        except KeyError as exc:
            return self._failure_result(step, str(exc), started_at)

        try:
            # NOTE: real tool implementations will validate/parse
            # step.arguments into their specific *Input model before
            # calling execute(); mocks currently accept the raw dict.
            output = tool.execute(step.arguments)
        except Exception as exc:  # noqa: BLE001 - a broken tool must not crash the agent
            return self._failure_result(step, str(exc), started_at)

        return ToolExecutionResult(
            tool_name=step.tool_name,
            status=ActionStatus.SUCCESS if output.success else ActionStatus.FAILED,
            arguments=step.arguments,
            returned_data=output.model_dump(),
            error_message=output.error_message,
            execution_time_ms=self._elapsed_ms(started_at),
        )

    def _failure_result(
        self, step: ExecutionStep, error_message: str, started_at: float
    ) -> ToolExecutionResult:
        return ToolExecutionResult(
            tool_name=step.tool_name,
            status=ActionStatus.FAILED,
            arguments=step.arguments,
            error_message=error_message,
            execution_time_ms=self._elapsed_ms(started_at),
        )

    @staticmethod
    def _elapsed_ms(started_at: float) -> float:
        return (time.perf_counter() - started_at) * 1000
