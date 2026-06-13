"""Tests for the Validator/Gatekeeper eliminating logic (TASK-011)."""

import json

from tests.test_llm import FakeClient, FakeResponse
from trendidea.agents.validator import Validator
from trendidea.config import Settings
from trendidea.llm import LLMClient
from trendidea.models import Competitor, Idea, IdeaStatus


def _llm(*payloads):
    responses = [FakeResponse(json.dumps(p, ensure_ascii=False)) for p in payloads]
    return LLMClient(Settings(_env_file=None), client=FakeClient(responses))


def _idea(**over):
    base = dict(
        title="Test idea",
        signal_refs=["http://a", "http://b"],
        revenue_model="abonelik",
        competitors=[Competitor(name="Acme")],
    )
    base.update(over)
    return Idea(**base)


def test_reject_when_fewer_than_two_sources():
    # one source -> deterministic reject, LLM never called
    llm = _llm()  # no responses queued; calling LLM would raise IndexError
    out = Validator(llm).validate([_idea(signal_refs=["http://only-one"])])
    assert out == []


def test_reject_when_no_revenue_model():
    llm = _llm()
    out = Validator(llm).validate([_idea(revenue_model="TBD")])
    assert out == []


def test_pass_above_threshold():
    payload = {
        "verdict": "pass",
        "confidence": 80,
        "notes": "Sağlam fikir",
        "competitors": [{"name": "Acme", "url": "http://acme", "verified": True, "note": "var"}],
    }
    out = Validator(_llm(payload)).validate([_idea()])
    assert len(out) == 1
    assert out[0].status == IdeaStatus.PASSED
    assert out[0].confidence == 80
    assert out[0].competitors[0].verified is True


def test_reject_below_threshold_even_if_verdict_pass():
    payload = {"verdict": "pass", "confidence": 30, "notes": "zayıf"}
    out = Validator(_llm(payload), threshold=50).validate([_idea()])
    assert out == []


def test_reject_when_verdict_reject():
    payload = {"verdict": "reject", "confidence": 90, "notes": "rakip doğrulanamadı"}
    out = Validator(_llm(payload)).validate([_idea()])
    assert out == []


def test_passed_sorted_by_confidence():
    p1 = {"verdict": "pass", "confidence": 60, "notes": ""}
    p2 = {"verdict": "pass", "confidence": 90, "notes": ""}
    out = Validator(_llm(p1, p2)).validate([_idea(title="low"), _idea(title="high")])
    assert [i.title for i in out] == ["high", "low"]


def test_validation_fails_safe_on_llm_error():
    # empty FakeClient -> complete() raises IndexError -> idea rejected, no crash
    out = Validator(_llm()).validate([_idea()])
    assert out == []
