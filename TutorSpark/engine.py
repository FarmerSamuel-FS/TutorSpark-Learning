from __future__ import annotations

"""
engine.py

Core battle engine for TutorSpark CLI.

- Renders RPG-style battles for a *single* quiz run.
- Uses hero_class to set HP + lifelines.
- Shows quest titles (10-quest story per hero class).
- At the end of the run, records a QuizSession and marks which
  questions this hero has already seen in the DB.
"""

import os
import random
import textwrap
import time
from datetime import datetime
from typing import List, Set, Tuple

import db
from models import LearnerProfile, Question, QuizSession, UsabilityEvent
from quest_lore import build_battle_intro
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
    wrapped_lines: List[str] = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=68) or [""])
    width = max(len(line) for line in wrapped_lines)
    border = "+" + "-" * (width + 2) + "+"
    print("\n" + border)
    for line in wrapped_lines:
        print(f"| {line.ljust(width)} |")
    print(border)


def print_guardrail_notice() -> None:
    print_boxed(
        [
            "TutorSpark guardrails: supports reasoning before answers.",
            "Use H for a concept hint, F to reduce choices, C for a suggestion.",
            "The system logs support use and timing for usability review.",
        ]
    )


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


# === Quest story helpers =====================================================

QUEST_TITLES = {
    "warrior": [
        "Training Grounds",
        "Dungeon of Debugging",
        "The Stack Overflow Keep",
        "Refactor Ravine",
        "Merge Conflict Marsh",
        "The Big-O Arena",
        "Tower of Recursion",
        "Heapfire Citadel",
        "The Integration Gauntlet",
        "Final Boss: Legacy Code Dragon",
    ],
    "mage": [
        "Circle of Recursion",
        "Forest of Functions",
        "Lambda Labyrinth",
        "Memoization Monastery",
        "Graph Grove",
        "Dynamic Dungeon",
        "The Sorting Spire",
        "Complexity Crags",
        "The Compiler’s Court",
        "Final Boss: Runtime Wraith",
    ],
    "healer": [
        "Clinic of Unit Tests",
        "Ward of Assertions",
        "Coverage Cathedral",
        "Regression Ruins",
        "Refactor Refuge",
        "Sandbox Sanctuary",
        "Mockingbird Monastery",
        "Pipeline Infirmary",
        "On-Call Citadel",
        "Final Boss: Production Pager Storm",
    ],
    "neo pro": [
        "Bootloader Backstreets",
        "Kernel Crossroads",
        "Container Coliseum",
        "CI/CD Skyline",
        "Microservice Maze",
        "Concurrency Crossfire",
        "Distributed Dungeon",
        "Zero-Day Zone",
        "Code Nexus Summit",
        "Final Boss: The Infinite Loop",
    ],
}


def get_quest_number(profile: LearnerProfile) -> int:
    """
    Determine which quest this hero is on based on completed quiz sessions.
    completed=0 -> Quest 1, completed=1 -> Quest 2, etc.; clamped to 10.
    """
    if profile.id is None:
        return 1
    completed = db.count_quiz_sessions_for_profile(profile.id)
    return min(completed + 1, 10)


def get_quest_title(profile: LearnerProfile, quest_number: int) -> str:
    """Return the story title for the given hero and quest number (1–10)."""
    key = profile.hero_class.lower()
    titles = QUEST_TITLES.get(key, QUEST_TITLES["warrior"])
    idx = min(max(quest_number, 1), len(titles)) - 1
    return titles[idx]


# === Domain helpers (hints, grades, etc.) ===================================

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
    if any(key in topic_lower for key in ["arithmetic", "fraction", "geometry", "algebra", "data literacy"]):
        return "Number Wraith"
    if any(key in topic_lower for key in ["life science", "earth science", "physical science", "space science", "scientific method"]):
        return "Lab Slime"
    if any(key in topic_lower for key in ["u.s. history", "world history", "civics", "geography"]):
        return "Timeline Phantom"
    if any(key in topic_lower for key in ["digital literacy", "internet safety", "hardware", "software basics", "productivity"]):
        return "Glitch Imp"
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


def get_reflection_prompt(q: Question) -> str:
    prompts = {
        "Algorithms": "Which step in the algorithm changes the search space?",
        "Data Structures": "What access pattern does the problem describe?",
        "Programming Fundamentals": "Which language rule is the question testing?",
        "Complexity": "How does the work grow as the input gets larger?",
        "Software Engineering": "What behavior would help future developers trust the code?",
        "Version Control": "Which action changes local history versus remote history?",
    }
    return prompts.get(
        q.topic,
        "What clue in the question points toward the correct concept?",
    )


def apply_fifty_fifty(q: Question, hidden: Set[int]) -> str:
    """
    50/50 lifeline: hide two wrong options.
    """
    candidates = [
        i
        for i in range(len(q.options))
        if i != q.correct_index and i not in hidden
    ]
    if len(candidates) <= 1:
        return "50/50 can’t eliminate any more options."
    to_hide = set(random.sample(candidates, k=min(2, len(candidates))))
    hidden.update(to_hide)
    return "50/50 used: two incorrect options have been removed."


def hero_stats(profile: LearnerProfile) -> Tuple[int, int, int, int, int, int]:
    """
    Map hero_class to starting stats.

    Returns:
      max_hp, damage_on_hit, hints_left, fifty_fifty_left,
      calls_left, free_passes
    """
    hc = profile.hero_class.lower()

    if hc == "warrior":       # Beginner
        return 24, 3, 4, 2, 1, 0
    if hc == "mage":          # Intermediate
        return 20, 4, 5, 1, 1, 0
    if hc == "healer":        # Advanced
        return 18, 3, 3, 2, 1, 1
    if hc == "neo pro":       # Expert
        return 16, 5, 2, 1, 0, 0

    return 20, 4, 3, 2, 1, 0


# === Testable helpers for unit tests ========================================

def evaluate_answer(question: Question, chosen_index: int, current_hp: int) -> tuple[bool, int]:
    """
    Compare chosen answer to the correct index and update HP.

    Returns:
        (is_correct, new_hp)

    This is a small, pure function used by tests to validate answer logic
    without running the full interactive battle loop.
    """
    is_correct = (chosen_index == question.correct_index)
    if not is_correct:
        current_hp -= 1
    return is_correct, current_hp


def is_game_over(current_hp: int, remaining_questions: int) -> bool:
    """
    Game ends when HP is zero (or below) OR when there are no questions left.
    """
    return current_hp <= 0 or remaining_questions <= 0


# === Adaptive Engine ========================================================

class AdaptiveEngine:
    """
    AdaptiveEngine composes a QuestionSelectionStrategy.

    - Uses the chosen strategy to select questions from the bank.
    - Runs one full "quest" (quiz) with HP, lifelines, and XP.
    - Records the QuizSession and marks questions seen for this hero.
    """

    def __init__(self, selection_strategy: QuestionSelectionStrategy) -> None:
        self._selection_strategy = selection_strategy

    def run_quiz_session(
        self,
        profile: LearnerProfile,
        question_bank: List[Question],
        limit: int = 10,
        study_session_id: int | None = None,
        quest_topic: str = "CS Questline",
        quest_label: str | None = None,
        subject_key: str = "cs_fundamentals",
        tutoring_condition: str = "constrained",
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
        usability_events: List[UsabilityEvent] = []
        condition = tutoring_condition if tutoring_condition in {"constrained", "unconstrained"} else "constrained"
        support_enabled = condition == "constrained"

        def record_event(
            event_type: str,
            detail: str,
            question_id: int | None = None,
            elapsed_seconds: float | None = None,
            metadata: str | None = None,
        ) -> None:
            if profile.id is None:
                return
            usability_events.append(
                UsabilityEvent(
                    id=None,
                    profile_id=profile.id,
                    session_id=None,
                    event_type=event_type,
                    detail=detail,
                    created_at=datetime.utcnow(),
                    question_id=question_id,
                    elapsed_seconds=elapsed_seconds,
                    metadata=metadata,
                    study_session_id=study_session_id,
                )
            )

        max_hp, damage_on_hit, hints_left, fifty_fifty_left, calls_left, free_passes = hero_stats(profile)
        hp = max_hp

        quest_number = get_quest_number(profile)
        quest_title = quest_label or get_quest_title(profile, quest_number)

        clear_screen()
        print_banner("TutorSpark Training Grounds")
        print(color(f"Quest {quest_number}: {quest_title}", BOLD))
        print(
            color(
                f"Hero: {profile.name} the {profile.hero_class}  |  "
                f"Level: {profile.level}  |  Focus: {profile.focus_area}",
                CYAN,
            )
        )
        print(color(f"Starting HP: {render_bar(hp, max_hp, fill_char='❤')}", YELLOW))
        if support_enabled:
            print_guardrail_notice()
        else:
            print(
                color(
                    "Unconstrained run: answer directly. Hints, lifelines, and reflection prompts are hidden for comparison data.",
                    CYAN,
                )
            )

        record_event(
            "quest_started",
            f"quest={quest_number}; title={quest_title}; subject={quest_topic}; questions={total}; condition={condition}",
            metadata=f"hero_class={profile.hero_class}; level={profile.level}; tutoring_condition={condition}",
        )

        for idx, q in enumerate(selected, start=1):
            if hp <= 0:
                break

            enemy_name = enemy_name_for_topic(q.topic)
            hidden_indices: Set[int] = set()
            used_hint_this_question = False
            used_fifty_this_question = False
            used_friend_this_question = False
            question_started_at = time.perf_counter()

            while True:
                battle_intro = build_battle_intro(
                    profile,
                    subject_key,
                    quest_title,
                    q.topic,
                    enemy_name,
                    idx,
                    total,
                )
                print("\n" + "-" * 70)
                print(color(f"⚔️  Battle {idx}/{total}: A wild {enemy_name} appears!", BOLD))
                print(color(f"Topic: {q.topic}", CYAN))
                print(color(f"Path: {render_run_path(idx, total)}", CYAN))
                print(color(f"HP: {render_bar(hp, max_hp, fill_char='❤')}", YELLOW))
                if support_enabled:
                    print(
                        f"Streak: {current_streak}   "
                        f"Hints: {hints_left}   50/50: {fifty_fifty_left}   "
                        f"Call: {calls_left}   Free passes: {free_passes}"
                    )
                else:
                    print(f"Streak: {current_streak}   Support tools: unavailable in this condition")
                print("-" * 70)
                print_boxed([battle_intro])
                print(q.prompt)

                for opt_index, option in enumerate(q.options, start=1):
                    if opt_index - 1 in hidden_indices:
                        print(f"  {opt_index}. [eliminated]")
                    else:
                        print(f"  {opt_index}. {option}")

                if support_enabled:
                    print(
                        "\nChoose: 1–4 to answer, "
                        "H=Hint, F=50/50, C=Call a friend, P=Free pass"
                    )
                else:
                    print("\nChoose: 1–4 to answer")
                raw = input("Your move: ").strip().upper()

                is_correct = False
                used_free_pass = False

                if raw in {"1", "2", "3", "4"}:
                    answer_idx = int(raw) - 1
                    if answer_idx in hidden_indices:
                        print("That option has been eliminated. Pick another.")
                        record_event(
                            "guardrail_retry_prompted",
                            "learner_selected_eliminated_option",
                            question_id=q.id,
                            elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                        )
                        continue
                    is_correct = (answer_idx == q.correct_index)
                    break

                elif raw == "H":
                    if not support_enabled:
                        print("Hints are unavailable during this unconstrained study condition.")
                        record_event(
                            "support_unavailable",
                            f"battle={idx}; requested=hint; condition={condition}",
                            question_id=q.id,
                            elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                            metadata=f"tutoring_condition={condition}",
                        )
                        continue
                    if hints_left <= 0:
                        print("You have no hints left.")
                        continue
                    if used_hint_this_question:
                        print("You already used a hint on this question.")
                        continue
                    hints_left -= 1
                    used_hint_this_question = True
                    hint_text = get_hint_for_question(q)
                    record_event(
                        "hint_used",
                        f"battle={idx}",
                        question_id=q.id,
                        elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                        metadata=f"remaining_hints={hints_left}",
                    )
                    print(color(f"Hint: {hint_text}", CYAN))
                    print(
                        color(
                            "Guardrail check: try applying the hint before choosing an answer.",
                            CYAN,
                        )
                    )
                    continue

                elif raw == "F":
                    if not support_enabled:
                        print("50/50 is unavailable during this unconstrained study condition.")
                        record_event(
                            "support_unavailable",
                            f"battle={idx}; requested=fifty_fifty; condition={condition}",
                            question_id=q.id,
                            elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                            metadata=f"tutoring_condition={condition}",
                        )
                        continue
                    if fifty_fifty_left <= 0:
                        print("You have no 50/50 lifelines left.")
                        continue
                    if used_fifty_this_question:
                        print("You already used 50/50 on this question.")
                        continue
                    fifty_fifty_left -= 1
                    used_fifty_this_question = True
                    msg = apply_fifty_fifty(q, hidden_indices)
                    record_event(
                        "fifty_fifty_used",
                        f"battle={idx}; hidden={sorted(hidden_indices)}",
                        question_id=q.id,
                        elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                        metadata=f"remaining_fifty_fifty={fifty_fifty_left}",
                    )
                    print(color(msg, CYAN))
                    continue

                elif raw == "C":
                    if not support_enabled:
                        print("Call a friend is unavailable during this unconstrained study condition.")
                        record_event(
                            "support_unavailable",
                            f"battle={idx}; requested=call_friend; condition={condition}",
                            question_id=q.id,
                            elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                            metadata=f"tutoring_condition={condition}",
                        )
                        continue
                    if calls_left <= 0:
                        print("You have no calls left.")
                        continue
                    if used_friend_this_question:
                        print("You already called a friend for this question.")
                        continue
                    calls_left -= 1
                    used_friend_this_question = True
                    suggestion = friend_suggestion(q)
                    record_event(
                        "friend_call_used",
                        f"battle={idx}; suggestion={suggestion + 1}",
                        question_id=q.id,
                        elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                        metadata=f"remaining_calls={calls_left}",
                    )
                    print(
                        color(
                            f"📞 Your friend thinks the answer is option {suggestion + 1} "
                            "(but they might be wrong!).",
                            CYAN,
                        )
                    )
                    continue

                elif raw == "P":
                    if not support_enabled:
                        print("Free Pass is unavailable during this unconstrained study condition.")
                        record_event(
                            "support_unavailable",
                            f"battle={idx}; requested=free_pass; condition={condition}",
                            question_id=q.id,
                            elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                            metadata=f"tutoring_condition={condition}",
                        )
                        continue
                    if free_passes <= 0:
                        print("You don't have any free passes yet. "
                              "Earn them by getting answer streaks of 3.")
                        continue
                    free_passes -= 1
                    used_free_pass = True
                    is_correct = True
                    record_event(
                        "free_pass_used",
                        f"battle={idx}",
                        question_id=q.id,
                        elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                        metadata=f"remaining_free_passes={free_passes}",
                    )
                    print(color("You use a free pass and avoid taking damage!", GREEN))
                    break

                else:
                    print("Invalid choice. Try again.")
                    record_event(
                        "guardrail_retry_prompted",
                        f"invalid_input={raw or '<blank>'}",
                        question_id=q.id,
                        elapsed_seconds=round(time.perf_counter() - question_started_at, 2),
                    )
                    continue

            answer_elapsed = round(time.perf_counter() - question_started_at, 2)
            if is_correct:
                record_event(
                    "answer_submitted",
                    f"battle={idx}; correct=true",
                    question_id=q.id,
                    elapsed_seconds=answer_elapsed,
                    metadata=(
                        f"hint_used={used_hint_this_question}; "
                        f"fifty_fifty_used={used_fifty_this_question}; "
                        f"friend_call_used={used_friend_this_question}"
                    ),
                )
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
                record_event(
                    "answer_submitted",
                    f"battle={idx}; correct=false",
                    question_id=q.id,
                    elapsed_seconds=answer_elapsed,
                    metadata=(
                        f"hint_used={used_hint_this_question}; "
                        f"fifty_fifty_used={used_fifty_this_question}; "
                        f"friend_call_used={used_friend_this_question}"
                    ),
                )
                if support_enabled:
                    reflection_prompt = get_reflection_prompt(q)
                    record_event(
                        "reflection_prompted",
                        f"battle={idx}; prompt={reflection_prompt}",
                        question_id=q.id,
                        elapsed_seconds=answer_elapsed,
                        metadata=f"tutoring_condition={condition}",
                    )
                    print(color(f"Reflection prompt: {reflection_prompt}", CYAN))
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
            topic=f"Quest {quest_number} - {quest_topic}",
            total_questions=total,
            correct_answers=correct,
            created_at=datetime.utcnow(),
        )
        db.insert_quiz_session(session)

        if profile.id is not None:
            record_event(
                "quest_completed",
                (
                    f"score={correct}/{total}; grade={grade}; "
                    f"best_streak={best_streak}; xp={xp_earned}"
                ),
                metadata=(
                    f"tutoring_condition={condition}; "
                    + (
                        "guardrails=hint_before_answer,reflection_after_miss,invalid_input_retry"
                        if support_enabled
                        else "guardrails=none; support_tools=hidden"
                    )
                ),
            )
            for event in usability_events:
                event.session_id = session.id
            db.insert_usability_events(usability_events)

        if profile.id is not None and selected:
            db.mark_questions_seen(profile.id, [q.id for q in selected])

        return session
