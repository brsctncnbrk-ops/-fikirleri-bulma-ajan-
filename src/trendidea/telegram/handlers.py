"""Pure command-routing logic for the Telegram bot (framework-independent).

Routing is decoupled from python-telegram-bot so it can be unit-tested without a
running bot; bot.py adapts Telegram updates onto CommandRouter.handle().
"""

from __future__ import annotations

from collections.abc import Callable

HELP_TEXT = (
    "Komutlar:\n"
    "/bugun — bugünün raporu\n"
    "/fikir <numara> — bir fikrin detayını derinleştir\n"
    "/tara — manuel anlık tarama tetikle\n"
    "/kaynaklar — taranan kaynakların durumu\n"
    "Serbest mesaj — günün raporu bağlamında soru-cevap"
)


class CommandRouter:
    def __init__(
        self,
        *,
        get_today_report: Callable[[], str],
        trigger_scan: Callable[[], str],
        get_sources_status: Callable[[], str],
        deepen_idea: Callable[[int], str],
        answer_freeform: Callable[[str, str], str],
        allowed_chat_id: str = "",
    ) -> None:
        self.get_today_report = get_today_report
        self.trigger_scan = trigger_scan
        self.get_sources_status = get_sources_status
        self.deepen_idea = deepen_idea
        self.answer_freeform = answer_freeform
        self.allowed_chat_id = str(allowed_chat_id or "")

    def authorized(self, chat_id: str) -> bool:
        # empty allowlist = allow all (development); otherwise must match
        return not self.allowed_chat_id or str(chat_id) == self.allowed_chat_id

    def handle(self, chat_id: str, text: str) -> str:
        if not self.authorized(chat_id):
            return "⛔ Bu bot yalnızca yetkili sohbetle çalışır."

        text = (text or "").strip()
        if not text:
            return HELP_TEXT

        if text.startswith(("/start", "/help")):
            return HELP_TEXT
        if text.startswith("/bugun"):
            return self.get_today_report()
        if text.startswith("/tara"):
            return self.trigger_scan()
        if text.startswith("/kaynaklar"):
            return self.get_sources_status()
        if text.startswith("/fikir"):
            return self._handle_fikir(text)
        if text.startswith("/"):
            return f"Bilinmeyen komut.\n\n{HELP_TEXT}"
        return self.answer_freeform(text, str(chat_id))

    def _handle_fikir(self, text: str) -> str:
        parts = text.split()
        if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
            return "Kullanım: /fikir <numara> (örn. /fikir 1)"
        return self.deepen_idea(int(parts[1]))
