"""Fallback Manager.

Decides what the agent does when something in the pipeline can't proceed
normally: a tool failed, validation rejected the results, or the planner
could not produce a usable plan. Centralizing this avoids ad-hoc error
handling scattered across the orchestrator.
"""

from abc import ABC, abstractmethod

from app.schemas.validation import ValidationResult


class FallbackManager(ABC):
    @abstractmethod
    def handle_validation_failure(self, validation: ValidationResult) -> str:
        """Return a user-facing message when validation rejects tool results."""

    @abstractmethod
    def handle_planning_failure(self, error: Exception) -> str:
        """Return a user-facing message when the planner raises."""

    @abstractmethod
    def handle_execution_failure(self, error: Exception) -> str:
        """Return a user-facing message when tool execution raises unexpectedly."""


class DefaultFallbackManager(FallbackManager):
    """Placeholder fallback strategy — generic apologetic messages.

    TODO: differentiate by failure type (retry with adjusted params,
    suggest alternative dates/destinations, escalate to a human agent,
    etc.) instead of returning a single generic message per category.
    """

    def handle_validation_failure(self, validation: ValidationResult) -> str:
        return (
            "I couldn't confirm valid options for your request. "
            "Could you double-check the details and try again?"
        )

    def handle_planning_failure(self, error: Exception) -> str:
        return "I'm having trouble understanding that request right now. Could you rephrase it?"

    def handle_execution_failure(self, error: Exception) -> str:
        return "Something went wrong while looking that up. Please try again in a moment."
