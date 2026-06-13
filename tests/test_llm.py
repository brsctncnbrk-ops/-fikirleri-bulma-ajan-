"""Tests for the LLM wrapper: extraction, JSON parsing, token tracking (TASK-009)."""

from types import SimpleNamespace

import pytest

from trendidea.config import Settings
from trendidea.llm import LLMClient, LLMError, extract_json


def _settings():
    return Settings(_env_file=None)


class FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeResponse:
    def __init__(self, text, input_tokens=10, output_tokens=20):
        self.content = [FakeBlock(text)]
        self.usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens)


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_with_fence_and_prose():
    text = 'İşte sonuç:\n```json\n{"x": [1,2]}\n```\nteşekkürler'
    assert extract_json(text) == {"x": [1, 2]}


def test_extract_json_invalid_raises():
    with pytest.raises(LLMError):
        extract_json("not json at all")


def test_complete_extracts_text_and_tracks_tokens():
    client = FakeClient([FakeResponse("hello", input_tokens=5, output_tokens=7)])
    llm = LLMClient(_settings(), client=client)
    out = llm.complete("sys", "user")
    assert out == "hello"
    assert llm.cost.input_tokens == 5
    assert llm.cost.output_tokens == 7
    assert llm.cost.calls == 1


def test_web_search_flag_adds_tool():
    client = FakeClient([FakeResponse("done")])
    llm = LLMClient(_settings(), client=client)
    llm.complete("sys", "find competitors", use_web_search=True, max_searches=3)
    sent = client.messages.calls[0]
    assert sent["tools"][0]["type"] == "web_search_20250305"
    assert sent["tools"][0]["max_uses"] == 3


def test_complete_json_retries_then_parses():
    client = FakeClient([FakeResponse("garbage"), FakeResponse('{"ok": true}')])
    llm = LLMClient(_settings(), client=client)
    result = llm.complete_json("sys", "give json", retries=1)
    assert result == {"ok": True}
    assert len(client.messages.calls) == 2  # retried once


def test_complete_json_raises_after_retries():
    client = FakeClient([FakeResponse("nope"), FakeResponse("still nope")])
    llm = LLMClient(_settings(), client=client)
    with pytest.raises(LLMError):
        llm.complete_json("sys", "give json", retries=1)
