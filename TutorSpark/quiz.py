from __future__ import annotations

"""
quiz.py

Quest orchestration for TutorSpark CLI.

This module does NOT implement the battle loop (that's in engine.py).
Instead, it:

- Figures out which quest number the hero is on
  (via engine.get_quest_number).
- Loads an appropriate question bank:
      * unseen questions for this hero first (no repeats),
      * falls back to the full QUESTION_BANK if needed.
- Calls AdaptiveEngine.run_quiz_session(...) with a fixed limit of 10.
"""

from typing import List

import db
from engine import AdaptiveEngine, get_quest_number
from models import LearnerProfile, Question, QuizSession
from question_bank import QUESTION_BANK

QUEST_QUESTION_COUNT = 10
TOTAL_QUESTS = 10


def _load_question_pool_for_profile(profile: LearnerProfile) -> List[Question]:
    """
    Load a question pool for this hero, preferring *unseen* questions.

    Uses:
        - db.get_seen_question_ids_for_profile(profile_id)
        - question_bank.QUESTION_BANK
    """
    if profile.id is None:
        # New hero not yet stored; just use the full bank.
        return list(QUESTION_BANK)

    seen_ids = db.get_seen_question_ids_for_profile(profile.id)
    unseen = [q for q in QUESTION_BANK if q.id not in seen_ids]

    if unseen:
        return unseen

    # Fallback: all questions have been seen; allow repeats.
    return list(QUESTION_BANK)


def run_quest_for_profile(engine: AdaptiveEngine, profile: LearnerProfile) -> QuizSession:
    """
    Run a single quest (quiz) for the given hero using the provided engine.

    This enforces:
        - Fixed 10 questions per quest (if available).
        - A maximum of TOTAL_QUESTS quests being "story canon" – after that
          quest numbers clamp at 10 but the player can keep grinding.
    """
    quest_number = get_quest_number(profile)
    if quest_number > TOTAL_QUESTS:
        quest_number = TOTAL_QUESTS  # story label only; engine still runs fine

    question_pool = _load_question_pool_for_profile(profile)
    if not question_pool:
        raise RuntimeError(
            "No questions available. Add questions to QUESTION_BANK in question_bank.py."
        )

    limit = min(QUEST_QUESTION_COUNT, len(question_pool))

    session = engine.run_quiz_session(profile, question_pool, limit=limit)
    return session
