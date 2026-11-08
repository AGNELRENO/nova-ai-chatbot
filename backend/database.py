
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Database location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "nova_chatbot.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints on every connection
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation
            ON messages(conversation_id, id)
        """)

        conn.execute("PRAGMA foreign_keys = ON")


def create_conversation(conversation_id):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO conversations
            (conversation_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, "New Chat", now, now))


def save_message(conversation_id, role, content):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO messages
            (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, role, content, now))

        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
        """, (now, conversation_id))

        # Set conversation title from the first user message
        if role == "user":
            conn.execute("""
                UPDATE conversations
                SET title = CASE
                    WHEN title = 'New Chat' THEN ?
                    ELSE title
                END
                WHERE conversation_id = ?
            """, (content[:50], conversation_id))


def get_messages(conversation_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conversation_id,)).fetchall()

    return [
        {
            "role": row["role"],
            "parts": [{"text": row["content"]}]
        }
        for row in rows
    ]


def get_all_conversations():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT conversation_id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
        """).fetchall()

    return [dict(row) for row in rows]


def delete_conversation(conversation_id):
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            DELETE FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
