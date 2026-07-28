"""Agent Planner.

This is the "thinking" component: given the current conversation state and
the latest user message, decide the intent and which tool(s) to call with
which inputs (an AgentPlan). This is what makes the system an agent rather
than a scripted chatbot — the planner, not a fixed dialogue tree, decides
the next action.

The concrete implementation below is a placeholder. A real implementation
will typically call an LLM with function/tool-calling to produce the plan,
using ConversationState (history + slots) as context.
"""

from abc import ABC, abstractmethod

from app.schemas.agent import AgentPlan
from app.schemas.common import IntentType
from app.schemas.conversation import ConversationState


class AgentPlanner(ABC):
    @abstractmethod
    def create_plan(self, state: ConversationState, user_message: str) -> AgentPlan:
        """Produce a plan of tool calls (or a clarification request) for the
        given conversation state and latest user message."""


class PlaceholderAgentPlanner(AgentPlanner):
    """Static placeholder — always asks for clarification.

    TODO: replace with an LLM-backed planner that:
      1. classifies intent from `user_message` + `state.context`
      2. fills/validates required slots (origin, destination, dates, ...)
      3. emits PlannedAction(s) for the tools needed to satisfy the intent,
         or sets needs_clarification when required slots are missing.
    """

    def create_plan(self, state: ConversationState, user_message: str) -> AgentPlan:
        return AgentPlan(
            intent=IntentType.UNKNOWN,
            actions=[],
            needs_clarification=True,
            clarification_question=(
                "This is a placeholder planner response. Real intent "
                "classification and slot filling are not implemented yet."
            ),
        )
