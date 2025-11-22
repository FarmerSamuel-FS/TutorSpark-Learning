from __future__ import annotations

from typing import List

import db
from hero_art import get_hero_art
from models import LearnerProfile

# === ANSI color constants ====================================================

RESET = "\033[0m"
BOLD = "\033[1m"

FG_BLACK = "\033[30m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"

# Short aliases
RED = FG_RED
GREEN = FG_GREEN
YELLOW = FG_YELLOW
BLUE = FG_BLUE
MAGENTA = FG_MAGENTA
CYAN = FG_CYAN
WHITE = FG_WHITE


def color(text: str, *styles: str) -> str:
    if not styles:
        return text
    return "".join(styles) + text + RESET


def _print_boxed(lines: List[str]) -> None:
    if not lines:
        return
    width = max(len(line) for line in lines)
    border = "+" + "-" * (width + 2) + "+"
    print("\n" + border)
    for line in lines:
        print(f"| {line.ljust(width)} |")
    print(border)


# === Hero stories + art ======================================================


def _hero_story(hero_class: str, name: str) -> None:
    """Show big colored ASCII art plus a short lore box."""
    hc = hero_class.lower()

    if hc == "warrior":
        lines = [
            f"{name}, the {hero_class} of Stackville,",
            "raised on logic puzzles and late-night coding sessions,",
            "now stands ready to smash bugs and conquer basic CS monsters.",
            "High HP, forgiving difficulty – perfect for warming up.",
        ]
        box_color = RED
    elif hc == "mage":
        lines = [
            f"{name}, the {hero_class} of Algorithmia,",
            "weaves spells of recursion and dynamic programming,",
            "trading some defense for deeper insight and trickier battles.",
            "Balanced HP, strong hint magic.",
        ]
        box_color = MAGENTA
    elif hc == "healer":
        lines = [
            f"{name}, the {hero_class} of Debug Bay,",
            "keeps teammates alive with careful test suites and code reviews,",
            "facing tougher foes but recovering from mistakes with grace.",
            "Lower HP, advanced questions – but powerful recovery tools.",
        ]
        box_color = GREEN
    else:  # NEO PRO
        lines = [
            f"{name}, the {hero_class} of Code Nexus,",
            "a legendary hybrid warrior-mage-healer,",
            "seeks the toughest challenges with minimal lifelines.",
            "Lower HP, fewer assists – designed for advanced players.",
        ]
        box_color = CYAN

    ascii_art = get_hero_art(hero_class)
    print("\n" + ascii_art + "\n")

    print(color("", box_color), end="")
    _print_boxed(lines)
    print(RESET, end="")


# === Hero selection ==========================================================

def _choose_hero_class(name: str) -> str:
    """
    Let the player preview each class's avatar + story, then lock in.
    """
    mapping = {
        "1": "Warrior",
        "2": "Mage",
        "3": "Healer",
        "4": "NEO PRO",
    }

    while True:
        print()
        print(color("Choose your hero class:", BOLD))
        print(color("1) Warrior ", RED), " – Beginner: high HP, more forgiving.")
        print(color("2) Mage   ", MAGENTA), " – Intermediate: balanced HP, extra hint power.")
        print(color("3) Healer ", GREEN), " – Advanced: trickier fights, but strong support skills.")
        print(color("4) NEO PRO", CYAN), " – Expert: low HP, minimal lifelines, max challenge.")

        choice = input(color("\nEnter 1–4 to preview your hero: ", YELLOW)).strip()
        if choice not in mapping:
            print(color("Invalid choice. Please enter 1, 2, 3, or 4.", RED))
            continue

        hero_class = mapping[choice]

        # Show avatar + lore for this class
        _hero_story(hero_class, name)

        confirm = input(
            color(
                "\nLock in this hero? (Y to confirm, anything else to choose again): ",
                YELLOW,
            )
        ).strip().lower()

        if confirm == "y":
            return hero_class


def _default_level_for_class(hero_class: str) -> str:
    hc = hero_class.lower()
    if hc == "warrior":
        return "Beginner"
    if hc == "mage":
        return "Intermediate"
    if hc == "healer":
        return "Advanced"
    return "Expert"


# Auto-focus per hero class
HERO_FOCUS_MAP = {
    "warrior": "CS Fundamentals (Beginner)",
    "mage": "Algorithms & Problem Solving",
    "healer": "Testing & Software Quality",
    "neo pro": "Systems & Advanced CS",
}


def _focus_for_hero_class(hero_class: str) -> str:
    return HERO_FOCUS_MAP.get(hero_class.lower(), "CS Fundamentals")


# === Profile creation / loading =============================================


def _create_new_profile() -> LearnerProfile:
    print(color("Welcome to TutorSpark CLI! Let's create your learner profile.\n", CYAN))

    name = input(color("Hero name: ", YELLOW)).strip() or "Learner"
    hero_class = _choose_hero_class(name)
    level = _default_level_for_class(hero_class)

    # No menu: focus is implied by hero class
    focus = _focus_for_hero_class(hero_class)
    print(color(f"\nYour training path: {focus}", CYAN))

    profile = LearnerProfile(
        id=None,
        name=name,
        level=level,
        focus_area=focus,
        hero_class=hero_class,
    )
    profile = db.insert_profile(profile)

    print(color(f"\nProfile created. Welcome, {name} the {hero_class}!", CYAN, BOLD))
    return profile


def load_or_create_profile() -> LearnerProfile:
    """
    If a profile exists, let the user Continue or start a New Game.
    Otherwise, create a new hero profile.
    """
    existing = db.load_single_profile()

    if existing is None:
        return _create_new_profile()

    print(color("\n=== TutorSpark Save Slot ===", BOLD))
    print(
        color(
            f"1) Continue as {existing.name} the {existing.hero_class}",
            GREEN,
        )
    )
    print(color("2) Start a new hero (this resets your progress).", YELLOW))

    while True:
        choice = input(color("Choose 1 or 2: ", YELLOW)).strip()
        if choice == "1":
            # Make sure focus stays consistent with hero class if you tweak mapping later
            if not existing.focus_area:
                existing.focus_area = _focus_for_hero_class(existing.hero_class)
            print(
                color(
                    f"\nWelcome back to TutorSpark CLI, {existing.name} "
                    f"({existing.hero_class}, {existing.level} – {existing.focus_area}).",
                    CYAN,
                )
            )
            return existing
        if choice == "2":
            confirm = input(
                color(
                    "This will erase your current hero and quiz history. "
                    "Type 'RESET' to confirm or anything else to cancel: ",
                    RED,
                )
            ).strip()
            if confirm == "RESET":
                db.reset_all_data()
                return _create_new_profile()
            else:
                print(color("Reset cancelled. Continuing with existing hero.", GREEN))
                return existing
        print(color("Invalid choice. Please enter 1 or 2.", RED))
