"""FastAPI dependency providers.

Wires concrete implementations into the abstract interfaces used by
app/agent/*. Swapping an implementation (e.g. InMemorySessionStore ->
RedisSessionStore, or the LLM provider behind the Planner) happens here
and nowhere else.
"""

from functools import lru_cache

from app.agent.conversation_manager import ConversationManager
from app.agent.extraction import LLMSlotExtractor, SlotExtractor
from app.agent.fallback_manager import DefaultFallbackManager, FallbackManager
from app.agent.itinerary_builder import DefaultItineraryBuilder, ItineraryBuilder
from app.agent.orchestrator import TravelAgentOrchestrator
from app.agent.planner import LLMPlanner, Planner
from app.agent.tool_executor import ToolExecutor
from app.agent.validator import PassThroughValidator, Validator
from app.config import get_settings
from app.llm.base import LLMClient
from app.llm.factory import build_llm_client
from app.session.store import InMemorySessionStore, SessionStore
from app.tools.registry import ToolRegistry, build_default_registry


@lru_cache
def get_session_store() -> SessionStore:
    return InMemorySessionStore()


@lru_cache
def get_conversation_manager() -> ConversationManager:
    return ConversationManager(session_store=get_session_store())


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return build_default_registry()


@lru_cache
def get_llm_client() -> LLMClient:
    return build_llm_client(get_settings())


@lru_cache
def get_slot_extractor() -> SlotExtractor:
    return LLMSlotExtractor(llm_client=get_llm_client())


@lru_cache
def get_planner() -> Planner:
    return LLMPlanner(
        conversation_manager=get_conversation_manager(), extractor=get_slot_extractor()
    )


@lru_cache
def get_tool_executor() -> ToolExecutor:
    return ToolExecutor(registry=get_tool_registry())


@lru_cache
def get_validator() -> Validator:
    return PassThroughValidator()


@lru_cache
def get_fallback_manager() -> FallbackManager:
    return DefaultFallbackManager()


@lru_cache
def get_itinerary_builder() -> ItineraryBuilder:
    return DefaultItineraryBuilder()


@lru_cache
def get_orchestrator() -> TravelAgentOrchestrator:
    return TravelAgentOrchestrator(
        conversation_manager=get_conversation_manager(),
        planner=get_planner(),
        tool_executor=get_tool_executor(),
        validator=get_validator(),
        fallback_manager=get_fallback_manager(),
        itinerary_builder=get_itinerary_builder(),
    )
