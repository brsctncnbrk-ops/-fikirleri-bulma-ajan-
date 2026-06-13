"""Application configuration loaded from environment / .env (pydantic-settings).

Loading config never crashes on missing optional keys; instead helpers report
which capabilities are available so the pipeline can degrade gracefully.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Required for a full run (the system's brain + interface) ---
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")

    # --- Optional sources (skipped when missing) ---
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="trendidea/0.1", alias="REDDIT_USER_AGENT")
    producthunt_token: str = Field(default="", alias="PRODUCTHUNT_TOKEN")

    # --- Model settings ---
    llm_model_reasoning: str = Field(default="claude-sonnet-4-6", alias="LLM_MODEL_REASONING")
    llm_model_cheap: str = Field(default="claude-haiku-4-5", alias="LLM_MODEL_CHEAP")

    # --- Runtime settings ---
    daily_report_hour: int = Field(default=9, alias="DAILY_REPORT_HOUR")
    timezone: str = Field(default="Europe/Istanbul", alias="TIMEZONE")
    scan_window_hours: int = Field(default=72, alias="SCAN_WINDOW_HOURS")
    database_path: str = Field(default="trendidea.db", alias="DATABASE_PATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Capability checks -------------------------------------------------
    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_telegram(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def has_reddit(self) -> bool:
        return bool(self.reddit_client_id and self.reddit_client_secret)

    @property
    def has_producthunt(self) -> bool:
        return bool(self.producthunt_token)

    def missing_required(self) -> list[str]:
        """Return the names of required-but-missing settings for a full run."""
        missing: list[str] = []
        if not self.has_anthropic:
            missing.append("ANTHROPIC_API_KEY")
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.telegram_chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        return missing

    def enabled_sources(self) -> list[str]:
        """Sources that can run given the current keys (free sources always on)."""
        sources = ["hackernews", "github_trending", "google_trends", "rss"]
        if self.has_reddit:
            sources.append("reddit")
        if self.has_producthunt:
            sources.append("producthunt")
        return sources


_settings: Settings | None = None


def get_settings(reload: bool = False) -> Settings:
    """Return a cached Settings instance (reload=True rebuilds it)."""
    global _settings
    if _settings is None or reload:
        _settings = Settings()
    return _settings
