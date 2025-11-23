# test_db.py
"""
DB-layer tests using a temporary SQLite file, so we don't touch the real tutorspark.db.
"""

import sys
from pathlib import Path

# Ensure project root (TutorSpark folder) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sqlite3

import db
import pytest
from models import LearnerProfile, QuizSession


@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    """
    Point db.DB_PATH (or equivalent) to a temp file for this test run.
    Adjust this if your DB module uses a different constant/name.
    """
    test_db = tmp_path / "test_tutorspark.db"

    if hasattr(db, "DB_PATH"):
        monkeypatch.setattr(db, "DB_PATH", test_db)

    db.init_db()
    return test_db


def test_init_db_creates_required_tables(temp_db_path):
    conn = sqlite3.connect(temp_db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name IN ('learner_profiles','quiz_sessions');"
    )
    rows = {r[0] for r in cur.fetchall()}
    conn.close()

    assert "learner_profiles" in rows
    assert "quiz_sessions" in rows


def test_insert_and_fetch_learner_profile_round_trip(temp_db_path):
    profile = LearnerProfile(
        id=None,
        name="Unit Test Hero",
        level="Intermediate",
        focus_area="Data Structures",
        hero_class="Mage",
    )

    # Adjust names to your actual helper functions
    profile_id = db.insert_learner_profile(profile)
    fetched_profiles = db.get_all_profiles()

    assert any(p.id == profile_id and p.name == "Unit Test Hero" for p in fetched_profiles)


def test_insert_quiz_session_persists_stats(temp_db_path):
    # Ensure at least one profile exists
    profiles = db.get_all_profiles()
    if not profiles:
        p = LearnerProfile(
            id=None,
            name="Analytics Hero",
            level="Beginner",
            focus_area="Python Basics",
            hero_class="Warrior",
        )
        profile_id = db.insert_learner_profile(p)
    else:
        profile_id = profiles[0].id

    session = QuizSession(
        id=None,
        profile_id=profile_id,
        topic="CS Questline",
        total_questions=10,
        correct_answers=8,
        created_at="2025-11-23T00:00:00",
    )

    session_id = db.insert_quiz_session(session)

    recent = db.get_recent_quiz_sessions(limit=5)
    assert any(s.id == session_id and s.correct_answers == 8 for s in recent)
