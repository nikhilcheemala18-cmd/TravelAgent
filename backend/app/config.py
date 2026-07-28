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

    cors_allow_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
