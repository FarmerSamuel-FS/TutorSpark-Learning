from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class LearnerProfile:
    """
    Represents a learner in TutorSpark CLI.
    Maps to the `learner_profiles` table in SQLite.
    """
    id: Optional[int]
    name: str
    level: str          # Beginner / Intermediate / Advanced / Expert
    focus_area: str     # e.g. "Python Basics", "Data Structures"
    hero_class: str     # Warrior, Mage, Healer, NEO PRO


@dataclass
class QuizSession:
    """
    Represents a single completed quiz / practice session.
    Stored for basic analytics and to feed the adaptive engine later.
    """
    id: Optional[int]
    profile_id: int
    topic: str
    total_questions: int
    correct_answers: int
    created_at: datetime


@dataclass
class UsabilityEvent:
    """
    Represents one measurable interaction during a quiz run.
    Used for Week 2 usability logging and later HCI analysis.
    """
    id: Optional[int]
    profile_id: int
    session_id: Optional[int]
    event_type: str
    detail: str
    created_at: datetime
    question_id: Optional[int] = None
    elapsed_seconds: Optional[float] = None
    metadata: Optional[str] = None
    study_session_id: Optional[int] = None


@dataclass
class StudySession:
    """
    Represents one formal usability-study run for an anonymous participant.
    """
    id: Optional[int]
    profile_id: int
    participant_code: str
    task_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None


@dataclass
class SurveyResponse:
    """
    Stores a post-task usability survey response for later HCI analysis.
    """
    id: Optional[int]
    study_session_id: int
    profile_id: int
    question_key: str
    prompt: str
    rating: int
    created_at: datetime


@dataclass
class ParticipantDemographic:
    """
    Stores anonymous participant context for Week 3 HCI testing.
    """
    id: Optional[int]
    study_session_id: int
    profile_id: int
    age_range: str
    learning_background: str
    cs_experience: str
    primary_device: str
    accessibility_needs: str
    created_at: datetime
    open_feedback: str = ""
    frustration_notes: str = ""
    positive_notes: str = ""


@dataclass
class Question:
    """
    Milestone 1 keeps questions in memory instead of a full repository.
    """
    id: int
    topic: str
    prompt: str
    options: List[str]
    correct_index: int
