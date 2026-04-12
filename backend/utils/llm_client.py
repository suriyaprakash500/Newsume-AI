"""Lazy singleton Groq client with retry + backoff."""
from __future__ import annotations

import asyncio
import json
import logging

from groq import Groq

from config.settings import settings

logger = logging.getLogger(__name__)

_client = None

MAX_RETRIES = 2
BACKOFF_BASE = 2.0


def get_client() -> Groq | None:
    global _client
    if not settings.groq_api_key:
        return None
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _generate_json_sync(prompt: str, model_name: str | None = None) -> dict | list | None:
    """Synchronous LLM call with retry. Runs in a thread to avoid blocking the event loop."""
    client = get_client()
    if client is None:
        return None

    name = model_name or settings.groq_model
    last_error = None

    # Groq needs a system message or explicit instructions to return JSON properly
    # sometimes just prompt works, but adding it helps.
    messages = [
        {
            "role": "user",
            "content": f"{prompt}\n\nPlease output ONLY valid JSON.",
        }
    ]

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=name,
                messages=messages,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content is None:
                return None
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning("Groq returned invalid JSON (attempt %d): %s", attempt + 1, e)
            last_error = e
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "429" in err_str or "500" in err_str or "503" in err_str:
                import time
                wait = BACKOFF_BASE ** (attempt + 1)
                logger.warning("Groq transient error (attempt %d), retrying in %ss: %s", attempt + 1, wait, e)
                time.sleep(wait)
            else:
                logger.warning("Groq non-retryable error: %s", e)
                break

    logger.error("Groq failed after %d attempts: %s", MAX_RETRIES + 1, last_error)
    return None


async def generate_json(prompt: str, model_name: str | None = None) -> dict | list | None:
    """Non-blocking wrapper \u2014 offloads the sync Groq call to a thread."""
    return await asyncio.to_thread(_generate_json_sync, prompt, model_name)


def validate_keys(data: dict | list | None, required: dict[str, type]) -> dict:
    """Ensure all required keys exist with correct types; fill defaults."""
    if not isinstance(data, dict):
        data = {}
    result = {}
    for key, expected_type in required.items():
        val = data.get(key)
        if val is not None and isinstance(val, expected_type):
            result[key] = val
        elif expected_type == str:
            result[key] = ""
        elif expected_type == list:
            result[key] = []
        elif expected_type == int:
            result[key] = 0
        elif expected_type == float:
            result[key] = 0.0
        else:
            result[key] = None
    return result
