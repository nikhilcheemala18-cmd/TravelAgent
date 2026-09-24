import json
import unittest

from app.agent.conversation_manager import ConversationManager
from app.agent.planner import LLMPlanner
from app.agent.prompts.extraction import build_extraction_user_prompt
from app.llm.providers.mock_client import MockLLMClient
from app.schemas.agent import ExecutionPlan
from app.schemas.travel_session import TravelSession
from app.session.store import InMemorySessionStore


REFERENCE_DATE = "2026-09-05"


def extract(message: str, session: TravelSession | None = None) -> dict:
    prompt = build_extraction_user_prompt(
        message=message,
        session=session or TravelSession(),
        reference_date=REFERENCE_DATE,
    )
    return json.loads(MockLLMClient().complete(system_prompt="", user_prompt=prompt))


class MockExtractionCorrectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = TravelSession(
            origin="Delhi",
            destination="Paris",
            departure_date="2026-11-20",
            passengers=2,
            budget=2000,
            hotel_rating=4,
        )

    def test_destination_correction_with_explicit_destination(self) -> None:
        self.assertEqual(
            extract("Change destination to Tokyo", self.session),
            {"destination": "Tokyo"},
        )

    def test_natural_destination_correction(self) -> None:
        self.assertEqual(
            extract("I want to go to Tokyo instead", self.session),
            {"destination": "Tokyo"},
        )

    def test_destination_correction_preserves_existing_fields_in_planner(self) -> None:
        planner = LLMPlanner(
            ConversationManager(InMemorySessionStore()),
            extractor=type(
                "Extractor",
                (),
                {"extract": lambda _, message, session: extract(message, session)},
            )(),
        )

        plan = planner.create_plan("Change destination to Tokyo", self.session)

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.session.origin, "Delhi")
        self.assertEqual(plan.session.destination, "Tokyo")
        self.assertEqual(plan.session.departure_date, "2026-11-20")
        self.assertEqual(plan.session.passengers, 2)

    def test_explicit_return_date_correction(self) -> None:
        self.assertEqual(
            extract("Change my return date to 2026-11-28", self.session),
            {"return_date": "2026-11-28"},
        )

    def test_natural_return_date_wording(self) -> None:
        self.assertEqual(
            extract("I'll come back on 2026-11-28", self.session),
            {"return_date": "2026-11-28"},
        )

    def test_origin_only_follow_up(self) -> None:
        self.assertEqual(extract("From Delhi", self.session), {"origin": "Delhi"})

    def test_destination_only_follow_up(self) -> None:
        self.assertEqual(extract("To Paris", self.session), {"destination": "Paris"})

    def test_partial_update_followed_by_successful_planning(self) -> None:
        planner = LLMPlanner(
            ConversationManager(InMemorySessionStore()),
            extractor=type(
                "Extractor",
                (),
                {"extract": lambda _, message, session: extract(message, session)},
            )(),
        )
        partial = TravelSession(
            destination="Paris", departure_date="2026-11-20", passengers=2
        )

        plan = planner.create_plan("From Delhi", partial)

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(plan.session.origin, "Delhi")
        self.assertEqual(plan.session.destination, "Paris")
        self.assertEqual(plan.session.departure_date, "2026-11-20")
        self.assertEqual(plan.session.passengers, 2)

    def test_tomorrow_relative_date(self) -> None:
        self.assertEqual(
            extract("Plan from Delhi to Paris tomorrow for 2 passengers")[
                "departure_date"
            ],
            "2026-09-06",
        )

    def test_next_friday_relative_date(self) -> None:
        self.assertEqual(
            extract("Plan from Delhi to Paris next Friday for 2 passengers")[
                "departure_date"
            ],
            "2026-09-11",
        )


if __name__ == "__main__":
    unittest.main()
