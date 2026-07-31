"""Business-rule validation for a merged TravelSession.

Distinct from app/agent/validator.py's Validator, which verifies tool
*results* after execution — this checks the *inputs* the Planner is about
to act on, before any tool ever runs (return date before departure,
negative passenger count, an impossible budget, an out-of-range hotel
rating). Kept separate from ConversationManager (which only merges and
reports state, never judges it) and out of Planner's own body so the
rules themselves stay in one small, easily extended place, independent of
any tool/provider.
"""

from dataclasses import dataclass
from datetime import date

from app.schemas.travel_session import TravelSession


@dataclass(frozen=True)
class SessionRuleViolation:
    field: str
    message: str


def validate_session(session: TravelSession) -> list[SessionRuleViolation]:
    """Return a conversational explanation for anything in `session` that
    doesn't make sense given what's filled in so far. Empty if consistent.

    Only checks fields that are actually set — an unset optional field is
    never a violation (that's ConversationManager's missing-slots concern,
    not this module's).
    """
    violations: list[SessionRuleViolation] = []

    if session.departure_date and session.return_date:
        departure = _try_parse_date(session.departure_date)
        return_ = _try_parse_date(session.return_date)
        if departure and return_ and return_ < departure:
            violations.append(
                SessionRuleViolation(
                    field="return_date",
                    message=(
                        "Your return date is before your departure date — "
                        "could you double-check that?"
                    ),
                )
            )

    if session.passengers is not None and session.passengers <= 0:
        violations.append(
            SessionRuleViolation(
                field="passengers",
                message="I need at least 1 passenger — how many people will be travelling?",
            )
        )

    if session.budget is not None and session.budget <= 0:
        violations.append(
            SessionRuleViolation(
                field="budget",
                message="That budget doesn't look right — could you give me a valid amount?",
            )
        )

    if session.hotel_rating is not None and not (1 <= session.hotel_rating <= 5):
        violations.append(
            SessionRuleViolation(
                field="hotel_rating",
                message="Hotel star ratings run from 1 to 5 — which would you prefer?",
            )
        )

    return violations


def _try_parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
