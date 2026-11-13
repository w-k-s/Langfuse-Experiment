import os
import asyncio
from langgraph.types import Command
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from langfuse_experiment.db import answer_interrupt


def listen(app, graph):
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    async def on_message(update: Update, ctx):
        msg = update.message
        if not msg or not msg.text:
            return

        replied = msg.reply_to_message
        if replied is None:
            print(f"Ignoring '{msg.text}' — not a reply to a question.")
            return

        thread_id = answer_interrupt(msg.chat_id, replied.message_id, msg.text)
        if thread_id is None:
            print(f"Ignoring reply to unknown or already answered message {replied.message_id}.")
            return

        config = app.runnable_config(thread_id)
        print("Resuming", thread_id, "with", msg.text)
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: graph.invoke(Command(resume=msg.text), config=config, context=app),
        )
        print(result)

    async def on_error(update, ctx):
        print(f"Telegram error: {ctx.error!r}")

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, on_message))
    application.add_error_handler(on_error)

    print("listening for messages")
    application.run_polling()
