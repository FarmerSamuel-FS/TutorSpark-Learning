import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question_bank import (
    SUBJECT_CATEGORIES,
    SUBJECT_QUIZZES,
    get_questions_for_subject,
    get_subject_title,
    get_subjects_for_category,
)


def test_week_three_categories_are_available():
    assert set(SUBJECT_CATEGORIES) == {
        "math",
        "science",
        "history",
        "tech",
        "computer_knowledge",
    }


def test_subject_quizzes_are_available():
    assert set(SUBJECT_QUIZZES) == {
        "basic_math",
        "general_science",
        "history_civics",
        "digital_literacy",
        "internet_safety",
        "cs_fundamentals",
        "algorithms_complexity",
        "data_structures",
        "python_programming",
        "software_engineering",
    }


def test_each_subject_quiz_has_questions():
    for subject_key, subject in SUBJECT_QUIZZES.items():
        questions = get_questions_for_subject(subject_key)

        assert questions, subject_key
        assert all(question.topic in subject["topics"] for question in questions)


def test_computer_knowledge_category_contains_existing_cs_quizzes():
    subject_keys = [
        subject_key
        for subject_key, _ in get_subjects_for_category("computer_knowledge")
    ]

    assert "cs_fundamentals" in subject_keys
    assert "algorithms_complexity" in subject_keys
    assert "data_structures" in subject_keys
    assert "python_programming" in subject_keys
    assert "software_engineering" in subject_keys


def test_unknown_subject_falls_back_to_cs_fundamentals_title():
    assert get_subject_title("not-real") == "CS Fundamentals"
