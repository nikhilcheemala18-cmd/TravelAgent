"""Agent Orchestrator.

Wires the pipeline together: ConversationManager -> Planner -> ToolExecutor
-> Validator -> (FallbackManager | ItineraryBuilder). This is the single
place that knows the *order* of the agent loop; every other component only
knows its own step.
"""

from app.agent.conversation_manager import ConversationManager
from app.agent.fallback_manager import FallbackManager
from app.agent.itinerary_builder import ItineraryBuilder
from app.agent.planner import Planner
from app.agent.tool_executor import ToolExecutor
from app.agent.validator import Validator
from app.schemas.agent import ClarificationAction
from app.schemas.conversation import ChatRequest, ChatResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class TravelAgentOrchestrator:
    def __init__(
        self,
        conversation_manager: ConversationManager,
        planner: Planner,
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
            decision = self._planner.create_plan(request.message, state.travel_session)
        except Exception as exc:  # noqa: BLE001 - planner failures must not crash the agent
            logger.exception("Planner failed for session %s", state.session_id)
            reply = self._fallback_manager.handle_planning_failure(exc)
            self._conversation_manager.add_assistant_message(state, reply)
            return ChatResponse(session_id=state.session_id, reply=reply)

        # The planner always returns the session with any newly extracted
        # values merged in, even when it still needs clarification.
        state.travel_session = decision.session

        if isinstance(decision, ClarificationAction):
            self._conversation_manager.add_assistant_message(state, decision.question)
            return ChatResponse(
                session_id=state.session_id,
                reply=decision.question,
                requires_clarification=True,
                missing_slots=decision.missing_slots,
            )

        results = self._tool_executor.execute_plan(decision)
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
