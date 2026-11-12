import os
import asyncio
from langgraph.types import Command
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from langfuse_experiment.telegram.registry import registry


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

        conv_id = registry.get(replied.message_id)
        if conv_id is None:
            print(f"Ignoring reply to unknown message {replied.message_id}.")
            return

        config = app.runnable_config(conv_id)
        print("Resuming", conv_id, "with", msg.text)
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: graph.invoke(Command(resume=msg.text), config=config)
        )
        print(result)

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, on_message))

    print("listening for messages")
    application.run_polling()
