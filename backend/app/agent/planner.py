"""Agent Planner.

The "thinking" component of the agent: given the latest user message and
the current TravelSession, it decides whether enough is known to build an
ExecutionPlan, or whether the user still needs to be asked for more
details (ClarificationAction). This decision, not a fixed dialogue tree,
is what makes the system an agent.

Only origin, destination, departure date, and passenger count are ever
required to proceed — everything else (return date, budget, hotel
rating, ...) is an optional preference the traveler can add at any point
without ever blocking execution.

The Planner never touches a SessionStore, never calls a tool, never
validates tool output, and never builds an itinerary. It also never talks
to an LLM directly, and holds no provider-specific logic: extracting
values from the message is delegated to a SlotExtractor (which may or may
not be LLM-backed), merging those values into the session / judging
completeness is delegated to the ConversationManager, and checking that
the merged session is internally consistent (e.g. a return date can't be
before departure) is delegated to app/agent/session_rules.py. This class
stays focused on the planning decision itself.
"""

from abc import ABC, abstractmethod

from app.agent.conversation_manager import ConversationManager
from app.agent.extraction import SlotExtractor
from app.agent.session_rules import SessionRuleViolation, validate_session
from app.schemas.agent import ClarificationAction, ExecutionPlan, ExecutionStep
from app.schemas.common import ToolName
from app.schemas.travel_session import TravelSession

# Direct, conversational questions used when exactly one required slot is
# missing — matches how a human travel agent would ask, not a form field
# label. Never hints at a specific date format; the extractor understands
# natural language on the way back in.
_SLOT_QUESTIONS: dict[str, str] = {
    "origin": "Where will you be flying from?",
    "destination": "Where would you like to go?",
    "departure_date": "When are you planning to leave?",
    "passengers": "How many people will be travelling?",
}
# Noun-phrase form of the same questions, used to combine several missing
# slots into one flowing sentence ("Could you tell me X, Y and Z?").
_SLOT_PROMPTS: dict[str, str] = {
    "origin": "where you'll be flying from",
    "destination": "where you'd like to go",
    "departure_date": "when you're planning to leave",
    "passengers": "how many people will be travelling",
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

        # Fix anything nonsensical before asking for anything else — no
        # point requesting a passenger count while a return date that
        # predates departure sits uncorrected.
        violations = validate_session(updated_session)
        if violations:
            return ClarificationAction(
                session=updated_session,
                missing_slots=[violation.field for violation in violations],
                question=self._combine_violation_messages(violations),
            )

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
    def _combine_violation_messages(violations: list[SessionRuleViolation]) -> str:
        return " ".join(violation.message for violation in violations)

    @staticmethod
    def _build_clarification_question(missing_slots: list[str]) -> str:
        if len(missing_slots) == 1:
            slot = missing_slots[0]
            if slot in _SLOT_QUESTIONS:
                return _SLOT_QUESTIONS[slot]

        prompts = [_SLOT_PROMPTS[slot] for slot in missing_slots if slot in _SLOT_PROMPTS]
        if not prompts:
            return "Could you tell me a bit more about your trip?"
        if len(prompts) == 1:
            joined = prompts[0]
        else:
            joined = ", ".join(prompts[:-1]) + " and " + prompts[-1]
        return f"Could you tell me {joined}?"

    @staticmethod
    def _build_steps(session: TravelSession) -> list[ExecutionStep]:
        """Every required slot is filled at this point, so flight and
        hotel searches can both be planned; `return_date` may still be
        None (one-way / open-ended trip) — both tools accept that.
        `budget`/`hotel_rating`, when present, are passed through as
        search filters (max_price/min_rating) rather than applied after
        the fact, so a search that matches nothing comes back as a
        genuinely empty result the tool can explain, not a full list the
        rest of the agent has to second-guess.

        TODO: make hotel/car-rental steps conditional on detected intent
        once the planner tracks it.
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
                    "max_price": session.budget,
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
                    "min_rating": session.hotel_rating,
                },
                priority=2,
            ),
        ]
