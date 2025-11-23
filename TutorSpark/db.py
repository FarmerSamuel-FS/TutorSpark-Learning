from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Set

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
      - seen_questions (which questions a profile has already faced)
    """
    conn = get_connection()
    cur = conn.cursor()

    # learner_profiles now stores hero_class
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS learner_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            focus_area TEXT NOT NULL,
            hero_class TEXT NOT NULL DEFAULT 'Warrior'
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

    # Track which questions each profile has already seen
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_questions (
            profile_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            PRIMARY KEY (profile_id, question_id),
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id)
        );
        """
    )

    conn.commit()
    conn.close()


# --- Helper for handling created_at -----------------------------------------


def _normalise_created_at(value) -> datetime:
    """
    Accepts either a datetime or an ISO8601 string and always returns datetime.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            # Fallback: current time if the string is malformed
            return datetime.utcnow()
    # Fallback for anything unexpected
    return datetime.utcnow()


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


def get_all_profiles() -> List[LearnerProfile]:
    """
    Return all learner profiles (used by tests and future features).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM learner_profiles ORDER BY id ASC;")
    rows = cur.fetchall()
    conn.close()

    profiles: List[LearnerProfile] = []
    for row in rows:
        profiles.append(
            LearnerProfile(
                id=row["id"],
                name=row["name"],
                level=row["level"],
                focus_area=row["focus_area"],
                hero_class=row["hero_class"],
            )
        )
    return profiles


def insert_profile(profile: LearnerProfile) -> LearnerProfile:
    """
    Original insert helper that returns the profile object with id set.
    """
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


def insert_learner_profile(profile: LearnerProfile) -> int:
    """
    Test-friendly wrapper: insert a profile and return the new integer id.
    """
    persisted = insert_profile(profile)
    return persisted.id or 0


def reset_all_data() -> None:
    """
    Used when the player chooses 'Start a new hero' and types RESET.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        DELETE FROM seen_questions;
        DELETE FROM quiz_sessions;
        DELETE FROM learner_profiles;
        VACUUM;
        """
    )
    conn.commit()
    conn.close()


# --- Quiz session helpers ----------------------------------------------------


def insert_quiz_session(session: QuizSession) -> int:
    """
    Insert a QuizSession and return the new integer session id.

    NOTE: This is shaped to work both with the game engine and with
    the pytest tests, which expect `insert_quiz_session(...)` to
    return an int (the session id).
    """
    created_dt = _normalise_created_at(session.created_at)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO quiz_sessions (profile_id, topic, total_questions, correct_answers, created_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            session.profile_id,
            session.topic,
            session.total_questions,
            session.correct_answers,
            created_dt.isoformat(),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    session.id = new_id
    conn.close()
    return new_id


def count_quiz_sessions_for_profile(profile_id: int) -> int:
    """
    How many quiz sessions this profile has completed (all focus areas).
    Used to scale difficulty/length: later quizzes = more questions.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) AS c FROM quiz_sessions WHERE profile_id = ?;",
        (profile_id,),
    )
    row = cur.fetchone()
    conn.close()
    return int(row["c"] if row is not None else 0)


def get_recent_quiz_sessions(limit: int = 10) -> List[QuizSession]:
    """
    Return the most recent quiz sessions across all profiles, newest first.
    Used by tests to verify that stats are persisted correctly.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, profile_id, topic, total_questions, correct_answers, created_at
        FROM quiz_sessions
        ORDER BY created_at DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    sessions: List[QuizSession] = []
    for row in rows:
        created_at_str = row["created_at"]
        try:
            created_dt = datetime.fromisoformat(created_at_str)
        except ValueError:
            created_dt = datetime.utcnow()

        sessions.append(
            QuizSession(
                id=row["id"],
                profile_id=row["profile_id"],
                topic=row["topic"],
                total_questions=row["total_questions"],
                correct_answers=row["correct_answers"],
                created_at=created_dt,
            )
        )
    return sessions


# --- Seen-questions helpers (for multi-level, no-repeat quizzes) ------------


def get_seen_question_ids_for_profile(profile_id: int) -> Set[int]:
    """
    Return the set of question_ids this profile has already seen in any session.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT question_id FROM seen_questions WHERE profile_id = ?;",
        (profile_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return {int(r["question_id"]) for r in rows}


def mark_questions_seen(profile_id: int, question_ids: Iterable[int]) -> None:
    """
    Mark a batch of question IDs as 'seen' for this profile.
    Called at the end of each quiz session so future runs can avoid repeats.
    """
    ids = list(set(int(qid) for qid in question_ids))
    if not ids:
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR IGNORE INTO seen_questions (profile_id, question_id)
        VALUES (?, ?);
        """,
        [(profile_id, qid) for qid in ids],
    )
    conn.commit()
    conn.close()
