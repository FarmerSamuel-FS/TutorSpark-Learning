# test_strategies.py
"""
Tests for question selection strategies used by TutorSpark CLI.
Focus: SequentialStrategy behavior.
"""

import sys
from pathlib import Path

# Ensure project root (TutorSpark folder) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from models import LearnerProfile, Question
from strategies import SequentialStrategy


def make_dummy_profile() -> LearnerProfile:
    """Helper to build a simple learner profile."""
    return LearnerProfile(
        id=None,  # adjust if your dataclass has different fields
        name="Test Hero",
        level="Beginner",
        focus_area="Python Basics",
        hero_class="Warrior",
    )


def make_questions(n: int = 5) -> list[Question]:
    """Create a small bank of dummy questions."""
    questions: list[Question] = []
    for i in range(n):
        questions.append(
            Question(
                id=None if hasattr(Question, "id") else i,
                prompt=f"Q{i}",
                options=["A", "B", "C", "D"],
                correct_index=1,
                topic="CS Fundamentals",
            )
        )
    return questions


def test_sequential_strategy_returns_first_n_questions():
    """Strategy should return the first N questions in order."""
    profile = make_dummy_profile()
    all_questions = make_questions(5)
    strategy = SequentialStrategy()

    selected = strategy.select_questions(all_questions, profile, limit=3)

    assert len(selected) == 3
    assert selected == all_questions[:3]


def test_sequential_strategy_respects_limit_greater_than_pool():
    """If limit > len(pool), it should not crash and just return all questions."""
    profile = make_dummy_profile()
    all_questions = make_questions(4)
    strategy = SequentialStrategy()

    selected = strategy.select_questions(all_questions, profile, limit=10)

    assert len(selected) == 4
    assert selected == all_questions


def test_sequential_strategy_is_deterministic_for_same_inputs():
    """Given the same inputs, strategy should always return the same result."""
    profile = make_dummy_profile()
    all_questions = make_questions(5)
    strategy = SequentialStrategy()

    first_call = strategy.select_questions(all_questions, profile, limit=3)
    second_call = strategy.select_questions(all_questions, profile, limit=3)

    assert first_call == second_call
