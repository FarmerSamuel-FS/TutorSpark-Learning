from __future__ import annotations

import os
import random
import time
from datetime import datetime
from typing import List, Set, Tuple

import db
from models import LearnerProfile, Question, QuizSession
from strategies import QuestionSelectionStrategy

# === Terminal styling / graphics helpers ====================================

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


def color(text: str, *styles: str) -> str:
    if not styles:
        return text
    return "".join(styles) + text + RESET


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(title: str) -> None:
    line = "=" * (len(title) + 4)
    print(f"\n{line}\n| {title} |\n{line}\n")


def print_boxed(lines: List[str]) -> None:
    if not lines:
        return
    width = max(len(line) for line in lines)
    border = "+" + "-" * (width + 2) + "+"
    print("\n" + border)
    for line in lines:
        print(f"| {line.ljust(width)} |")
    print(border)


def render_bar(current: int, maximum: int, length: int = 20, fill_char: str = "#") -> str:
    if maximum <= 0:
        ratio = 0.0
    else:
        ratio = current / maximum
    filled = int(length * ratio)
    filled = max(0, min(filled, length))
    bar = fill_char * filled + "-" * (length - filled)
    return f"[{bar}] {current}/{maximum}"


def pause_dots(message: str, dot_count: int = 3, delay: float = 0.25) -> None:
    print(message, end="", flush=True)
    for _ in range(dot_count):
        print(".", end="", flush=True)
        time.sleep(delay)
    print()


def render_run_path(current_battle: int, total: int) -> str:
    segments: List[str] = []
    for i in range(1, total + 1):
        if i < current_battle:
            segments.append("✔")
        elif i == current_battle:
            segments.append("▶")
        else:
            segments.append("·")
    return " ".join(segments)


# === Domain helpers =========================================================

_HINTS = {
    1: "Think divide-and-conquer: you keep halving the search space.",
    2: "Customers lining up at a bank are a common real-world analogy.",
    3: "It's a three-letter keyword that starts most function definitions.",
    4: "Among the choices, pick the one that grows slightly faster than linear.",
    5: "Good tests describe expected behavior and catch future mistakes.",
    6: "This command records a snapshot of your changes locally.",
    7: "This complexity grows exponentially with input size.",
    8: "Picture a stack of plates on a table.",
    9: "In Python, Boolean literals start with a capital letter.",
    10: "It’s one of the four OOP pillars and protects internal state.",
    11: "It’s a graph algorithm named after a Dutch computer scientist.",
    12: "On average, hashing gives constant-time lookup.",
    13: "It is a document that defines how Python code should be formatted.",
    14: "This kind of testing focuses on the smallest testable parts.",
    15: "It both fetches and integrates changes from the remote.",
    16: "Divide-and-conquer sort that splits, sorts, and merges.",
    17: "This tree type automatically keeps itself balanced.",
    18: "It describes an upper bound on growth rate as n grows.",
    19: "Count how many elements are inside the list.",
    20: "This pattern lets you swap algorithms without changing the client code.",
    21: "Every push can trigger automated builds and tests.",
    22: "Lets you work on features independently, then merge later.",
    23: "Use a queue to visit nodes level by level.",
    24: "This structure efficiently maintains the highest (or lowest) priority item.",
    25: "It compares values, not memory identities.",
}


def compute_grade_and_feedback(score_percent: float) -> Tuple[str, str]:
    if score_percent >= 90:
        return "A", "Outstanding work – you’re mastering these topics!"
    if score_percent >= 80:
        return "B", "Great job – a bit more practice and you’ll be at the top."
    if score_percent >= 70:
        return "C", "Solid foundation – review missed questions to level up."
    if score_percent >= 60:
        return "D", "You’re close – another focused session will help a lot."
    return "F", "This is a starting point – use the feedback to guide your next run."


def assign_badge(score_percent: float, total_questions: int, correct: int) -> str:
    if total_questions > 0 and correct == total_questions:
        return "🏆 Perfect Run"
    if score_percent >= 80:
        return "⭐ CS Rising Star"
    if score_percent >= 60:
        return "🎯 Solid Start"
    if total_questions > 0:
        return "👣 First Steps"
    return "📎 Session Recorded"


def render_progress_bar(score_percent: float, length: int = 20) -> str:
    filled = int(length * (score_percent / 100.0))
    filled = max(0, min(filled, length))
    bar = "#" * filled + "-" * (length - filled)
    return f"[{bar}]"


def enemy_name_for_topic(topic: str) -> str:
    topic_lower = topic.lower()
    if "algorithm" in topic_lower:
        return "Sorting Slime"
    if "data" in topic_lower:
        return "Queue Goblin"
    if "programming" in topic_lower:
        return "Syntax Sprite"
    if "complexity" in topic_lower:
        return "Big-O Ogre"
    if "software" in topic_lower:
        return "Regression Wraith"
    if "version" in topic_lower:
        return "Merge Goblin"
    return "Logic Gremlin"


def friend_suggestion(q: Question) -> int:
    """
    Simulate 'Call a friend' suggestion.
    75% chance of suggesting the correct answer, otherwise a random wrong one.
    """
    if random.random() < 0.75:
        return q.correct_index
    wrongs = [i for i in range(len(q.options)) if i != q.correct_index]
    return random.choice(wrongs) if wrongs else q.correct_index


def get_hint_for_question(q: Question) -> str:
    return _HINTS.get(
        q.id,
        "Think carefully about the core concept this question is testing.",
    )


def apply_fifty_fifty(q: Question, hidden: Set[int]) -> str:
    """
    50/50 lifeline: hide two wrong options.
    """
    candidates = [i for i in range(len(q.options))
                  if i != q.correct_index and i not in hidden]
    if len(candidates) <= 1:
        return "50/50 can’t eliminate any more options."
    to_hide = set(random.sample(candidates, k=min(2, len(candidates))))
    hidden.update(to_hide)
    return "50/50 used: two incorrect options have been removed."


def hero_stats(profile: LearnerProfile) -> Tuple[int, int, int, int, int, int]:
    """
    Map hero_class to starting stats.

    Returns:
      max_hp, damage_on_hit, hints_left, fifty_fifty_left, calls_left, free_passes
    """
    hc = profile.hero_class.lower()

    # Warrior – Beginner: high HP, forgiving
    if hc == "warrior":
        return 24, 3, 4, 2, 1, 0

    # Mage – Intermediate: balanced, extra hints
    if hc == "mage":
        return 20, 4, 5, 1, 1, 0

    # Healer – Advanced: slightly lower HP, +1 free pass
    if hc == "healer":
        return 18, 3, 3, 2, 1, 1

    # NEO PRO – Expert: lowest HP, minimal lifelines
    if hc == "neo pro":
        return 16, 5, 2, 1, 0, 0

    # Fallback defaults
    return 20, 4, 3, 2, 1, 0


# === Adaptive Engine ========================================================

class AdaptiveEngine:
    """
    AdaptiveEngine composes a QuestionSelectionStrategy.

    Matches your 2.1 Strategy design:
      - AdaptiveEngine has a composition relationship with QuestionSelectionStrategy.
      - Concrete strategies (SequentialStrategy, RandomStrategy) implement the interface.

    Here we layer on:
      - RPG-style HP battles and HUD
      - Lifelines: Hint (text clue), 50/50, Call a friend, Free pass
      - XP, streaks, badges, progress bar
      - QuizSession persistence for analytics/V&V
    """

    def __init__(self, selection_strategy: QuestionSelectionStrategy) -> None:
        self._selection_strategy = selection_strategy

    def run_quiz_session(
        self,
        profile: LearnerProfile,
        question_bank: List[Question],
        limit: int = 5,
    ) -> QuizSession:
        selected = self._selection_strategy.select_questions(
            question_bank,
            profile,
            limit=limit,
        )

        total = len(selected)
        correct = 0
        current_streak = 0
        best_streak = 0

        # Hero-based stats
        max_hp, damage_on_hit, hints_left, fifty_fifty_left, calls_left, free_passes = hero_stats(profile)
        hp = max_hp

        clear_screen()
        print_banner("TutorSpark Training Grounds")
        print(
            color(
                f"Hero: {profile.name} the {profile.hero_class}  |  "
                f"Level: {profile.level}  |  Focus: {profile.focus_area}",
                CYAN,
            )
        )
        print(color(f"Starting HP: {render_bar(hp, max_hp, fill_char='❤')}", YELLOW))

        for idx, q in enumerate(selected, start=1):
            if hp <= 0:
                break

            enemy_name = enemy_name_for_topic(q.topic)
            hidden_indices: Set[int] = set()
            used_hint_this_question = False
            used_fifty_this_question = False
            used_friend_this_question = False

            while True:
                print("\n" + "-" * 70)
                print(color(f"⚔️  Battle {idx}/{total}: A wild {enemy_name} appears!", BOLD))
                print(color(f"Topic: {q.topic}", CYAN))
                print(color(f"Path: {render_run_path(idx, total)}", CYAN))
                print(color(f"HP: {render_bar(hp, max_hp, fill_char='❤')}", YELLOW))
                print(
                    f"Streak: {current_streak}   "
                    f"Hints: {hints_left}   50/50: {fifty_fifty_left}   "
                    f"Call: {calls_left}   Free passes: {free_passes}"
                )
                print("-" * 70)
                print(q.prompt)

                for opt_index, option in enumerate(q.options, start=1):
                    if opt_index - 1 in hidden_indices:
                        print(f"  {opt_index}. [eliminated]")
                    else:
                        print(f"  {opt_index}. {option}")

                print(
                    "\nChoose: 1–4 to answer, "
                    "H=Hint, F=50/50, C=Call a friend, P=Free pass"
                )
                raw = input("Your move: ").strip().upper()

                is_correct = False
                used_free_pass = False

                # Answer
                if raw in {"1", "2", "3", "4"}:
                    answer_idx = int(raw) - 1
                    if answer_idx in hidden_indices:
                        print("That option has been eliminated. Pick another.")
                        continue
                    is_correct = (answer_idx == q.correct_index)
                    break

                # Hint (text clue only)
                elif raw == "H":
                    if hints_left <= 0:
                        print("You have no hints left.")
                        continue
                    if used_hint_this_question:
                        print("You already used a hint on this question.")
                        continue
                    hints_left -= 1
                    used_hint_this_question = True
                    hint_text = get_hint_for_question(q)
                    print(color(f"Hint: {hint_text}", CYAN))
                    continue

                # 50/50
                elif raw == "F":
                    if fifty_fifty_left <= 0:
                        print("You have no 50/50 lifelines left.")
                        continue
                    if used_fifty_this_question:
                        print("You already used 50/50 on this question.")
                        continue
                    fifty_fifty_left -= 1
                    used_fifty_this_question = True
                    msg = apply_fifty_fifty(q, hidden_indices)
                    print(color(msg, CYAN))
                    continue

                # Call a friend
                elif raw == "C":
                    if calls_left <= 0:
                        print("You have no calls left.")
                        continue
                    if used_friend_this_question:
                        print("You already called a friend for this question.")
                        continue
                    calls_left -= 1
                    used_friend_this_question = True
                    suggestion = friend_suggestion(q)
                    print(
                        color(
                            f"📞 Your friend thinks the answer is option {suggestion + 1} "
                            "(but they might be wrong!).",
                            CYAN,
                        )
                    )
                    continue

                # Free pass
                elif raw == "P":
                    if free_passes <= 0:
                        print("You don't have any free passes yet. "
                              "Earn them by getting answer streaks of 3.")
                        continue
                    free_passes -= 1
                    used_free_pass = True
                    is_correct = True
                    print(color("You use a free pass and avoid taking damage!", GREEN))
                    break

                else:
                    print("Invalid choice. Try again.")
                    continue

            # Resolve outcome
            if is_correct:
                print(color("✨ Correct! The enemy is defeated.", GREEN, BOLD))
                correct += 1

                if not used_free_pass:
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)

                    if current_streak > 0 and current_streak % 3 == 0:
                        free_passes += 1
                        print(
                            color(
                                "🔥 Hot streak! You unlocked a FREE PASS (P) for a future battle.",
                                YELLOW,
                            )
                        )
                else:
                    print("Your streak stays where it is thanks to the free pass.")
            else:
                correct_answer = q.options[q.correct_index]
                print(
                    color(
                        f"💥 Incorrect. The correct answer was: {correct_answer}",
                        RED,
                    )
                )
                hp -= damage_on_hit
                if hp < 0:
                    hp = 0
                current_streak = 0
                print(color(f"Your HP drops to: {render_bar(hp, max_hp, fill_char='❤')}", RED))

                if hp <= 0:
                    print(color("\n💀 You are out of HP for this training run!", RED, BOLD))
                    break

        # Summary
        score_percent = (correct / total * 100) if total else 0.0
        grade, feedback = compute_grade_and_feedback(score_percent)
        badge = assign_badge(score_percent, total, correct)
        progress_bar = render_progress_bar(score_percent)

        base_xp = correct * 10
        streak_bonus = best_streak * 5
        xp_earned = base_xp + streak_bonus

        pause_dots("\nCalculating training results", dot_count=5, delay=0.2)

        summary_lines = [
            f"Score: {correct}/{total} ({score_percent:.0f}%)   Grade: {grade}",
            f"Best streak (combo): {best_streak}",
            f"XP earned this session: {xp_earned}",
            f"Badge unlocked: {badge}",
        ]
        print_boxed(summary_lines)
        print(color(f"\nCoach notes: {feedback}", CYAN))
        print(color(f"Overall progress: {progress_bar}", YELLOW))

        session = QuizSession(
            id=None,
            profile_id=profile.id or 0,
            topic="CS Fundamentals (Milestone 1)",
            total_questions=total,
            correct_answers=correct,
            created_at=datetime.utcnow(),
        )
        db.insert_quiz_session(session)
        return session
