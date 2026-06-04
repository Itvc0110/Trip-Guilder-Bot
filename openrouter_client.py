from __future__ import annotations

import json
from typing import Any

import requests

from config import Settings


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter cannot return a usable response."""


class OpenRouterClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        response_format: dict[str, str] | None = None,
    ) -> str:
        if not self.settings.has_api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is missing. Add it to .env before calling the real model."
            )

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        response = requests.post(
            self.settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.settings.app_referer,
                "X-OpenRouter-Title": self.settings.app_title,
            },
            data=json.dumps(payload),
            timeout=60,
        )

        if response.status_code >= 400:
            raise OpenRouterError(
                f"OpenRouter returned HTTP {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(f"Unexpected OpenRouter response shape: {data}") from exc
