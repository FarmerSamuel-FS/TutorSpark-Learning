# test_engine.py
"""
Lightweight tests for core quiz-session logic.
These assume small pure helpers in engine.py that update HP / detect game over.
"""

import sys
from pathlib import Path

# Ensure project root (TutorSpark folder) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import engine
import pytest
from models import Question


def make_question(prompt: str = "2 + 2 = ?") -> Question:
    return Question(
        id=None if hasattr(Question, "id") else 1,
        prompt=prompt,
        options=["3", "4", "5", "6"],
        correct_index=1,
        topic="Math",
    )


def test_evaluate_answer_marks_correct_and_incorrect():
    """
    Assumes engine.evaluate_answer(question, chosen_index, current_hp)
    -> (is_correct: bool, new_hp: int)
    """
    q = make_question()
    hp_start = 3

    is_correct, hp_after = engine.evaluate_answer(q, chosen_index=1, current_hp=hp_start)
    assert is_correct is True
    assert hp_after == hp_start  # no HP loss on correct

    is_correct2, hp_after2 = engine.evaluate_answer(q, chosen_index=0, current_hp=hp_start)
    assert is_correct2 is False
    assert hp_after2 == hp_start - 1


def test_is_game_over_when_hp_zero_or_no_questions():
    """
    Assumes engine.is_game_over(current_hp, remaining_questions) -> bool.
    """
    assert engine.is_game_over(current_hp=0, remaining_questions=5) is True
    assert engine.is_game_over(current_hp=1, remaining_questions=0) is True
    assert engine.is_game_over(current_hp=3, remaining_questions=5) is False


def test_enemy_name_for_topic_covers_week3_categories():
    assert engine.enemy_name_for_topic("Arithmetic") == "Number Wraith"
    assert engine.enemy_name_for_topic("Life Science") == "Lab Slime"
    assert engine.enemy_name_for_topic("Civics") == "Timeline Phantom"
    assert engine.enemy_name_for_topic("Internet Safety") == "Glitch Imp"
    assert engine.enemy_name_for_topic("Algorithms") == "Sorting Slime"
