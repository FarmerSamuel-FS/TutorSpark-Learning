from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import LearnerProfile, QuizSession

# SQLite DB stored next to this file
DB_PATH = Path(__file__).with_name("tutorspark.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the database schema if it doesn't exist.
    Tables:
      - learner_profiles
      - quiz_sessions
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS learner_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            focus_area TEXT NOT NULL,
            hero_class TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id)
        );
        """
    )

    conn.commit()
    conn.close()


# --- Learner profile helpers -------------------------------------------------


def load_single_profile() -> Optional[LearnerProfile]:
    """
    For Milestone 1 we assume a single learner profile per machine.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM learner_profiles LIMIT 1;")
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return LearnerProfile(
        id=row["id"],
        name=row["name"],
        level=row["level"],
        focus_area=row["focus_area"],
        hero_class=row["hero_class"],
    )


def insert_profile(profile: LearnerProfile) -> LearnerProfile:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO learner_profiles (name, level, focus_area, hero_class)
        VALUES (?, ?, ?, ?);
        """,
        (profile.name, profile.level, profile.focus_area, profile.hero_class),
    )
    conn.commit()
    profile.id = cur.lastrowid
    conn.close()
    return profile


def reset_all_data() -> None:
    """
    Deletes the SQLite file and recreates an empty schema.
    Used when the player chooses 'Start a new hero' in profile.py.
    """
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


# --- Quiz session helpers ----------------------------------------------------


def insert_quiz_session(session: QuizSession) -> QuizSession:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO quiz_sessions (
            profile_id, topic, total_questions, correct_answers, created_at
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            session.profile_id,
            session.topic,
            session.total_questions,
            session.correct_answers,
            session.created_at.isoformat(),
        ),
    )
    conn.commit()
    session.id = cur.lastrowid
    conn.close()
    return session
