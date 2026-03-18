"""SQLite 기반 데이터 저장소"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models.user_profile import UserProfile


DB_PATH = Path(__file__).parent.parent / "innerview.db"


class Database:
    """사용자 프로파일 및 게임 세션 저장"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    nickname TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    choice_index INTEGER NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS couple_sessions (
                    session_id TEXT PRIMARY KEY,
                    player_a_id TEXT NOT NULL,
                    player_b_id TEXT NOT NULL,
                    session_json TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (player_a_id) REFERENCES users(user_id),
                    FOREIGN KEY (player_b_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS couple_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (session_id) REFERENCES couple_sessions(session_id)
                );
            """)

    # ──── 사용자 ────

    def create_user(self, user_id: str, nickname: str = "") -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, nickname) VALUES (?, ?)",
                (user_id, nickname),
            )

    def get_user(self, user_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT user_id, nickname, created_at FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if row:
            return {"user_id": row[0], "nickname": row[1], "created_at": row[2]}
        return None

    # ──── 프로파일 ────

    def save_profile(self, profile: UserProfile) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO profiles (user_id, profile_json) VALUES (?, ?)",
                (profile.user_id, profile.model_dump_json()),
            )

    def get_latest_profile(self, user_id: str) -> Optional[UserProfile]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT profile_json FROM profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            ).fetchone()
        if row:
            return UserProfile.model_validate_json(row[0])
        return None

    def get_profile_history(self, user_id: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT profile_json, created_at FROM profiles WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [{"profile": json.loads(r[0]), "created_at": r[1]} for r in rows]

    # ──── 답변 ────

    def save_answer(self, user_id: str, question_id: str, choice_index: int) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO answers (user_id, question_id, choice_index) VALUES (?, ?, ?)",
                (user_id, question_id, choice_index),
            )

    # ──── 커플 세션 ────

    def save_couple_session(self, session_json: str, session_id: str, player_a: str, player_b: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO couple_sessions
                   (session_id, player_a_id, player_b_id, session_json, updated_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                (session_id, player_a, player_b, session_json),
            )

    def save_couple_answer(self, session_id: str, user_id: str, game_type: str, question_id: str, answer: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO couple_answers (session_id, user_id, game_type, question_id, answer) VALUES (?, ?, ?, ?, ?)",
                (session_id, user_id, game_type, question_id, answer),
            )
