"""Application configuration.

Central place for environment-driven settings. Real travel API credentials
(flight/hotel/car providers) should be added here as they are integrated —
keep them optional so the app still boots in mock mode without them.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Travel Booking Agent"
    app_env: str = "development"
    api_prefix: str = "/api/v1"

    # When True, tool implementations return mock data instead of calling
    # real travel provider APIs. Flip per-environment once real providers
    # (flights/hotels/cars) are wired up in app/tools/.
    mock_mode: bool = True

    # Placeholder credentials for future real provider integrations.
    flight_provider_api_key: str | None = None
    hotel_provider_api_key: str | None = None
    car_rental_provider_api_key: str | None = None

    # Which LLMClient app/llm/factory.py builds. "mock" (default) needs no
    # credentials and runs fully offline — good for local dev/tests.
    # Add a new provider by registering it in app/llm/factory.py, not by
    # adding branches anywhere that consumes LLMClient.
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    # Override to point an OpenAI-compatible client at a different host,
    # e.g. a local Ollama server — only used by providers that support it.
    llm_base_url: str | None = None

    # FallbackManager retry policy for transient tool failures. Bounded —
    # fallback_max_retries=0 disables retries without disabling fallback
    # (unresolved tools are still reported, just never retried).
    fallback_max_retries: int = 2
    fallback_retry_delay_ms: int = 250

    cors_allow_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
