"""Tests for the Idea Generator (TASK-010)."""

import json

from tests.test_llm import FakeClient, FakeResponse
from trendidea.agents.idea_generator import IdeaGenerator
from trendidea.config import Settings
from trendidea.llm import LLMClient
from trendidea.models import Cluster, IdeaStatus, Signal


def _llm(payload):
    client = FakeClient([FakeResponse(json.dumps(payload, ensure_ascii=False))])
    return LLMClient(Settings(_env_file=None), client=client)


def _cluster():
    return Cluster(
        label="invoicing, freelancers",
        score=0.8,
        signals=[
            Signal(source="hn", url="http://a", title="Invoicing pain"),
            Signal(source="reddit", url="http://b", title="Need invoicing tool"),
        ],
    )


def test_generate_parses_ideas():
    payload = [
        {
            "title": "Freelancer fatura asistanı",
            "target_customer": "Serbest çalışanlar",
            "pain": "Fatura takibi zor",
            "revenue_model": "abonelik",
            "first_revenue_estimate": "2-4 hafta",
            "mvp_scope": "Fatura oluştur + hatırlatma",
            "dev_time": "1 hafta",
            "competitors": [{"name": "Acme", "url": "http://acme"}],
            "main_risk": "Pazar doygunluğu",
            "signal_refs": ["http://a", "http://b"],
        }
    ]
    ideas = IdeaGenerator(_llm(payload)).generate([_cluster()])
    assert len(ideas) == 1
    idea = ideas[0]
    assert idea.title == "Freelancer fatura asistanı"
    assert idea.status == IdeaStatus.CANDIDATE
    assert idea.signal_refs == ["http://a", "http://b"]
    assert idea.competitors[0].name == "Acme"


def test_generate_skips_items_without_title():
    payload = [{"title": ""}, {"pain": "x"}]
    ideas = IdeaGenerator(_llm(payload)).generate([_cluster()])
    assert ideas == []


def test_generate_empty_when_no_clusters():
    ideas = IdeaGenerator(_llm([])).generate([])
    assert ideas == []


def test_generate_handles_object_wrapper():
    payload = {"ideas": [{"title": "X", "revenue_model": "tek seferlik"}]}
    ideas = IdeaGenerator(_llm(payload)).generate([_cluster()])
    assert len(ideas) == 1
    assert ideas[0].revenue_model == "tek seferlik"
    assert ideas[0].target_customer == "TBD"  # missing field defaults to TBD
