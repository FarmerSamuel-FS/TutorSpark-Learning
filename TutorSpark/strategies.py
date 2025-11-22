from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import List

from models import LearnerProfile, Question


class QuestionSelectionStrategy(ABC):
    """
    Strategy interface (from 2.1 Pattern Strategy).

    Different implementations will choose questions using different algorithms.
    """

    @abstractmethod
    def select_questions(
        self,
        all_questions: List[Question],
        profile: LearnerProfile,
        limit: int,
    ) -> List[Question]:
        ...


class SequentialStrategy(QuestionSelectionStrategy):
    """
    Simple sequential selection.

    Returns the first N questions in a fixed order.
    """

    def select_questions(
        self,
        all_questions: List[Question],
        profile: LearnerProfile,
        limit: int,
    ) -> List[Question]:
        return all_questions[:limit]


class RandomStrategy(QuestionSelectionStrategy):
    """
    Random selection / ordering of questions.

    Each quiz session:
      - Shuffles the pool, and
      - Picks up to `limit` questions.

    This gives the 'different questions each time' behavior.
    """

    def select_questions(
        self,
        all_questions: List[Question],
        profile: LearnerProfile,
        limit: int,
    ) -> List[Question]:
        if not all_questions:
            return []

        pool = list(all_questions)
        random.shuffle(pool)

        if limit >= len(pool):
            return pool
        return pool[:limit]
