"""Anthropic Claude wrapper: completions, JSON helper, and server-side web search.

The wrapper is dependency-injectable (a fake client can be passed in tests), so
no live API key is needed to exercise the surrounding logic.
"""

from __future__ import annotations

import json
import logging
import re

from trendidea.config import Settings
from trendidea.logging_conf import CostTracker

logger = logging.getLogger(__name__)

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search"}

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class LLMError(RuntimeError):
    """Raised when the model output cannot be used (e.g. unparseable JSON)."""


def extract_json(text: str):
    """Pull a JSON object/array out of model text (tolerates code fences/prose)."""
    fenced = _JSON_FENCE_RE.search(text)
    candidate = fenced.group(1).strip() if fenced else text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    # fall back to the first {...} or [...] span
    for opener, closer in (("{", "}"), ("[", "]")):
        start = candidate.find(opener)
        end = candidate.rfind(closer)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise LLMError("Model output is not valid JSON")


class LLMClient:
    def __init__(
        self,
        settings: Settings,
        cost_tracker: CostTracker | None = None,
        client=None,
    ) -> None:
        self.settings = settings
        self.cost = cost_tracker or CostTracker()
        self._client = client

    @property
    def client(self):
        if self._client is None:
            import anthropic  # imported lazily so tests/dry-run need no SDK key

            self._client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        return self._client

    def complete(
        self,
        system: str,
        user: str,
        model: str | None = None,
        max_tokens: int = 1500,
        use_web_search: bool = False,
        max_searches: int = 5,
    ) -> str:
        model = model or self.settings.llm_model_reasoning
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if use_web_search:
            kwargs["tools"] = [{**WEB_SEARCH_TOOL, "max_uses": max_searches}]

        response = self.client.messages.create(**kwargs)
        self._track(model, response)
        return self._extract_text(response)

    def complete_json(self, system: str, user: str, retries: int = 1, **kwargs):
        """Like complete() but returns parsed JSON, retrying once on parse failure."""
        last_error: Exception | None = None
        prompt = user
        for attempt in range(retries + 1):
            text = self.complete(system, prompt, **kwargs)
            try:
                return extract_json(text)
            except LLMError as exc:
                last_error = exc
                logger.warning("llm json parse failed", extra={"attempt": attempt})
                prompt = user + "\n\nYANIT YALNIZCA geçerli JSON olmalı, başka metin ekleme."
        raise last_error  # type: ignore[misc]

    # --- internals --------------------------------------------------------
    def _track(self, model: str, response) -> None:
        usage = getattr(response, "usage", None)
        if usage is not None:
            self.cost.add(
                model,
                int(getattr(usage, "input_tokens", 0) or 0),
                int(getattr(usage, "output_tokens", 0) or 0),
            )

    @staticmethod
    def _extract_text(response) -> str:
        parts: list[str] = []
        for block in getattr(response, "content", []) or []:
            block_type = getattr(block, "type", None) or (
                block.get("type") if isinstance(block, dict) else None
            )
            if block_type == "text":
                text = getattr(block, "text", None)
                if text is None and isinstance(block, dict):
                    text = block.get("text", "")
                parts.append(text or "")
        return "\n".join(p for p in parts if p).strip()
