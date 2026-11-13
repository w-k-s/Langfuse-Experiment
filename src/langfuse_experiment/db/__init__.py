import sqlite3
from contextlib import closing
from pathlib import Path

DB_DIR = Path.home() / ".langfuse_experiment"
DB_PATH = DB_DIR / "langfuse.db"


def create_tables():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as con:
        with con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS interrupts (
                    chat_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    thread_id TEXT NOT NULL,
                    interrupt_id TEXT,
                    agent_question TEXT,
                    human_response TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, message_id)
                )
            """)


def create_interrupt(chat_id, message_id, thread_id, agent_question, interrupt_id=None):
    with closing(sqlite3.connect(DB_PATH)) as con:
        with con:
            con.execute(
                """
                INSERT INTO interrupts (chat_id, message_id, thread_id, interrupt_id, agent_question)
                VALUES (?, ?, ?, ?, ?)
                """,
                (chat_id, message_id, thread_id, interrupt_id, agent_question),
            )


def answer_interrupt(chat_id, message_id, human_response):
    with closing(sqlite3.connect(DB_PATH)) as con:
        with con:
            row = con.execute(
                """
                UPDATE interrupts
                SET human_response = ?
                WHERE chat_id = ? AND message_id = ? AND human_response IS NULL
                RETURNING thread_id
                """,
                (human_response, chat_id, message_id),
            ).fetchone()

    if row is None:
        return None
    return row[0]
