from __future__ import annotations

import sqlite3
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from models import (
    LearnerProfile,
    ParticipantDemographic,
    QuizSession,
    StudySession,
    SurveyResponse,
    UsabilityEvent,
)

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

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usability_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            session_id INTEGER,
            event_type TEXT NOT NULL,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL,
            question_id INTEGER,
            elapsed_seconds REAL,
            metadata TEXT,
            study_session_id INTEGER,
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id),
            FOREIGN KEY(session_id) REFERENCES quiz_sessions(id),
            FOREIGN KEY(study_session_id) REFERENCES study_sessions(id)
        );
        """
    )

    _ensure_column(cur, "usability_events", "question_id", "INTEGER")
    _ensure_column(cur, "usability_events", "elapsed_seconds", "REAL")
    _ensure_column(cur, "usability_events", "metadata", "TEXT")
    _ensure_column(cur, "usability_events", "study_session_id", "INTEGER")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            participant_code TEXT NOT NULL,
            task_name TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_session_id INTEGER NOT NULL,
            profile_id INTEGER NOT NULL,
            question_key TEXT NOT NULL,
            prompt TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(study_session_id) REFERENCES study_sessions(id),
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS participant_demographics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_session_id INTEGER NOT NULL,
            profile_id INTEGER NOT NULL,
            age_range TEXT NOT NULL,
            learning_background TEXT NOT NULL,
            cs_experience TEXT NOT NULL,
            primary_device TEXT NOT NULL,
            accessibility_needs TEXT NOT NULL,
            created_at TEXT NOT NULL,
            open_feedback TEXT NOT NULL DEFAULT '',
            frustration_notes TEXT NOT NULL DEFAULT '',
            positive_notes TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(study_session_id) REFERENCES study_sessions(id),
            FOREIGN KEY(profile_id) REFERENCES learner_profiles(id)
        );
        """
    )
    _ensure_column(cur, "participant_demographics", "open_feedback", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(cur, "participant_demographics", "frustration_notes", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(cur, "participant_demographics", "positive_notes", "TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()


# --- Helper for handling created_at -----------------------------------------


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, column_type: str) -> None:
    """
    Add a column to an existing SQLite table if a prior build created it without
    the new Week 2 experimental-data fields.
    """
    cur.execute(f"PRAGMA table_info({table});")
    existing = {row["name"] for row in cur.fetchall()}
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type};")


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


def get_profile_by_name(name: str) -> Optional[LearnerProfile]:
    """
    Return a learner profile by hero name, matching case-insensitively.
    Used by the web/Pi study flow so returning users can load the same hero.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM learner_profiles
        WHERE lower(name) = lower(?)
        ORDER BY id ASC
        LIMIT 1;
        """,
        (name.strip(),),
    )
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


def update_profile_hero_class(profile_id: int, hero_class: str) -> None:
    """
    Update the hero class for an existing profile while keeping its progress.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE learner_profiles
        SET hero_class = ?
        WHERE id = ?;
        """,
        (hero_class, profile_id),
    )
    conn.commit()
    conn.close()


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
        DELETE FROM usability_events;
        DELETE FROM survey_responses;
        DELETE FROM participant_demographics;
        DELETE FROM study_sessions;
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


def insert_usability_event(event: UsabilityEvent) -> int:
    """
    Insert one learner interaction event and return its new id.
    """
    created_dt = _normalise_created_at(event.created_at)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO usability_events (
            profile_id,
            session_id,
            event_type,
            detail,
            created_at,
            question_id,
            elapsed_seconds,
            metadata,
            study_session_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            event.profile_id,
            event.session_id,
            event.event_type,
            event.detail,
            created_dt.isoformat(),
            event.question_id,
            event.elapsed_seconds,
            event.metadata,
            event.study_session_id,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    event.id = new_id
    conn.close()
    return new_id


def insert_usability_events(events: Iterable[UsabilityEvent]) -> List[int]:
    """
    Persist multiple usability events and return their ids.
    Kept simple because Week 2 event volume is small.
    """
    ids: List[int] = []
    for event in events:
        ids.append(insert_usability_event(event))
    return ids


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


def get_recent_usability_events(profile_id: int, limit: int = 10) -> List[UsabilityEvent]:
    """
    Return recent interaction events for one profile, newest first.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id,
            profile_id,
            session_id,
            event_type,
            detail,
            created_at,
            question_id,
            elapsed_seconds,
            metadata,
            study_session_id
        FROM usability_events
        WHERE profile_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?;
        """,
        (profile_id, limit),
    )
    rows = cur.fetchall()
    conn.close()

    events: List[UsabilityEvent] = []
    for row in rows:
        try:
            created_dt = datetime.fromisoformat(row["created_at"])
        except ValueError:
            created_dt = datetime.utcnow()
        events.append(
            UsabilityEvent(
                id=row["id"],
                profile_id=row["profile_id"],
                session_id=row["session_id"],
                event_type=row["event_type"],
                detail=row["detail"],
                created_at=created_dt,
                question_id=row["question_id"],
                elapsed_seconds=row["elapsed_seconds"],
                metadata=row["metadata"],
                study_session_id=row["study_session_id"],
            )
        )
    return events


def next_participant_code() -> str:
    """
    Return the next anonymous participant code, such as P001.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM study_sessions;")
    row = cur.fetchone()
    conn.close()
    return f"P{int(row['c']) + 1:03d}"


def insert_study_session(study: StudySession) -> int:
    started_at = _normalise_created_at(study.started_at)
    completed_at = (
        _normalise_created_at(study.completed_at).isoformat()
        if study.completed_at is not None
        else None
    )

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO study_sessions (
            profile_id,
            participant_code,
            task_name,
            started_at,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            study.profile_id,
            study.participant_code,
            study.task_name,
            started_at.isoformat(),
            completed_at,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    study.id = new_id
    conn.close()
    return new_id


def complete_study_session(study_session_id: int, completed_at: datetime | None = None) -> None:
    completed_dt = completed_at or datetime.utcnow()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE study_sessions
        SET completed_at = ?
        WHERE id = ?;
        """,
        (completed_dt.isoformat(), study_session_id),
    )
    conn.commit()
    conn.close()


def insert_survey_response(response: SurveyResponse) -> int:
    created_dt = _normalise_created_at(response.created_at)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO survey_responses (
            study_session_id,
            profile_id,
            question_key,
            prompt,
            rating,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            response.study_session_id,
            response.profile_id,
            response.question_key,
            response.prompt,
            response.rating,
            created_dt.isoformat(),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    response.id = new_id
    conn.close()
    return new_id


def insert_survey_responses(responses: Iterable[SurveyResponse]) -> List[int]:
    ids: List[int] = []
    for response in responses:
        ids.append(insert_survey_response(response))
    return ids


def insert_participant_demographic(demographic: ParticipantDemographic) -> int:
    """
    Store one anonymous demographic record for a formal HCI study run.
    """
    created_dt = _normalise_created_at(demographic.created_at)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO participant_demographics (
            study_session_id,
            profile_id,
            age_range,
            learning_background,
            cs_experience,
            primary_device,
            accessibility_needs,
            created_at,
            open_feedback,
            frustration_notes,
            positive_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            demographic.study_session_id,
            demographic.profile_id,
            demographic.age_range,
            demographic.learning_background,
            demographic.cs_experience,
            demographic.primary_device,
            demographic.accessibility_needs,
            created_dt.isoformat(),
            demographic.open_feedback,
            demographic.frustration_notes,
            demographic.positive_notes,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    demographic.id = new_id
    conn.close()
    return new_id


def get_study_metrics(study_session_id: int) -> Dict[str, Any]:
    """
    Return computed metrics for one formal usability-study session.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) AS event_count,
            SUM(CASE WHEN event_type = 'answer_submitted' THEN 1 ELSE 0 END) AS answer_count,
            SUM(CASE WHEN event_type = 'answer_submitted' AND detail LIKE '%correct=true%' THEN 1 ELSE 0 END) AS correct_count,
            SUM(CASE WHEN event_type IN ('hint_used', 'fifty_fifty_used', 'friend_call_used', 'free_pass_used') THEN 1 ELSE 0 END) AS support_count,
            SUM(CASE WHEN event_type = 'guardrail_retry_prompted' THEN 1 ELSE 0 END) AS retry_count,
            SUM(CASE WHEN event_type = 'reflection_prompted' THEN 1 ELSE 0 END) AS reflection_count,
            COALESCE(AVG(CASE WHEN event_type = 'answer_submitted' THEN elapsed_seconds END), 0) AS avg_answer_seconds
        FROM usability_events
        WHERE study_session_id = ?;
        """,
        (study_session_id,),
    )
    event_row = cur.fetchone()

    cur.execute(
        """
        SELECT COALESCE(AVG(rating), 0) AS avg_survey_rating
        FROM survey_responses
        WHERE study_session_id = ?;
        """,
        (study_session_id,),
    )
    survey_row = cur.fetchone()
    conn.close()

    answer_count = int(event_row["answer_count"] or 0)
    correct_count = int(event_row["correct_count"] or 0)
    support_count = int(event_row["support_count"] or 0)

    return {
        "event_count": int(event_row["event_count"] or 0),
        "answer_count": answer_count,
        "correct_count": correct_count,
        "accuracy_rate": (correct_count / answer_count) if answer_count else 0.0,
        "support_count": support_count,
        "support_usage_rate": (support_count / answer_count) if answer_count else 0.0,
        "retry_count": int(event_row["retry_count"] or 0),
        "reflection_count": int(event_row["reflection_count"] or 0),
        "average_answer_seconds": float(event_row["avg_answer_seconds"] or 0.0),
        "average_survey_rating": float(survey_row["avg_survey_rating"] or 0.0),
    }


def export_usability_events_csv(profile_id: int, output_path: Path) -> Path:
    """
    Export one participant/profile's interaction log for HCI analysis.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id,
            profile_id,
            session_id,
            event_type,
            detail,
            created_at,
            question_id,
            elapsed_seconds,
            metadata,
            study_session_id
        FROM usability_events
        WHERE profile_id = ?
        ORDER BY created_at ASC, id ASC;
        """,
        (profile_id,),
    )
    rows = cur.fetchall()
    conn.close()

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "participant_profile_id",
                "session_id",
                "event_type",
                "detail",
                "created_at",
                "question_id",
                "elapsed_seconds",
                "metadata",
                "study_session_id",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["id"],
                    row["profile_id"],
                    row["session_id"],
                    row["event_type"],
                    row["detail"],
                    row["created_at"],
                    row["question_id"],
                    row["elapsed_seconds"],
                    row["metadata"],
                    row["study_session_id"],
                ]
            )
    return output_path


def export_study_bundle_csv(profile_id: int, output_dir: Path) -> Dict[str, Path]:
    """
    Export Week 3 HCI data as separate CSV files: events, surveys, and demographics.
    Keeping files separate makes spreadsheet analysis cleaner for the paper.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = export_usability_events_csv(profile_id, output_dir / "usability_events.csv")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            sr.id,
            ss.participant_code,
            sr.study_session_id,
            sr.profile_id,
            sr.question_key,
            sr.prompt,
            sr.rating,
            sr.created_at
        FROM survey_responses sr
        JOIN study_sessions ss ON ss.id = sr.study_session_id
        WHERE sr.profile_id = ?
        ORDER BY sr.created_at ASC, sr.id ASC;
        """,
        (profile_id,),
    )
    survey_rows = cur.fetchall()

    cur.execute(
        """
        SELECT
            pd.id,
            ss.participant_code,
            pd.study_session_id,
            pd.profile_id,
            pd.age_range,
            pd.learning_background,
            pd.cs_experience,
            pd.primary_device,
            pd.accessibility_needs,
            pd.created_at,
            pd.open_feedback,
            pd.frustration_notes,
            pd.positive_notes
        FROM participant_demographics pd
        JOIN study_sessions ss ON ss.id = pd.study_session_id
        WHERE pd.profile_id = ?
        ORDER BY pd.created_at ASC, pd.id ASC;
        """,
        (profile_id,),
    )
    demographic_rows = cur.fetchall()
    conn.close()

    survey_path = output_dir / "survey_responses.csv"
    with survey_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "participant_code",
                "study_session_id",
                "profile_id",
                "question_key",
                "prompt",
                "rating",
                "created_at",
            ]
        )
        for row in survey_rows:
            writer.writerow([row[column] for column in row.keys()])

    demographic_path = output_dir / "participant_demographics.csv"
    with demographic_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "participant_code",
                "study_session_id",
                "profile_id",
                "age_range",
                "learning_background",
                "cs_experience",
                "primary_device",
                "accessibility_needs",
                "created_at",
                "open_feedback",
                "frustration_notes",
                "positive_notes",
            ]
        )
        for row in demographic_rows:
            writer.writerow([row[column] for column in row.keys()])

    return {
        "events": events_path,
        "surveys": survey_path,
        "demographics": demographic_path,
    }


def get_profile_progress_summary(profile_id: int, recent_limit: int = 5) -> Dict[str, Any]:
    """
    Return compact analytics for one learner profile.

    This is intentionally small for Week 1: it gives the demo a visible
    progress readout while keeping the data model simple enough to extend
    into knowledge tracing later.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) AS session_count,
            COALESCE(SUM(total_questions), 0) AS total_questions,
            COALESCE(SUM(correct_answers), 0) AS correct_answers,
            COALESCE(MAX(
                CASE
                    WHEN total_questions > 0
                    THEN (correct_answers * 100.0 / total_questions)
                    ELSE 0
                END
            ), 0) AS best_score
        FROM quiz_sessions
        WHERE profile_id = ?;
        """,
        (profile_id,),
    )
    summary_row = cur.fetchone()

    cur.execute(
        """
        SELECT id, profile_id, topic, total_questions, correct_answers, created_at
        FROM quiz_sessions
        WHERE profile_id = ?
        ORDER BY created_at DESC
        LIMIT ?;
        """,
        (profile_id, recent_limit),
    )
    recent_rows = cur.fetchall()
    cur.execute(
        """
        SELECT event_type, COUNT(*) AS event_count
        FROM usability_events
        WHERE profile_id = ?
        GROUP BY event_type
        ORDER BY event_type ASC;
        """,
        (profile_id,),
    )
    event_rows = cur.fetchall()
    cur.execute(
        """
        SELECT
            COALESCE(AVG(elapsed_seconds), 0) AS avg_elapsed_seconds,
            COALESCE(MAX(elapsed_seconds), 0) AS max_elapsed_seconds
        FROM usability_events
        WHERE profile_id = ? AND event_type = 'answer_submitted';
        """,
        (profile_id,),
    )
    timing_row = cur.fetchone()
    conn.close()

    session_count = int(summary_row["session_count"] if summary_row else 0)
    total_questions = int(summary_row["total_questions"] if summary_row else 0)
    correct_answers = int(summary_row["correct_answers"] if summary_row else 0)
    average_score = (
        (correct_answers / total_questions) * 100.0
        if total_questions > 0
        else 0.0
    )
    best_score = float(summary_row["best_score"] if summary_row else 0.0)

    recent_sessions: List[QuizSession] = []
    for row in recent_rows:
        try:
            created_dt = datetime.fromisoformat(row["created_at"])
        except ValueError:
            created_dt = datetime.utcnow()
        recent_sessions.append(
            QuizSession(
                id=row["id"],
                profile_id=row["profile_id"],
                topic=row["topic"],
                total_questions=row["total_questions"],
                correct_answers=row["correct_answers"],
                created_at=created_dt,
            )
        )

    return {
        "session_count": session_count,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "average_score": average_score,
        "best_score": best_score,
        "recent_sessions": recent_sessions,
        "usability_event_counts": {
            row["event_type"]: int(row["event_count"]) for row in event_rows
        },
        "average_answer_seconds": float(
            timing_row["avg_elapsed_seconds"] if timing_row else 0.0
        ),
        "slowest_answer_seconds": float(
            timing_row["max_elapsed_seconds"] if timing_row else 0.0
        ),
    }


def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Rank saved learner profiles by best quiz score, then average score.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            lp.id AS profile_id,
            lp.name,
            lp.hero_class,
            lp.focus_area,
            COUNT(qs.id) AS session_count,
            COALESCE(SUM(qs.total_questions), 0) AS total_questions,
            COALESCE(SUM(qs.correct_answers), 0) AS correct_answers,
            COALESCE(MAX(
                CASE
                    WHEN qs.total_questions > 0
                    THEN qs.correct_answers * 100.0 / qs.total_questions
                    ELSE 0
                END
            ), 0) AS best_score,
            COALESCE(AVG(
                CASE
                    WHEN qs.total_questions > 0
                    THEN qs.correct_answers * 100.0 / qs.total_questions
                    ELSE 0
                END
            ), 0) AS average_score
        FROM learner_profiles lp
        LEFT JOIN quiz_sessions qs ON qs.profile_id = lp.id
        GROUP BY lp.id
        ORDER BY best_score DESC, average_score DESC, correct_answers DESC, session_count DESC, lp.name ASC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "profile_id": row["profile_id"],
            "name": row["name"],
            "hero_class": row["hero_class"],
            "focus_area": row["focus_area"],
            "session_count": int(row["session_count"]),
            "total_questions": int(row["total_questions"]),
            "correct_answers": int(row["correct_answers"]),
            "best_score": float(row["best_score"]),
            "average_score": float(row["average_score"]),
        }
        for row in rows
    ]


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
