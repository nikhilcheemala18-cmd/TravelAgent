"""Builds the configured LLMClient.

The single place in the codebase that decides *which* LLM provider to
use, based on Settings.llm_provider (env var LLM_PROVIDER). Everything
that consumes an LLMClient — currently only app/agent/extraction.py — is
built against the LLMClient interface and never sees this decision.

Adding a new provider means adding a module under app/llm/providers/ and
registering it in _PROVIDER_FACTORIES below; no caller changes.
"""

from collections.abc import Callable

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.providers.mock_client import MockLLMClient
from app.llm.providers.openai_client import OpenAILLMClient


def _build_mock(settings: Settings) -> LLMClient:
    return MockLLMClient()


def _build_openai(settings: Settings) -> LLMClient:
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is required when LLM_PROVIDER=openai.")
    return OpenAILLMClient(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
    )


_PROVIDER_FACTORIES: dict[str, Callable[[Settings], LLMClient]] = {
    "mock": _build_mock,
    "openai": _build_openai,
}


def build_llm_client(settings: Settings) -> LLMClient:
    provider = settings.llm_provider.strip().lower()
    try:
        factory = _PROVIDER_FACTORIES[provider]
    except KeyError:
        supported = ", ".join(sorted(_PROVIDER_FACTORIES))
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Supported: {supported}."
        ) from None
    return factory(settings)
