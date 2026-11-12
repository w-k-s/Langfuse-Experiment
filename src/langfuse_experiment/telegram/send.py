import os
import asyncio
from uuid import uuid4
from telegram import Bot
from langfuse_experiment.telegram.registry import registry


def send(msg, thread=None, to=None, token=None):
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    to = to or os.environ["TELEGRAM_CHAT_ID"]
    thread = thread or str(uuid4())

    async def _send():
        bot = Bot(token)
        sent = await bot.send_message(chat_id=to, text=msg)
        return sent.message_id

    message_id = asyncio.run(_send())

    if registry is not None:
        registry[message_id] = thread

    return thread, message_id
