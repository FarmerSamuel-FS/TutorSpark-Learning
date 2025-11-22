from __future__ import annotations

from profile import load_or_create_profile

import db
from engine import AdaptiveEngine
from quiz import run_quest_for_profile
from strategies import RandomStrategy


def main() -> None:
    # Ensure DB schema exists
    db.init_db()

    # Load or create learner profile
    profile = load_or_create_profile()

    # Choose a question selection strategy and create the engine once
    strategy = RandomStrategy()
    engine = AdaptiveEngine(strategy)

    # Simple menu
    while True:
        print("\n=== TutorSpark CLI – Milestone 1 ===")
        print("1. Start CS Fundamentals quest")
        print("2. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            run_quest_for_profile(engine, profile)
        elif choice == "2":
            print("Goodbye, and good luck with your studies!")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
