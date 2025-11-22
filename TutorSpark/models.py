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
class Question:
    """
    Milestone 1 keeps questions in memory instead of a full repository.
    """
    id: int
    topic: str
    prompt: str
    options: List[str]
    correct_index: int
