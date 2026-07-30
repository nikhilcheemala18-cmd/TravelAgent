"""Slot extraction for the Planner.

Turns free-form, natural-language user text — plus the trip details
already known — into TravelSession field updates. All natural-language
understanding (city names in any phrasing, spelled-out numbers,
approximate amounts, relative dates) is delegated to an injected
LLMClient; this module's own job is prompt assembly and turning the LLM's
response into data the Planner/ConversationManager can trust, not the
extraction itself.
"""

import json
from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from pydantic import ValidationError

from app.agent.prompts.extraction import EXTRACTION_SYSTEM_PROMPT, build_extraction_user_prompt
from app.llm.base import LLMClient
from app.schemas.travel_session import TravelSession
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SlotExtractionError(Exception):
    """Raised when the LLM's structured output can't be trusted.

    Covers non-JSON responses, non-object JSON, and values that fail
    TravelSession validation. Deliberately not caught anywhere in this
    module or in the Planner — corrupted extraction output must surface
    as a clear failure rather than silently produce a half-filled or
    wrong TravelSession.
    """


class SlotExtractor(ABC):
    @abstractmethod
    def extract(self, message: str, session: TravelSession) -> dict[str, Any]:
        """Return the TravelSession field values found in `message`.

        `session` is the trip state already collected, provided as context
        so the extractor can tell what's already known from what's new. A
        field not mentioned in `message` must come back either omitted or
        explicitly `None` — both mean "not mentioned"; callers (see
        ConversationManager.update_session) only ever apply non-`None`
        values, so a caller never needs to distinguish the two.
        """


class LLMExtractor(SlotExtractor):
    """Structured-extraction SlotExtractor backed by an LLMClient.

    Provider-agnostic: it depends only on the LLMClient interface, so
    switching between OpenAI / Gemini / Claude / Ollama / the offline mock
    is a Settings/DI change (see app/llm/factory.py, app/api/deps.py), not
    a code change here. This class never executes a tool, never builds an
    ExecutionPlan, never calls a travel API, and never touches
    ConversationState — it only turns a message into a validated dict of
    field updates for the Planner to act on.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    def extract(self, message: str, session: TravelSession) -> dict[str, Any]:
        raw_response = self._llm_client.complete(
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_prompt=build_extraction_user_prompt(
                message=message, session=session, reference_date=date.today().isoformat()
            ),
        )
        return self._parse_and_validate(raw_response, session)

    def _parse_and_validate(self, raw_response: str, session: TravelSession) -> dict[str, Any]:
        payload = self._strip_code_fence(raw_response)

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise SlotExtractionError(
                f"LLM extraction response was not valid JSON ({exc}). "
                f"Raw response: {raw_response!r}"
            ) from exc

        if not isinstance(data, dict):
            raise SlotExtractionError(
                "LLM extraction response must be a JSON object, got "
                f"{type(data).__name__}: {raw_response!r}"
            )

        known_fields = set(TravelSession.model_fields)
        unknown_keys = set(data) - known_fields
        if unknown_keys:
            logger.warning("Dropping unrecognized fields from LLM extraction: %s", unknown_keys)
        updates = {key: value for key, value in data.items() if key in known_fields}

        # Type-check the proposed updates against TravelSession before
        # handing them back — a value that doesn't fit the schema (e.g.
        # passengers: "two") must fail loudly, not get coerced or ignored.
        try:
            TravelSession.model_validate({**session.model_dump(), **updates})
        except ValidationError as exc:
            raise SlotExtractionError(
                f"LLM extraction response failed TravelSession validation: {exc}"
            ) from exc

        return updates

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        """Some models wrap JSON in ```/```json fences despite instructions
        not to; tolerate that without loosening the JSON parsing itself."""
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            if stripped.lower().startswith("json"):
                stripped = stripped[len("json") :]
        return stripped.strip()
