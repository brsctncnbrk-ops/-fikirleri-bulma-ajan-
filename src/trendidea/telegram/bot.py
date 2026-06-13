"""Thin python-telegram-bot adapter onto CommandRouter (runtime wiring)."""

from __future__ import annotations

import logging

from trendidea.telegram.handlers import CommandRouter

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, router: CommandRouter) -> None:
        self.token = token
        self.router = router
        self._app = None

    def build_application(self, post_init=None):
        """Construct the PTB Application with a single text handler.

        post_init: optional async callback run once after init (e.g. start scheduler).
        """
        from telegram.ext import Application, MessageHandler, filters

        builder = Application.builder().token(self.token)
        if post_init is not None:
            builder = builder.post_init(post_init)
        app = builder.build()

        async def on_message(update, context):
            message = update.message
            if message is None or not message.text:
                return
            chat_id = update.effective_chat.id
            reply = self.router.handle(chat_id, message.text)
            await message.reply_text(reply)

        app.add_handler(MessageHandler(filters.TEXT, on_message))
        self._app = app
        return app

    async def send_message(self, chat_id: str, text: str) -> None:
        """Push a message (used by the scheduler to deliver the daily report)."""
        from telegram import Bot

        await Bot(self.token).send_message(chat_id=chat_id, text=text)
