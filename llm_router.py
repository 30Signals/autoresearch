"""
llm_router.py — Reusable Free LLM Router

Rotates across multiple provider/model slots, tracks per-slot cooldowns,
and waits when all slots are rate-limited.

Config path resolution (in order):
1. Explicit path passed to constructor
2. ~/.llm_router_config.json
3. ./llm_router_config.json
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

import litellm
from litellm.exceptions import (
    RateLimitError,
    ServiceUnavailableError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    ContextWindowExceededError,
)

logger = logging.getLogger(__name__)

# Suppress litellm's verbose logging
litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class LLMRouter:
    """
    Routes LLM calls across multiple provider/model slots with:
    - Round-robin rotation
    - Per-slot cooldown tracking
    - Automatic retry with backoff
    - Permanent slot disabling on auth errors
    """

    def __init__(self, config_path=None):
        self._config = self._load_config(config_path)
        self._slots = self._expand_slots(self._config["providers"])
        self._slot_index = 0
        self._cooldown_until: dict[str, datetime] = {}
        self._disabled: set[str] = set()

        if not self._slots:
            raise ValueError("No provider slots found in config. Check your llm_router_config.json.")

        logger.info(f"LLMRouter initialized with {len(self._slots)} slots")

    def _load_config(self, config_path) -> dict:
        candidates = []
        if config_path:
            candidates.append(Path(config_path))
        candidates.append(Path.home() / ".llm_router_config.json")
        candidates.append(Path("llm_router_config.json"))

        for path in candidates:
            if path.exists():
                logger.info(f"Loading LLM router config from: {path}")
                with open(path) as f:
                    return json.load(f)

        raise FileNotFoundError(
            "No llm_router_config.json found. Checked:\n"
            + "\n".join(f"  {p}" for p in candidates)
            + "\n\nCopy llm_router_config.json.example to ~/.llm_router_config.json and fill in your API keys."
        )

    def _expand_slots(self, providers: list) -> list:
        """Expand each provider × model into a flat slot list."""
        slots = []
        for provider in providers:
            for model in provider["models"]:
                slot = {
                    "name": f"{provider['name']}::{model}",
                    "type": provider["type"],
                    "api_key": provider["api_key"],
                    "model": model,
                }
                slots.append(slot)
        return slots

    def _slot_key(self, slot: dict) -> str:
        return slot["name"]

    def _is_available(self, slot: dict) -> bool:
        key = self._slot_key(slot)
        if key in self._disabled:
            return False
        cooldown = self._cooldown_until.get(key)
        if cooldown and datetime.now() < cooldown:
            return False
        return True

    def _next_available_slot(self) -> dict | None:
        """
        Find the next available slot using round-robin.
        Returns None if all slots are disabled.
        Returns the slot and updates the index.
        """
        n = len(self._slots)
        for _ in range(n):
            slot = self._slots[self._slot_index % n]
            self._slot_index = (self._slot_index + 1) % n
            if self._is_available(slot):
                return slot
        return None

    def _wait_for_slot(self) -> dict:
        """Wait until at least one slot becomes available, then return it."""
        while True:
            slot = self._next_available_slot()
            if slot:
                return slot

            # All slots cooling down — find soonest expiry
            active_cooldowns = [
                cd for key, cd in self._cooldown_until.items()
                if key not in self._disabled and datetime.now() < cd
            ]
            if not active_cooldowns:
                # All slots permanently disabled
                raise RuntimeError("All LLM slots are permanently disabled (auth errors). Check your API keys.")

            soonest = min(active_cooldowns)
            wait_secs = (soonest - datetime.now()).total_seconds() + 0.5
            print(f"  [router] All slots cooling down. Waiting {wait_secs:.1f}s...")
            time.sleep(max(0.5, wait_secs))

    def _set_cooldown(self, slot: dict, seconds: int):
        key = self._slot_key(slot)
        self._cooldown_until[key] = datetime.now() + timedelta(seconds=seconds)
        logger.warning(f"Slot {key} on cooldown for {seconds}s")

    def _disable_slot(self, slot: dict, reason: str):
        key = self._slot_key(slot)
        self._disabled.add(key)
        logger.error(f"Slot {key} permanently disabled: {reason}")
        print(f"  [router] Slot {slot['name']} disabled: {reason}")

    def _build_litellm_kwargs(self, slot: dict, **extra) -> tuple[str, dict]:
        """Return (model_string, kwargs_dict) for litellm call."""
        kwargs = dict(extra)
        provider_type = slot["type"]

        if provider_type == "openrouter":
            model_str = f"openrouter/{slot['model']}"
            kwargs["api_base"] = "https://openrouter.ai/api/v1"
            kwargs["api_key"] = slot["api_key"]
        elif provider_type == "google":
            model_str = slot["model"]  # already "gemini/gemini-2.0-flash-exp"
            kwargs["api_key"] = slot["api_key"]
        elif provider_type == "groq":
            model_str = slot["model"]  # already "groq/llama-3.3-70b-versatile"
            kwargs["api_key"] = slot["api_key"]
        else:
            # Generic fallback
            model_str = slot["model"]
            kwargs["api_key"] = slot["api_key"]

        return model_str, kwargs

    def _call_with_retry(self, build_kwargs_fn) -> object:
        """
        Core retry loop. build_kwargs_fn(slot) → (model_str, call_kwargs).
        Raises BadRequestError / ContextWindowExceededError to caller.
        """
        max_attempts = len(self._slots) * 3 + 5
        for attempt in range(max_attempts):
            slot = self._wait_for_slot()
            model_str, kwargs = build_kwargs_fn(slot)

            try:
                logger.debug(f"Calling {model_str} (slot: {slot['name']})")
                response = litellm.completion(model=model_str, **kwargs)
                return response

            except RateLimitError as e:
                print(f"  [router] Rate limit on {slot['name']} — cooldown 60s")
                self._set_cooldown(slot, 60)

            except ServiceUnavailableError as e:
                print(f"  [router] Service unavailable on {slot['name']} — cooldown 30s")
                self._set_cooldown(slot, 30)

            except APIConnectionError as e:
                print(f"  [router] Connection error on {slot['name']} — cooldown 10s")
                self._set_cooldown(slot, 10)

            except AuthenticationError as e:
                self._disable_slot(slot, f"AuthenticationError: {e}")

            except ContextWindowExceededError:
                # Propagate — harness handles trimming
                raise

            except BadRequestError as e:
                err_str = str(e).lower()
                # Decommissioned / unsupported models should disable the slot permanently
                if any(kw in err_str for kw in ("decommissioned", "not supported", "deprecated", "no longer")):
                    self._disable_slot(slot, f"Model decommissioned: {e}")
                else:
                    # Other bad requests (e.g. invalid params) — propagate
                    raise

            except Exception as e:
                print(f"  [router] Unexpected error on {slot['name']}: {type(e).__name__}: {e} — cooldown 10s")
                self._set_cooldown(slot, 10)

        raise RuntimeError(f"All retry attempts exhausted after {max_attempts} tries.")

    def chat_with_tools(self, messages: list, tools: list, tool_choice="auto", max_tokens=4096) -> object:
        """
        Call the LLM with tool/function calling support.
        Returns the raw litellm response.
        """
        def build_kwargs(slot):
            model_str, kwargs = self._build_litellm_kwargs(slot)
            kwargs["messages"] = messages
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
            kwargs["max_tokens"] = max_tokens
            return model_str, kwargs

        return self._call_with_retry(build_kwargs)

    def chat(self, messages: list, max_tokens=4096) -> object:
        """
        Simple chat call without tools.
        Returns the raw litellm response.
        """
        def build_kwargs(slot):
            model_str, kwargs = self._build_litellm_kwargs(slot)
            kwargs["messages"] = messages
            kwargs["max_tokens"] = max_tokens
            return model_str, kwargs

        return self._call_with_retry(build_kwargs)
