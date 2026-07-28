"""Tool Executor.

Takes an ExecutionPlan produced by the Planner and runs each ExecutionStep
against the ToolRegistry, in priority order, returning a uniform list of
ToolCallResult. This is the only layer that touches concrete tool
instances — the Planner only ever produces ExecutionStep data.
"""

from app.schemas.agent import ExecutionPlan, ExecutionStep
from app.schemas.common import ActionStatus
from app.schemas.tools import ToolCallResult
from app.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute_plan(self, plan: ExecutionPlan) -> list[ToolCallResult]:
        return [self.execute_step(step) for step in plan.ordered_steps()]

    def execute_step(self, step: ExecutionStep) -> ToolCallResult:
        try:
            tool = self._registry.get(step.tool_name)
        except KeyError as exc:
            return ToolCallResult(
                tool_name=step.tool_name,
                status=ActionStatus.FAILED,
                input=step.arguments,
                error_message=str(exc),
            )

        try:
            # NOTE: real tool implementations will validate/parse
            # step.arguments into their specific *Input model before
            # calling execute(); mocks currently accept the raw dict.
            output = tool.execute(step.arguments)
        except Exception as exc:  # noqa: BLE001 - tool failures must not crash the agent
            return ToolCallResult(
                tool_name=step.tool_name,
                status=ActionStatus.FAILED,
                input=step.arguments,
                error_message=str(exc),
            )

        return ToolCallResult(
            tool_name=step.tool_name,
            status=ActionStatus.SUCCESS if output.success else ActionStatus.FAILED,
            input=step.arguments,
            output=output.model_dump(),
            error_message=output.error_message,
        )
