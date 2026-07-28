"""Agent Planner.

The "thinking" component of the agent: given the latest user message and
the current TravelSession, it decides whether enough is known to build an
ExecutionPlan, or whether the user still needs to be asked for more
details (ClarificationAction). This decision, not a fixed dialogue tree,
is what makes the system an agent.

The Planner never touches a SessionStore, never calls a tool, never
validates tool output, and never builds an itinerary. It also never talks
to an LLM directly, and holds no provider-specific logic: extracting
values from the message is delegated to a SlotExtractor (which may or may
not be LLM-backed), and merging those values into the session / judging
completeness is delegated to the ConversationManager. This class stays
focused on the planning decision itself.
"""

from abc import ABC, abstractmethod

from app.agent.conversation_manager import ConversationManager
from app.agent.extraction import SlotExtractor
from app.schemas.agent import ClarificationAction, ExecutionPlan, ExecutionStep
from app.schemas.common import ToolName
from app.schemas.travel_session import TravelSession

_SLOT_PROMPTS: dict[str, str] = {
    "origin": "where you'll be departing from",
    "destination": "your destination",
    "departure_date": "your departure date (e.g. 2026-08-01)",
    "return_date": "your return date (e.g. 2026-08-10)",
    "passengers": "how many passengers are traveling",
}


class Planner(ABC):
    @abstractmethod
    def create_plan(
        self, message: str, session: TravelSession
    ) -> ClarificationAction | ExecutionPlan:
        """Produce the next planning decision for the given message and
        current TravelSession. Must never execute a tool."""


class LLMPlanner(Planner):
    """Planner whose language understanding comes from an LLM-backed
    SlotExtractor.

    The extraction step can raise SlotExtractionError when the LLM returns
    output that can't be trusted (invalid JSON, wrong types, ...). This
    class deliberately does not catch it: the Planner performs no
    retries and no fallback handling — it lets the error propagate so the
    orchestrator's existing planning-failure path (FallbackManager) can
    turn it into a graceful, descriptive response.
    """

    def __init__(
        self, conversation_manager: ConversationManager, extractor: SlotExtractor
    ) -> None:
        self._conversation_manager = conversation_manager
        self._extractor = extractor

    def create_plan(
        self, message: str, session: TravelSession
    ) -> ClarificationAction | ExecutionPlan:
        extracted = self._extractor.extract(message, session)
        updated_session = self._conversation_manager.update_session(session, extracted)
        missing = self._conversation_manager.get_missing_slots(updated_session)

        if missing:
            return ClarificationAction(
                session=updated_session,
                missing_slots=missing,
                question=self._build_clarification_question(missing),
            )

        return ExecutionPlan(
            session=updated_session,
            steps=self._build_steps(updated_session),
        )

    @staticmethod
    def _build_clarification_question(missing_slots: list[str]) -> str:
        prompts = [_SLOT_PROMPTS[slot] for slot in missing_slots if slot in _SLOT_PROMPTS]
        if not prompts:
            return "Could you provide a few more details about your trip?"
        if len(prompts) == 1:
            joined = prompts[0]
        else:
            joined = ", ".join(prompts[:-1]) + " and " + prompts[-1]
        return f"Could you tell me {joined}?"

    @staticmethod
    def _build_steps(session: TravelSession) -> list[ExecutionStep]:
        """Every required slot is filled at this point, so flight and
        hotel searches can both be planned. TODO: make hotel/car-rental
        steps conditional on detected intent once the planner tracks it.
        """
        return [
            ExecutionStep(
                tool_name=ToolName.FLIGHT_SEARCH,
                arguments={
                    "origin": session.origin,
                    "destination": session.destination,
                    "departure_date": session.departure_date,
                    "return_date": session.return_date,
                    "travelers": session.passengers,
                },
                priority=1,
            ),
            ExecutionStep(
                tool_name=ToolName.HOTEL_SEARCH,
                arguments={
                    "destination": session.destination,
                    "check_in_date": session.departure_date,
                    "check_out_date": session.return_date,
                    "guests": session.passengers,
                },
                priority=2,
            ),
        ]
