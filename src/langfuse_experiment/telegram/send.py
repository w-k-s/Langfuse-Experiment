import os
import asyncio
from telegram import Bot


def send(msg, to=None, token=None):
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    to = to or os.environ["TELEGRAM_CHAT_ID"]

    async def _send():
        bot = Bot(token)
        sent = await bot.send_message(chat_id=to, text=msg)
        return sent.chat_id, sent.message_id

    chat_id, message_id = asyncio.run(_send())
    return chat_id, message_id
