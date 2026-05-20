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
from models import (
    LearnerProfile,
    ParticipantDemographic,
    QuizSession,
    StudySession,
    SurveyResponse,
    UsabilityEvent,
)


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
        "AND name IN ("
        "'learner_profiles',"
        "'quiz_sessions',"
        "'usability_events',"
        "'study_sessions',"
        "'survey_responses',"
        "'participant_demographics'"
        ");"
    )
    rows = {r[0] for r in cur.fetchall()}
    conn.close()

    assert "learner_profiles" in rows
    assert "quiz_sessions" in rows
    assert "usability_events" in rows
    assert "study_sessions" in rows
    assert "survey_responses" in rows
    assert "participant_demographics" in rows


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


def test_get_profile_by_name_matches_case_insensitively(temp_db_path):
    profile_id = db.insert_learner_profile(
        LearnerProfile(
            id=None,
            name="Star Scholar",
            level="Participant",
            focus_area="Basic Math",
            hero_class="Mage",
        )
    )

    fetched = db.get_profile_by_name("star scholar")

    assert fetched is not None
    assert fetched.id == profile_id
    assert fetched.name == "Star Scholar"
    assert fetched.hero_class == "Mage"


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


def test_profile_progress_summary_calculates_scores(temp_db_path):
    profile = LearnerProfile(
        id=None,
        name="Summary Hero",
        level="Beginner",
        focus_area="CS Fundamentals",
        hero_class="Warrior",
    )
    profile_id = db.insert_learner_profile(profile)

    db.insert_quiz_session(
        QuizSession(
            id=None,
            profile_id=profile_id,
            topic="Quest 1",
            total_questions=10,
            correct_answers=8,
            created_at="2026-05-10T12:00:00",
        )
    )
    db.insert_quiz_session(
        QuizSession(
            id=None,
            profile_id=profile_id,
            topic="Quest 2",
            total_questions=10,
            correct_answers=6,
            created_at="2026-05-11T12:00:00",
        )
    )

    summary = db.get_profile_progress_summary(profile_id)

    assert summary["session_count"] == 2
    assert summary["total_questions"] == 20
    assert summary["correct_answers"] == 14
    assert summary["average_score"] == 70.0
    assert summary["best_score"] == 80.0
    assert summary["recent_sessions"][0].topic == "Quest 2"


def test_usability_events_round_trip_and_summary_counts(temp_db_path):
    profile = LearnerProfile(
        id=None,
        name="Usability Hero",
        level="Intermediate",
        focus_area="Algorithms",
        hero_class="Mage",
    )
    profile_id = db.insert_learner_profile(profile)
    session_id = db.insert_quiz_session(
        QuizSession(
            id=None,
            profile_id=profile_id,
            topic="Quest 1",
            total_questions=10,
            correct_answers=9,
            created_at="2026-05-12T12:00:00",
        )
    )

    event_id = db.insert_usability_event(
        UsabilityEvent(
            id=None,
            profile_id=profile_id,
            session_id=session_id,
            event_type="hint_used",
            detail="question_id=3; battle=1",
            created_at="2026-05-12T12:01:00",
            question_id=3,
            elapsed_seconds=4.2,
            metadata="remaining_hints=2",
            study_session_id=None,
        )
    )

    recent = db.get_recent_usability_events(profile_id)
    summary = db.get_profile_progress_summary(profile_id)

    assert any(event.id == event_id and event.event_type == "hint_used" for event in recent)
    assert recent[0].question_id == 3
    assert recent[0].elapsed_seconds == 4.2
    assert recent[0].metadata == "remaining_hints=2"
    assert summary["usability_event_counts"]["hint_used"] == 1


def test_study_session_survey_and_metrics(temp_db_path):
    profile = LearnerProfile(
        id=None,
        name="Study Hero",
        level="Beginner",
        focus_area="CS Fundamentals",
        hero_class="Warrior",
    )
    profile_id = db.insert_learner_profile(profile)
    assert db.next_participant_code() == "P001"

    study_id = db.insert_study_session(
        StudySession(
            id=None,
            profile_id=profile_id,
            participant_code="P001",
            task_name="CS Fundamentals usability task",
            started_at="2026-05-12T12:00:00",
        )
    )

    db.insert_usability_events(
        [
            UsabilityEvent(
                id=None,
                profile_id=profile_id,
                session_id=None,
                study_session_id=study_id,
                event_type="answer_submitted",
                detail="battle=1; correct=true",
                created_at="2026-05-12T12:00:10",
                question_id=1,
                elapsed_seconds=10.0,
            ),
            UsabilityEvent(
                id=None,
                profile_id=profile_id,
                session_id=None,
                study_session_id=study_id,
                event_type="hint_used",
                detail="battle=2",
                created_at="2026-05-12T12:00:20",
                question_id=2,
                elapsed_seconds=3.0,
            ),
            UsabilityEvent(
                id=None,
                profile_id=profile_id,
                session_id=None,
                study_session_id=study_id,
                event_type="reflection_prompted",
                detail="battle=2",
                created_at="2026-05-12T12:00:30",
                question_id=2,
                elapsed_seconds=12.0,
            ),
        ]
    )
    db.insert_survey_response(
        SurveyResponse(
            id=None,
            study_session_id=study_id,
            profile_id=profile_id,
            question_key="interface_clarity",
            prompt="The interface was easy to understand.",
            rating=4,
            created_at="2026-05-12T12:01:00",
        )
    )
    db.insert_participant_demographic(
        ParticipantDemographic(
            id=None,
            study_session_id=study_id,
            profile_id=profile_id,
            age_range="25-34",
            learning_background="college",
            cs_experience="beginner",
            primary_device="laptop",
            accessibility_needs="none",
            created_at="2026-05-12T12:00:05",
        )
    )
    db.complete_study_session(study_id)

    metrics = db.get_study_metrics(study_id)

    assert db.next_participant_code() == "P002"
    assert metrics["event_count"] == 3
    assert metrics["answer_count"] == 1
    assert metrics["accuracy_rate"] == 1.0
    assert metrics["support_count"] == 1
    assert metrics["reflection_count"] == 1
    assert metrics["average_answer_seconds"] == 10.0
    assert metrics["average_survey_rating"] == 4.0


def test_leaderboard_ranks_profiles_by_best_score(temp_db_path):
    alpha_id = db.insert_learner_profile(
        LearnerProfile(
            id=None,
            name="Alpha",
            level="Beginner",
            focus_area="CS Fundamentals",
            hero_class="Warrior",
        )
    )
    beta_id = db.insert_learner_profile(
        LearnerProfile(
            id=None,
            name="Beta",
            level="Intermediate",
            focus_area="Algorithms",
            hero_class="Mage",
        )
    )

    db.insert_quiz_session(
        QuizSession(
            id=None,
            profile_id=alpha_id,
            topic="Quest 1 - Python Programming",
            total_questions=10,
            correct_answers=7,
            created_at="2026-05-12T12:00:00",
        )
    )
    db.insert_quiz_session(
        QuizSession(
            id=None,
            profile_id=beta_id,
            topic="Quest 1 - Algorithms & Complexity",
            total_questions=10,
            correct_answers=9,
            created_at="2026-05-12T12:01:00",
        )
    )

    leaderboard = db.get_leaderboard()

    assert leaderboard[0]["name"] == "Beta"
    assert leaderboard[0]["best_score"] == 90.0
    assert leaderboard[1]["name"] == "Alpha"


def test_export_usability_events_csv_writes_analysis_file(temp_db_path, tmp_path):
    profile = LearnerProfile(
        id=None,
        name="CSV Hero",
        level="Beginner",
        focus_area="CS Fundamentals",
        hero_class="Warrior",
    )
    profile_id = db.insert_learner_profile(profile)
    db.insert_usability_event(
        UsabilityEvent(
            id=None,
            profile_id=profile_id,
            session_id=None,
            event_type="reflection_prompted",
            detail="battle=2; prompt=What clue points to the concept?",
            created_at="2026-05-12T12:02:00",
            question_id=8,
            elapsed_seconds=7.5,
            metadata="guardrail=reflection_after_miss",
        )
    )

    output_path = db.export_usability_events_csv(
        profile_id,
        tmp_path / "events.csv",
    )

    contents = output_path.read_text(encoding="utf-8")
    assert "participant_profile_id" in contents
    assert "reflection_prompted" in contents
    assert "guardrail=reflection_after_miss" in contents


def test_export_study_bundle_csv_writes_surveys_and_demographics(temp_db_path, tmp_path):
    profile = LearnerProfile(
        id=None,
        name="Bundle Hero",
        level="Beginner",
        focus_area="General Science",
        hero_class="Warrior",
    )
    profile_id = db.insert_learner_profile(profile)
    study_id = db.insert_study_session(
        StudySession(
            id=None,
            profile_id=profile_id,
            participant_code="P001",
            task_name="General Science usability task",
            started_at="2026-05-12T12:00:00",
        )
    )
    db.insert_survey_response(
        SurveyResponse(
            id=None,
            study_session_id=study_id,
            profile_id=profile_id,
            question_key="interface_clarity",
            prompt="The interface was easy to understand.",
            rating=5,
            created_at="2026-05-12T12:01:00",
        )
    )
    db.insert_participant_demographic(
        ParticipantDemographic(
            id=None,
            study_session_id=study_id,
            profile_id=profile_id,
            age_range="18-24",
            learning_background="college",
            cs_experience="none",
            primary_device="phone",
            accessibility_needs="larger text",
            created_at="2026-05-12T12:00:05",
        )
    )

    paths = db.export_study_bundle_csv(profile_id, tmp_path / "bundle")

    assert paths["events"].exists()
    assert "interface_clarity" in paths["surveys"].read_text(encoding="utf-8")
    demographics = paths["demographics"].read_text(encoding="utf-8")
    assert "18-24" in demographics
    assert "larger text" in demographics
