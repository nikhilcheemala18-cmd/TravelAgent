import unittest

from app.agent.conversation_manager import ConversationManager
from app.agent.planner import LLMPlanner
from app.schemas.agent import ClarificationAction, ExecutionPlan
from app.schemas.conversation import ChatRequest, PendingCityConfirmation
from app.schemas.travel_session import TravelSession
from app.session.store import InMemorySessionStore
from app.api.deps import (
    get_conversation_manager,
    get_fallback_manager,
    get_itinerary_builder,
    get_response_builder,
    get_tool_executor,
    get_validator,
)
from app.agent.orchestrator import TravelAgentOrchestrator


class StaticExtractor:
    def __init__(self, updates: dict) -> None:
        self._updates = updates

    def extract(self, message: str, session: TravelSession) -> dict:
        return self._updates


def build_planner(updates: dict) -> LLMPlanner:
    return LLMPlanner(
        ConversationManager(InMemorySessionStore()),
        extractor=StaticExtractor(updates),
    )


class CityResolutionTests(unittest.TestCase):
    def test_bangalore_alias_becomes_bengaluru(self) -> None:
        planner = build_planner(
            {
                "origin": "Hyderabad",
                "destination": "Bangalore",
                "departure_date": "2026-11-20",
                "passengers": 2,
            }
        )

        plan = planner.create_plan("unused", TravelSession())

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.session.destination, "Bengaluru")

    def test_bombay_alias_becomes_mumbai(self) -> None:
        planner = build_planner(
            {
                "origin": "Delhi",
                "destination": "Bombay",
                "departure_date": "2026-11-20",
                "passengers": 2,
            }
        )

        plan = planner.create_plan("unused", TravelSession())

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.session.destination, "Mumbai")

    def test_exact_canonical_city_is_preserved(self) -> None:
        planner = build_planner(
            {
                "origin": "Hyderabad",
                "destination": "Bengaluru",
                "departure_date": "2026-11-20",
                "passengers": 2,
            }
        )

        plan = planner.create_plan("unused", TravelSession())

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.session.destination, "Bengaluru")

    def test_common_typo_prompts_for_confirmation(self) -> None:
        planner = build_planner({"destination": "Bangaluru"})

        decision = planner.create_plan("unused", TravelSession(origin="Hyderabad"))

        self.assertIsInstance(decision, ClarificationAction)
        self.assertEqual(decision.pending_city_confirmation.field, "destination")
        self.assertEqual(decision.pending_city_confirmation.raw_value, "Bangaluru")
        self.assertEqual(decision.pending_city_confirmation.suggested_value, "Bengaluru")
        self.assertIn("Did you mean Bengaluru (Bangalore)?", decision.question)

    def test_confirmation_accept_applies_canonical_value(self) -> None:
        store = InMemorySessionStore()
        manager = ConversationManager(store)
        orchestrator = TravelAgentOrchestrator(
            conversation_manager=manager,
            planner=LLMPlanner(
                manager,
                StaticExtractor(
                    {
                        "origin": "Hyderabad",
                        "destination": "Bangaluru",
                        "departure_date": "2026-11-20",
                        "passengers": 2,
                    }
                ),
            ),
            tool_executor=get_tool_executor(),
            validator=get_validator(),
            fallback_manager=get_fallback_manager(),
            itinerary_builder=get_itinerary_builder(),
            response_builder=get_response_builder(),
        )

        first = orchestrator.handle_message(
            ChatRequest(
                message="I want to travel from Hyderabad to Bangaluru on 2026-11-20 for 2 passengers"
            )
        )
        second = orchestrator.handle_message(
            ChatRequest(session_id=first.session_id, message="yes")
        )

        self.assertTrue(first.requires_clarification)
        self.assertTrue(second.success)
        self.assertEqual(second.itinerary.traveler_information.destination, "Bengaluru")

    def test_confirmation_reject_asks_for_intended_city(self) -> None:
        planner = build_planner({})
        pending = PendingCityConfirmation(
            field="destination", raw_value="Bangaluru", suggested_value="Bengaluru"
        )

        decision = planner.create_plan(
            "no",
            TravelSession(origin="Hyderabad"),
            pending,
        )

        self.assertIsInstance(decision, ClarificationAction)
        self.assertIsNone(decision.pending_city_confirmation)
        self.assertIn("Which destination city did you mean?", decision.question)

    def test_unknown_city_gets_graceful_clarification(self) -> None:
        planner = build_planner({"destination": "Atlantis"})

        decision = planner.create_plan("unused", TravelSession(origin="Hyderabad"))

        self.assertIsInstance(decision, ClarificationAction)
        self.assertIsNone(decision.pending_city_confirmation)
        self.assertIn("I couldn't match 'Atlantis'", decision.question)


if __name__ == "__main__":
    unittest.main()
