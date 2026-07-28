"""Tool Executor.

Takes an AgentPlan produced by the planner and runs each PlannedAction
against the ToolRegistry, returning a uniform list of ToolCallResult. This
is the only layer that touches concrete tool instances — planner and
orchestrator only ever see ToolCallResult envelopes.
"""

from app.schemas.agent import AgentPlan, PlannedAction
from app.schemas.common import ActionStatus
from app.schemas.tools import ToolCallResult
from app.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute_plan(self, plan: AgentPlan) -> list[ToolCallResult]:
        return [self.execute_action(action) for action in plan.actions]

    def execute_action(self, action: PlannedAction) -> ToolCallResult:
        try:
            tool = self._registry.get(action.tool_name)
        except KeyError as exc:
            return ToolCallResult(
                tool_name=action.tool_name,
                status=ActionStatus.FAILED,
                input=action.tool_input,
                error_message=str(exc),
            )

        try:
            # NOTE: real tool implementations will validate/parse
            # action.tool_input into their specific *Input model before
            # calling execute(); mocks currently accept the raw dict.
            output = tool.execute(action.tool_input)
        except Exception as exc:  # noqa: BLE001 - tool failures must not crash the agent
            return ToolCallResult(
                tool_name=action.tool_name,
                status=ActionStatus.FAILED,
                input=action.tool_input,
                error_message=str(exc),
            )

        return ToolCallResult(
            tool_name=action.tool_name,
            status=ActionStatus.SUCCESS if output.success else ActionStatus.FAILED,
            input=action.tool_input,
            output=output.model_dump(),
            error_message=output.error_message,
        )
