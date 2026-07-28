"""Agent Orchestrator.

Wires the pipeline together: ConversationManager -> AgentPlanner ->
ToolExecutor -> Validator -> (FallbackManager | ItineraryBuilder). This is
the single place that knows the *order* of the agent loop; every other
component only knows its own step.
"""

from app.agent.conversation_manager import ConversationManager
from app.agent.fallback_manager import FallbackManager
from app.agent.itinerary_builder import ItineraryBuilder
from app.agent.planner import AgentPlanner
from app.agent.tool_executor import ToolExecutor
from app.agent.validator import Validator
from app.schemas.conversation import ChatRequest, ChatResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class TravelAgentOrchestrator:
    def __init__(
        self,
        conversation_manager: ConversationManager,
        planner: AgentPlanner,
        tool_executor: ToolExecutor,
        validator: Validator,
        fallback_manager: FallbackManager,
        itinerary_builder: ItineraryBuilder,
    ) -> None:
        self._conversation_manager = conversation_manager
        self._planner = planner
        self._tool_executor = tool_executor
        self._validator = validator
        self._fallback_manager = fallback_manager
        self._itinerary_builder = itinerary_builder

    def handle_message(self, request: ChatRequest) -> ChatResponse:
        state = self._conversation_manager.get_or_create_session(request.session_id)
        self._conversation_manager.add_user_message(state, request.message)

        try:
            plan = self._planner.create_plan(state, request.message)
        except Exception as exc:  # noqa: BLE001 - planner failures must not crash the agent
            logger.exception("Planner failed for session %s", state.session_id)
            reply = self._fallback_manager.handle_planning_failure(exc)
            self._conversation_manager.add_assistant_message(state, reply)
            return ChatResponse(session_id=state.session_id, reply=reply)

        if plan.needs_clarification:
            reply = plan.clarification_question or "Could you provide more details?"
            self._conversation_manager.add_assistant_message(state, reply)
            return ChatResponse(
                session_id=state.session_id, reply=reply, requires_clarification=True
            )

        results = self._tool_executor.execute_plan(plan)
        validation = self._validator.validate(results)

        if not validation.is_valid:
            reply = self._fallback_manager.handle_validation_failure(validation)
            self._conversation_manager.add_assistant_message(state, reply)
            return ChatResponse(session_id=state.session_id, reply=reply)

        itinerary = self._itinerary_builder.build(results)
        reply = itinerary.summary or "Here's what I found."
        self._conversation_manager.add_assistant_message(state, reply)

        return ChatResponse(
            session_id=state.session_id,
            reply=reply,
            itinerary=itinerary,
        )
