from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_PLANNER_MODEL = "deepseek/deepseek-v4-flash"
DEFAULT_SUMMARY_MODEL = "deepseek/deepseek-v4-flash"


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    openrouter_base_url: str
    router_model: str
    planner_model: str
    reviewer_model: str
    summary_model: str
    conversation_window: int
    app_title: str = "DiChoiBot"
    app_referer: str = "http://localhost"

    @property
    def has_api_key(self) -> bool:
        return bool(self.openrouter_api_key and self.openrouter_api_key != "your_key_here")


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", DEFAULT_OPENROUTER_URL).strip(),
        router_model=os.getenv("ROUTER_MODEL", DEFAULT_MODEL).strip(),
        planner_model=os.getenv("PLANNER_MODEL", DEFAULT_PLANNER_MODEL).strip(),
        reviewer_model=os.getenv("REVIEWER_MODEL", DEFAULT_MODEL).strip(),
        summary_model=os.getenv("SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL).strip(),
        conversation_window=int(os.getenv("CONVERSATION_WINDOW", "7")),
        app_title=os.getenv("OPENROUTER_APP_TITLE", "DiChoiBot").strip(),
        app_referer=os.getenv("OPENROUTER_APP_REFERER", "http://localhost").strip(),
    )
