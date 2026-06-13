"""Tests for Telegram command routing (TASK-013)."""

from trendidea.telegram.handlers import HELP_TEXT, CommandRouter


def _router(**over):
    defaults = dict(
        get_today_report=lambda: "RAPOR",
        trigger_scan=lambda: "TARAMA BAŞLADI",
        get_sources_status=lambda: "KAYNAKLAR",
        deepen_idea=lambda n: f"FIKIR-{n}",
        answer_freeform=lambda q, cid: f"CEVAP:{q}",
    )
    defaults.update(over)
    return CommandRouter(**defaults)


def test_routes_commands():
    r = _router()
    assert r.handle("1", "/bugun") == "RAPOR"
    assert r.handle("1", "/tara") == "TARAMA BAŞLADI"
    assert r.handle("1", "/kaynaklar") == "KAYNAKLAR"
    assert r.handle("1", "/fikir 3") == "FIKIR-3"


def test_help_and_unknown():
    r = _router()
    assert r.handle("1", "/start") == HELP_TEXT
    assert r.handle("1", "") == HELP_TEXT
    assert "Bilinmeyen komut" in r.handle("1", "/nope")


def test_fikir_requires_number():
    r = _router()
    assert "Kullanım" in r.handle("1", "/fikir")
    assert "Kullanım" in r.handle("1", "/fikir abc")


def test_freeform_goes_to_answer():
    r = _router()
    assert r.handle("1", "fatura nasıl?") == "CEVAP:fatura nasıl?"


def test_authorization_allowlist():
    r = _router(allowed_chat_id="42")
    assert r.handle("42", "/bugun") == "RAPOR"
    assert "yetkili" in r.handle("99", "/bugun")


def test_empty_allowlist_allows_all():
    r = _router(allowed_chat_id="")
    assert r.handle("anychat", "/bugun") == "RAPOR"
