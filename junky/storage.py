"""Local SQLite persistence. Each operation uses its own connection."""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .content import CARDS, LESSON_MAP, STARTER_SNIPPETS


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def data_home():
    value = os.environ.get("SCRIPTJUNKY_HOME")
    if value:
        return Path(value).expanduser().resolve()
    base = os.environ.get("XDG_DATA_HOME")
    return (Path(base).expanduser() if base else Path.home() / ".local" / "share") / "scriptjunky"


def text_field(value, name, limit, required=True):
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{name} is required")
    if len(value) > limit:
        raise ValueError(f"{name} must be at most {limit} characters")
    return value


class Store:
    def __init__(self, home=None, labs_dir=None):
        self.home = Path(home or data_home()).expanduser().resolve()
        # Keep explicit data homes isolated; the normal checkout workflow uses
        # visible project labs. Existing data-home labs retain their location.
        if labs_dir is not None:
            self.labs = Path(labs_dir).expanduser().resolve()
        elif home is not None or os.environ.get("SCRIPTJUNKY_HOME") or (self.home / "labs").exists():
            self.labs = self.home / "labs"
        else:
            self.labs = Path(__file__).resolve().parents[1] / "labs"
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.home / "learning.sqlite3"
        fresh = not self.path.exists()
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL,
                    lesson_id TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL DEFAULT 'note',
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
                    code TEXT NOT NULL, tags TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS progress (
                    lesson_id TEXT PRIMARY KEY, completed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY, lesson_id TEXT NOT NULL, passed INTEGER NOT NULL,
                    details TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    card_id TEXT PRIMARY KEY, repetitions INTEGER NOT NULL,
                    due_at TEXT NOT NULL, last_correct INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                PRAGMA user_version = 1;
            """)
            if fresh:
                timestamp = now()
                for item in STARTER_SNIPPETS:
                    db.execute("INSERT INTO snippets (title, description, code, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                               (item["title"], item["description"], item["code"], item["tags"], timestamp, timestamp))
        self.path.chmod(0o600)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def list_items(self, kind, query=""):
        if kind not in ("journal", "snippets"):
            raise ValueError("Unknown collection")
        query = text_field(query, "search", 300, required=False)
        columns = ("title", "body", "lesson_id") if kind == "journal" else ("title", "description", "code", "tags")
        with self.connection() as db:
            rows = db.execute(f"SELECT * FROM {kind} ORDER BY updated_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows if not query or any(query.casefold() in row[col].casefold() for col in columns)]

    def save_item(self, kind, item, item_id=None):
        if kind == "journal":
            fields = {"title": text_field(item.get("title"), "title", 140),
                      "body": text_field(item.get("body"), "body", 60000),
                      "lesson_id": text_field(item.get("lesson_id", ""), "lesson", 50, False)}
            if fields["lesson_id"] and fields["lesson_id"] not in LESSON_MAP:
                raise ValueError("Unknown lesson")
        elif kind == "snippets":
            fields = {"title": text_field(item.get("title"), "title", 140),
                      "description": text_field(item.get("description", ""), "description", 4000, False),
                      "code": text_field(item.get("code"), "code", 60000),
                      "tags": text_field(item.get("tags", ""), "tags", 300, False)}
        else:
            raise ValueError("Unknown collection")
        timestamp = now()
        with self.connection() as db:
            if item_id is not None:
                assignments = ", ".join(f"{key} = ?" for key in fields)
                cursor = db.execute(f"UPDATE {kind} SET {assignments}, updated_at = ? WHERE id = ?",
                                    (*fields.values(), timestamp, int(item_id)))
                if cursor.rowcount != 1:
                    raise ValueError("Entry not found")
            else:
                keys = ", ".join([*fields, "created_at", "updated_at"])
                marks = ", ".join("?" for _ in range(len(fields) + 2))
                cursor = db.execute(f"INSERT INTO {kind} ({keys}) VALUES ({marks})", (*fields.values(), timestamp, timestamp))
                item_id = cursor.lastrowid
            return dict(db.execute(f"SELECT * FROM {kind} WHERE id = ?", (item_id,)).fetchone())

    def delete_item(self, kind, item_id):
        if kind not in ("journal", "snippets"):
            raise ValueError("Unknown collection")
        with self.connection() as db:
            if db.execute(f"DELETE FROM {kind} WHERE id = ?", (int(item_id),)).rowcount != 1:
                raise ValueError("Entry not found")

    def record_check(self, lesson_id, result):
        timestamp = now()
        with self.connection() as db:
            db.execute("INSERT INTO attempts (lesson_id, passed, details, created_at) VALUES (?, ?, ?, ?)",
                       (lesson_id, int(result["passed"]), json.dumps(result), timestamp))
            if result["passed"]:
                cursor = db.execute("INSERT OR IGNORE INTO progress VALUES (?, ?)", (lesson_id, timestamp))
                if cursor.rowcount:
                    body = "\n".join(f"- {check['label']}: {check['message']}" for check in result["checks"])
                    body += f"\n\nLab: {result['path']}\nChecked at: {timestamp}\nArtifact checks verify results; they do not prove script correctness or reasoning quality."
                    db.execute("INSERT INTO journal (title, body, lesson_id, kind, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                               (f"Lab verified: {LESSON_MAP[lesson_id]['title']}", body, lesson_id, "lab", timestamp, timestamp))

    def progress(self):
        with self.connection() as db:
            completed = [dict(row) for row in db.execute("SELECT * FROM progress ORDER BY completed_at")]
            attempts = [dict(row) for row in db.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT 12")]
        for attempt in attempts:
            attempt["details"] = json.loads(attempt["details"])
        return {"completed": completed, "attempts": attempts}

    def due_cards(self):
        timestamp = now()
        with self.connection() as db:
            reviews = {row["card_id"]: dict(row) for row in db.execute("SELECT * FROM reviews")}
        return [card for card in CARDS if card["id"] not in reviews or reviews[card["id"]]["due_at"] <= timestamp]

    def review(self, card_id, answer):
        card = next((card for card in CARDS if card["id"] == card_id), None)
        if card is None or answer not in card["choices"]:
            raise ValueError("Unknown card or answer")
        correct = answer == card["choices"][card["answer"]]
        current = datetime.now(timezone.utc)
        with self.connection() as db:
            row = db.execute("SELECT * FROM reviews WHERE card_id = ?", (card_id,)).fetchone()
            repetitions = (row["repetitions"] if row else 0) + 1 if correct else 0
            interval = timedelta(days=min(30, 2 ** min(repetitions - 1, 5))) if correct else timedelta(minutes=10)
            due = (current + interval).isoformat(timespec="seconds")
            db.execute("INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?, ?)",
                       (card_id, repetitions, due, int(correct), now()))
        return {"correct": correct, "answer": card["choices"][card["answer"]],
                "explanation": card["explanation"], "due_at": due}

    def export(self):
        with self.connection() as db:
            collections = {table: [dict(row) for row in db.execute(f"SELECT * FROM {table}")]
                           for table in ("journal", "snippets", "progress", "attempts", "reviews")}
        return {"format": "scriptjunky-export", "version": 1, "exported_at": now(), **collections}

    def markdown(self):
        lines = ["# Script Junky field notebook", "", f"Exported: {now()}", "", "## Journal", ""]
        for item in self.list_items("journal"):
            lines.extend([f"### {item['title']}", "", f"{item['created_at']} · {item['lesson_id'] or 'general'}", "", item["body"], ""])
        lines.extend(["## Toolbox", ""])
        for item in self.list_items("snippets"):
            fence = "```"
            while fence in item["code"]:
                fence += "`"
            lines.extend([f"### {item['title']}", "", item["description"], "", f"Tags: {item['tags']}", "", fence + "sh", item["code"], fence, ""])
        lines.extend(["## Verified labs", ""])
        for item in self.progress()["completed"]:
            lines.append(f"- {item['lesson_id']}: {item['completed_at']}")
        return "\n".join(lines) + "\n"
