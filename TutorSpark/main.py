from __future__ import annotations

import textwrap
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from profile import load_or_create_profile, manage_hero_selection

import db
from engine import AdaptiveEngine, BOLD, YELLOW, color
from input_helpers import is_back_choice, read_menu_choice
from models import ParticipantDemographic, StudySession, SurveyResponse, UsabilityEvent
from quiz import run_quest_for_profile
from question_bank import (
    SUBJECT_CATEGORIES,
    SUBJECT_QUIZZES,
    get_questions_for_subject,
    get_subject_title,
    get_subjects_for_category,
)
from quest_lore import build_story_gift, get_hero_subject_quest_title
from strategies import RandomStrategy

SURVEY_PROMPTS = [
    (
        "interface_clarity",
        "The interface was easy to understand.",
    ),
    (
        "support_helpfulness",
        "The hints and support tools helped me reason through the answers.",
    ),
    (
        "cognitive_load",
        "The tutoring flow felt manageable and not overwhelming.",
    ),
    (
        "trust",
        "I trusted the tutoring feedback during the session.",
    ),
    (
        "touch_readiness",
        "The controls and prompts would work well on a touchscreen.",
    ),
    (
        "topic_fit",
        "The subject/category choices matched what I expected to study.",
    ),
    (
        "engagement_level",
        "The quest kept me engaged during the session.",
    ),
    (
        "tutoring_effectiveness",
        "The tutoring condition helped me understand the material.",
    ),
    (
        "interaction_quality",
        "The interaction quality felt smooth and useful.",
    ),
]


def _print_story_scroll(story: str) -> None:
    lines: list[str] = []
    for raw_line in story.strip().splitlines():
        if raw_line.strip() == "=== Quest Story Gift ===":
            continue
        if not raw_line.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(raw_line, width=72) or [""])

    width = max((len(line) for line in lines), default=20)
    top = "+" + "=" * (width + 2) + "+"
    print("\n=== Quest Story Gift ===")
    print(top)
    for line in lines:
        print(f"| {line.ljust(width)} |")
    print(top)


def _choose_subject() -> str | None:
    categories = list(SUBJECT_CATEGORIES.items())
    print("\n=== Choose Learning Category ===")
    for idx, (_, category) in enumerate(categories, start=1):
        print(f"{idx}. {category['title']}")
    print("Esc. Back")

    while True:
        choice = read_menu_choice(f"Choose 1-{len(categories)} or Esc to go back: ")
        if is_back_choice(choice):
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            category_key, category = categories[int(choice) - 1]
            subjects = get_subjects_for_category(category_key)
            if len(subjects) == 1:
                return subjects[0][0]
            print(f"\n=== {category['title']} Subjects ===")
            for subject_idx, (_, subject) in enumerate(subjects, start=1):
                print(f"{subject_idx}. {subject['title']}")
            print("Esc. Back to categories")

            while True:
                subject_choice = read_menu_choice(
                    f"Choose 1-{len(subjects)} or Esc to go back: "
                )
                if is_back_choice(subject_choice):
                    break
                if subject_choice.isdigit() and 1 <= int(subject_choice) <= len(subjects):
                    return subjects[int(subject_choice) - 1][0]
                print(f"Invalid choice. Please enter 1-{len(subjects)} or Esc.")
            print("\n=== Choose Learning Category ===")
            for idx, (_, category) in enumerate(categories, start=1):
                print(f"{idx}. {category['title']}")
            print("Esc. Back")
            continue
        print(f"Invalid choice. Please enter 1-{len(categories)} or Esc.")


def _record_study_event(
    profile,
    study_session_id: int,
    event_type: str,
    detail: str,
    metadata: str = "study_mode=true",
) -> None:
    if profile.id is None:
        return
    db.insert_usability_event(
        UsabilityEvent(
            id=None,
            profile_id=profile.id,
            session_id=None,
            study_session_id=study_session_id,
            event_type=event_type,
            detail=detail,
            created_at=datetime.utcnow(),
            metadata=metadata,
        )
    )


def _print_progress_report(profile) -> None:
    if profile.id is None:
        print("\nNo saved user profile found yet. Start a quest to create progress data.")
        return

    summary = db.get_profile_progress_summary(profile.id)
    sessions = summary["recent_sessions"]
    event_counts = summary["usability_event_counts"]
    recent_events = db.get_recent_usability_events(profile.id, limit=5)

    print("\n=== TutorSpark Progress Report ===")
    print(f"Hero: {profile.name} the {profile.hero_class}")
    print(f"Level: {profile.level}")
    print(f"Focus: {profile.focus_area}")
    print(f"Sessions completed: {summary['session_count']}")
    print(f"Questions answered: {summary['total_questions']}")
    print(f"Correct answers: {summary['correct_answers']}")
    print(f"Average score: {summary['average_score']:.0f}%")
    print(f"Best score: {summary['best_score']:.0f}%")
    print(f"Average answer time: {summary['average_answer_seconds']:.1f}s")
    print(f"Slowest answer time: {summary['slowest_answer_seconds']:.1f}s")

    if event_counts:
        print("\nUsability event counts:")
        for event_type, count in event_counts.items():
            label = event_type.replace("_", " ").title()
            print(f"- {label}: {count}")

    if not sessions:
        print("\nNo quiz sessions recorded yet. Run a quest to generate analytics.")
        return

    print("\nRecent sessions:")
    for session in sessions:
        score = (
            (session.correct_answers / session.total_questions) * 100.0
            if session.total_questions > 0
            else 0.0
        )
        date_label = session.created_at.strftime("%Y-%m-%d %H:%M")
        print(
            f"- {date_label}: {session.topic} "
            f"{session.correct_answers}/{session.total_questions} ({score:.0f}%)"
        )

    if recent_events:
        print("\nRecent usability events:")
        for event in recent_events:
            date_label = event.created_at.strftime("%Y-%m-%d %H:%M")
            label = event.event_type.replace("_", " ").title()
            print(f"- {date_label}: {label} ({event.detail})")


def _print_leaderboard() -> None:
    rows = db.get_leaderboard(limit=10)
    print("\n=== TutorSpark Leaderboard ===")
    if not rows:
        print("No user profiles found yet.")
        return

    for rank, row in enumerate(rows, start=1):
        print(
            f"{rank}. {row['name']} the {row['hero_class']} | "
            f"Best: {row['best_score']:.0f}% | "
            f"Avg: {row['average_score']:.0f}% | "
            f"Sessions: {row['session_count']} | "
            f"Correct: {row['correct_answers']}/{row['total_questions']}"
        )


def _run_dojo_practice() -> None:
    subject_key = _choose_subject()
    if subject_key is None:
        print("Dojo Practice Run cancelled. Returning to main menu.")
        return

    questions = get_questions_for_subject(subject_key)
    print(f"\n=== Dojo Practice Run: {get_subject_title(subject_key)} ===")
    print("Study these prompts with the correct answers before the quest battle.")
    if not questions:
        print("No practice questions available for this subject yet.")
        return

    for number, question in enumerate(questions, start=1):
        correct_answer = question.options[question.correct_index]
        print(f"\n{number}. [{question.topic}] {question.prompt}")
        print(f"   Correct answer: {correct_answer}")

    print("\nDojo complete. Start a subject quiz when you are ready for a randomized battle run.")


def _ask_post_task_survey(profile, study_session_id: int) -> None:
    if profile.id is None:
        return

    print("\n=== Post-Quest Usability Survey ===")
    print("Rate each item from 1 (strongly disagree) to 5 (strongly agree).")

    responses: list[SurveyResponse] = []
    for question_key, prompt in SURVEY_PROMPTS:
        while True:
            raw = read_menu_choice(f"{prompt} [1-5]: ")
            if raw in {"1", "2", "3", "4", "5"}:
                rating = int(raw)
                break
            print("Please enter a number from 1 to 5.")

        responses.append(
            SurveyResponse(
                id=None,
                study_session_id=study_session_id,
                profile_id=profile.id,
                question_key=question_key,
                prompt=prompt,
                rating=rating,
                created_at=datetime.utcnow(),
            )
        )

    db.insert_survey_responses(responses)
    print("Survey responses saved for usability analysis.")


def _ask_participant_demographics(profile, study_session_id: int) -> None:
    if profile.id is None:
        return

    print("\n=== Anonymous Participant Background ===")
    print("Use broad ranges only. Do not enter names, email addresses, or private details.")
    age_range = read_menu_choice("Age range (under 18, 18-24, 25-34, 35-44, 45+): ").strip()
    learning_background = read_menu_choice(
        "Learning background (K-12, college, self-taught, professional, other): "
    ).strip()
    cs_experience = read_menu_choice(
        "Computer/CS experience (none, beginner, intermediate, advanced): "
    ).strip()
    primary_device = read_menu_choice(
        "Primary device used today (laptop, desktop, phone, tablet, Raspberry Pi touchscreen): "
    ).strip()
    accessibility_needs = read_menu_choice(
        "Any accessibility notes for the interface? Type none if not applicable: "
    ).strip()
    open_feedback = read_menu_choice(
        "Any comments about the TutorSpark experience? Type none if not applicable: "
    ).strip()
    frustration_notes = read_menu_choice(
        "Was anything confusing, frustrating, or hard to use? Type none if not applicable: "
    ).strip()
    positive_notes = read_menu_choice(
        "What did you like, or what worked well? Type none if not applicable: "
    ).strip()

    db.insert_participant_demographic(
        ParticipantDemographic(
            id=None,
            study_session_id=study_session_id,
            profile_id=profile.id,
            age_range=age_range or "not provided",
            learning_background=learning_background or "not provided",
            cs_experience=cs_experience or "not provided",
            primary_device=primary_device or "not provided",
            accessibility_needs=accessibility_needs or "none",
            created_at=datetime.utcnow(),
            open_feedback=open_feedback or "none",
            frustration_notes=frustration_notes or "none",
            positive_notes=positive_notes or "none",
        )
    )
    print("Anonymous participant background saved.")


def _print_study_metrics(study_session_id: int) -> None:
    metrics = db.get_study_metrics(study_session_id)
    print("\n=== Study Session Metrics ===")
    print(f"Events captured: {metrics['event_count']}")
    print(f"Answers submitted: {metrics['answer_count']}")
    print(f"Accuracy rate: {metrics['accuracy_rate'] * 100:.0f}%")
    print(f"Support uses: {metrics['support_count']}")
    print(f"Support usage rate: {metrics['support_usage_rate'] * 100:.0f}%")
    print(f"Retry prompts: {metrics['retry_count']}")
    print(f"Reflection prompts: {metrics['reflection_count']}")
    print(f"Average answer time: {metrics['average_answer_seconds']:.1f}s")
    print(f"Average survey rating: {metrics['average_survey_rating']:.1f}/5")


def _run_subject_quiz_study(engine: AdaptiveEngine, profile) -> None:
    if profile.id is None:
        print("\nNo saved user profile found yet. Create a hero before starting a quest.")
        return

    participant_code = db.next_participant_code()
    subject_key = _choose_subject()
    if subject_key is None:
        print("Subject quiz cancelled. Returning to main menu.")
        return
    tutoring_condition = "constrained"
    subject_title = SUBJECT_QUIZZES[subject_key]["title"]
    quest_title = get_hero_subject_quest_title(profile, subject_key)
    task_name = f"{quest_title} Week 3 HCI quest"
    study = StudySession(
        id=None,
        profile_id=profile.id,
        participant_code=participant_code,
        task_name=task_name,
        started_at=datetime.utcnow(),
    )
    study_session_id = db.insert_study_session(study)

    print("\n=== TutorSpark Quest Study ===")
    print(f"Anonymous participant code: {participant_code}")
    print(f"Hero quest: {quest_title}")
    print(f"Task: complete one {subject_title} quest, then finish the short survey.")
    print("Your actions, timing, support use, and survey answers will be logged locally for Week 3 HCI analysis.")

    condition_metadata = f"study_mode=true; tutoring_condition={tutoring_condition}"
    _record_study_event(
        profile,
        study_session_id,
        "study_started",
        f"participant={participant_code}; condition={tutoring_condition}",
        metadata=condition_metadata,
    )
    _record_study_event(profile, study_session_id, "task_started", task_name, metadata=condition_metadata)

    session = run_quest_for_profile(
        engine,
        profile,
        study_session_id=study_session_id,
        subject_key=subject_key,
        tutoring_condition=tutoring_condition,
    )

    _record_study_event(
        profile,
        study_session_id,
        "task_completed",
        f"quiz_session_id={session.id}; score={session.correct_answers}/{session.total_questions}; condition={tutoring_condition}",
        metadata=condition_metadata,
    )
    print("\nQuest battle complete. Finish the survey to unlock your RPG story reward.")
    _ask_participant_demographics(profile, study_session_id)
    _ask_post_task_survey(profile, study_session_id)
    db.complete_study_session(study_session_id)
    _record_study_event(
        profile,
        study_session_id,
        "study_completed",
        f"participant={participant_code}; condition={tutoring_condition}",
        metadata=condition_metadata,
    )
    _print_story_scroll(
        build_story_gift(
            profile,
            subject_key,
            session.correct_answers,
            session.total_questions,
            participant_code=participant_code,
        )
    )
    _print_study_metrics(study_session_id)


def _export_usability_csv(profile) -> None:
    if profile.id is None:
        print("\nNo saved user profile found yet. Run a quest before exporting study data.")
        return

    safe_name = "".join(ch for ch in profile.name.lower() if ch.isalnum()) or "participant"
    output_dir = (
        Path.home()
        / "Desktop"
        / f"TutorSpark_Week3_HCI_Data_{safe_name}"
    )
    paths = db.export_study_bundle_csv(profile.id, output_dir)
    print("\nWeek 3 HCI study CSV bundle exported:")
    for label, path in paths.items():
        print(f"- {label.title()}: {path}")


def _export_week3_analysis_bundle() -> None:
    script_path = Path(__file__).resolve().parent / "scripts" / "week3_collect_analyze.py"
    subprocess.run([sys.executable, str(script_path)], check=True)


def main() -> None:
    # Ensure DB schema exists
    db.init_db()

    # Load or create user profile
    profile = load_or_create_profile()

    # Choose a question selection strategy and create the engine once
    strategy = RandomStrategy()
    engine = AdaptiveEngine(strategy)

    # Simple menu
    while True:
        print(color("=== TutorSpark CLI - Week 3 HCI Build ===", YELLOW, BOLD))
        print("1. Start subject quiz")
        print("2. Dojo Practice Run")
        print("3. View/select user profile")
        print("4. View progress report")
        print("5. View leaderboard")
        print("6. Export usability study CSV")
        print("7. Export Week 3 analysis bundle")
        print("8. Exit")

        choice = read_menu_choice("Choose an option: ")

        if choice == "1":
            _run_subject_quiz_study(engine, profile)
        elif choice == "2":
            _run_dojo_practice()
        elif choice == "3":
            profile = manage_hero_selection(profile)
        elif choice == "4":
            _print_progress_report(profile)
        elif choice == "5":
            _print_leaderboard()
        elif choice == "6":
            _export_usability_csv(profile)
        elif choice == "7":
            _export_week3_analysis_bundle()
        elif choice == "8":
            print("Goodbye, and good luck with your studies!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, or 8.")


if __name__ == "__main__":
    main()
