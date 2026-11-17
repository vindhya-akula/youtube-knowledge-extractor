
import json
import sqlite3
from pathlib import Path


class SummaryDatabase:
    def __init__(self, db_path="youtube_knowledge.db"):
        self.db_path = str(db_path)

        parent = Path(self.db_path).parent
        if str(parent) not in ("", "."):
            parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    video_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    video_id TEXT PRIMARY KEY,
                    transcript_text TEXT NOT NULL,
                    language TEXT NOT NULL,
                    is_generated INTEGER NOT NULL DEFAULT 0,
                    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Migrate existing databases without deleting saved summaries.
            columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(summaries)"
                ).fetchall()
            }

            if "category" not in columns:
                conn.execute("""
                    ALTER TABLE summaries
                    ADD COLUMN category TEXT NOT NULL DEFAULT 'general'
                """)

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_summary(self, video_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM summaries WHERE video_id = ?",
                (video_id,)
            ).fetchone()

        if not row:
            return None

        item = dict(row)
        item["summary"] = json.loads(item["summary_json"])
        return item

    def save_summary(self, video_id, title, summary, category="general"):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO summaries (
                    video_id, title, summary_json, category
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    title = excluded.title,
                    summary_json = excluded.summary_json,
                    category = excluded.category,
                    created_at = CURRENT_TIMESTAMP
            """, (
                video_id,
                title,
                json.dumps(summary, ensure_ascii=False),
                category
            ))

    def get_transcript(self, video_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM transcripts WHERE video_id = ?",
                (video_id,)
            ).fetchone()

        return dict(row) if row else None

    def save_transcript(self, video_id, text, language, is_generated):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO transcripts (
                    video_id, transcript_text, language, is_generated
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    transcript_text = excluded.transcript_text,
                    language = excluded.language,
                    is_generated = excluded.is_generated,
                    fetched_at = CURRENT_TIMESTAMP
            """, (
                video_id,
                text,
                language,
                int(is_generated)
            ))

    def search_summaries(self, query="", limit=30):
        pattern = f"%{query.strip()}%"

        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM summaries
                WHERE title LIKE ?
                   OR summary_json LIKE ?
                   OR video_id LIKE ?
                   OR category LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (
                pattern,
                pattern,
                pattern,
                pattern,
                limit
            )).fetchall()

        result = []

        for row in rows:
            item = dict(row)
            item["summary"] = json.loads(item["summary_json"])
            result.append(item)

        return result
