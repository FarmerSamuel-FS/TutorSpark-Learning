from __future__ import annotations

from typing import List

import db
from models import LearnerProfile

# === ANSI color constants ===
RESET   = "\033[0m"
BOLD    = "\033[1m"

FG_BLACK   = "\033[30m"
FG_RED     = "\033[31m"
FG_GREEN   = "\033[32m"
FG_YELLOW  = "\033[33m"
FG_BLUE    = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN    = "\033[36m"
FG_WHITE   = "\033[37m"

# Short aliases used in the rest of the file
RED     = FG_RED
GREEN   = FG_GREEN
YELLOW  = FG_YELLOW
BLUE    = FG_BLUE
MAGENTA = FG_MAGENTA
CYAN    = FG_CYAN
WHITE   = FG_WHITE


def color(text: str, *styles: str) -> str:
    if not styles:
        return text
    return "".join(styles) + text + RESET


# === Small text UI helpers ===================================================

def _print_boxed(lines: List[str]) -> None:
    if not lines:
        return
    width = max(len(line) for line in lines)
    border = "+" + "-" * (width + 2) + "+"
    print("\n" + border)
    for line in lines:
        print(f"| {line.ljust(width)} |")
    print(border)


def _ascii_for_class(hero_class: str) -> str:
    """
    Returns a little ASCII hero graphic for the chosen class.
    Kept small so it looks good in a terminal.
    """
    hc = hero_class.lower()

    if hc == "warrior":
        # Tiny knight with sword
        return r"""
          /> 
         /<\ 
        /^^^\ 
       | 0 0 |
       |_==_|__
         /||\
        /_||_\
          /\
         /  \
        """

    if hc == "mage":
        # Robed caster with staff
        return r"""
           /\ 
          /  \ 
         / /\ \ 
        /_/  \_\ 
          (  )
         /|/\|
        /_||||\
          /__\
           /\
        """

    if hc == "healer":
        # Heart + healing staff vibe
        return r"""
        .-''''-.
       /  .-.  \
      |  /   \  |
      |  \___/  |
       \       /
        `-._.-'
          ||
        __||__
       /  ++  \
       \______/
        """

    # NEO PRO – techy terminal hero
    return r"""
        _____________
       |  TUTORSPARK |
       |-------------|
       |  > _        |
       |             |
       |   CS  PRO   |
       |_____________|
           /|\
          /_|_\
        """


def _hero_story(hero_class: str, name: str) -> None:
    hc = hero_class.lower()

    if hc == "warrior":
        lines = [
            f"{name}, the {hero_class} of Stackville,",
            "raised on logic puzzles and late-night coding sessions,",
            "now stands ready to smash bugs and conquer basic CS monsters.",
            "High HP, forgiving difficulty – perfect for warming up.",
        ]
        art_color = RED
    elif hc == "mage":
        lines = [
            f"{name}, the {hero_class} of Algorithmia,",
            "weaves spells of recursion and dynamic programming,",
            "trading some defense for deeper insight and trickier battles.",
            "Balanced HP, strong hint magic.",
        ]
        art_color = MAGENTA
    elif hc == "healer":
        lines = [
            f"{name}, the {hero_class} of Debug Bay,",
            "keeps teammates alive with careful test suites and code reviews,",
            "facing tougher foes but recovering from mistakes with grace.",
            "Lower HP, advanced questions – but powerful recovery tools.",
        ]
        art_color = GREEN
    else:  # NEO PRO
        lines = [
            f"{name}, the {hero_class} of Code Nexus,",
            "a legendary hybrid warrior-mage-healer,",
            "seeks the toughest challenges with minimal lifelines.",
            "Lower HP, fewer assists – designed for advanced players.",
        ]
        art_color = CYAN

    ascii_art = _ascii_for_class(hero_class)

    # Show art first, then story box
    print(color(ascii_art, art_color, BOLD))
    _print_boxed(lines)


def _choose_hero_class() -> str:
    print()
    print(color("Choose your hero class:", BOLD))
    print(color("1) Warrior", RED), " – Beginner: high HP, more forgiving.")
    print(color("2) Mage   ", MAGENTA), " – Intermediate: balanced HP, extra hint power.")
    print(color("3) Healer ", GREEN), " – Advanced: trickier fights, but strong support skills.")
    print(color("4) NEO PRO", CYAN), " – Expert: low HP, minimal lifelines, max challenge.")

    mapping = {
        "1": "Warrior",
        "2": "Mage",
        "3": "Healer",
        "4": "NEO PRO",
    }

    while True:
        choice = input(color("Enter 1–4: ", YELLOW)).strip()
        if choice in mapping:
            return mapping[choice]
        print(color("Invalid choice. Please enter 1, 2, 3, or 4.", RED))


def _default_level_for_class(hero_class: str) -> str:
    hc = hero_class.lower()
    if hc == "warrior":
        return "Beginner"
    if hc == "mage":
        return "Intermediate"
    if hc == "healer":
        return "Advanced"
    return "Expert"


def _create_new_profile() -> LearnerProfile:
    print(color("Welcome to TutorSpark CLI! Let's create your learner profile.\n", CYAN))

    name = input(color("Hero name: ", YELLOW)).strip() or "Learner"
    hero_class = _choose_hero_class()
    level = _default_level_for_class(hero_class)

    focus = input(
        color("Primary focus area (e.g., Python Basics, Data Structures): ", YELLOW)
    ).strip()
    if not focus:
        focus = "Computer Science Fundamentals"

    profile = LearnerProfile(
        id=None,
        name=name,
        level=level,
        focus_area=focus,
        hero_class=hero_class,
    )
    profile = db.insert_profile(profile)

    _hero_story(hero_class, name)
    print(color(f"\nProfile created. Welcome, {name} the {hero_class}!", CYAN, BOLD))
    return profile


def load_or_create_profile() -> LearnerProfile:
    """
    If a profile exists, let the user Continue or start a New Game.
    Otherwise, create a new hero profile.
    """
    existing = db.load_single_profile()

    if existing is None:
        # No save file yet – create a new hero.
        return _create_new_profile()

    # We have an existing hero: offer Continue / New Game.
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
