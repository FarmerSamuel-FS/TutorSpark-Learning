from __future__ import annotations

from typing import List, Optional

import db
from hero_art import get_hero_art
from input_helpers import is_back_choice, read_menu_choice
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


def _print_tutorspark_startup_intro() -> None:
    title = [
        "TTTTT U   U TTTTT  OOO  RRRR   SSS  PPPP    A   RRRR  K  K",
        "  T   U   U   T   O   O R   R S     P   P  A A  R   R K K ",
        "  T   U   U   T   O   O RRRR   SSS  PPPP  AAAAA RRRR  KK  ",
        "  T   U   U   T   O   O R  R      S P     A   A R  R  K K ",
        "  T    UUU    T    OOO  R   R SSSS  P     A   A R   R K  K",
    ]
    print()
    for line in title:
        print(color(line, CYAN, BOLD))
    _print_boxed(
        [
            "An interactive RPG learning application for curious adventurers.",
            "Load a saved hero or create a new one to begin your quest.",
            "Choose a subject path, answer challenge prompts, and use lifelines wisely.",
            "After the final survey, TutorSpark unlocks your custom quest story reward.",
        ]
    )


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


def show_hero_card(profile: LearnerProfile) -> None:
    """Show the active hero's art and profile details."""
    _hero_story(profile.hero_class, profile.name)
    _print_boxed(
        [
            f"Active hero: {profile.name} the {profile.hero_class}",
            f"Level: {profile.level}",
            f"Training path: {profile.focus_area}",
        ]
    )


# === Hero selection ==========================================================

def _choose_hero_class(name: str, allow_back: bool = False) -> Optional[str]:
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
        if allow_back:
            print(color("Esc) Back", GREEN), " – Return to the previous menu.")

        prompt = "\nEnter 1–4 to preview your hero"
        if allow_back:
            prompt += " or Esc to go back"
        choice = read_menu_choice(color(f"{prompt}: ", YELLOW))
        if allow_back and is_back_choice(choice):
            return None
        if choice not in mapping:
            msg = "Invalid choice. Please enter 1, 2, 3, or 4"
            if allow_back:
                msg += ", or Esc"
            print(color(f"{msg}.", RED))
            continue

        hero_class = mapping[choice]

        # Show avatar + lore for this class
        _hero_story(hero_class, name)

        confirm = read_menu_choice(
            color(
                "\nLock in this hero? (Y to confirm, anything else to choose again): ",
                YELLOW,
            )
        ).lower()

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


# === User profile creation / loading ========================================


def _create_new_profile(allow_back: bool = False) -> Optional[LearnerProfile]:
    print(color("Welcome to TutorSpark CLI! Let's create your user profile.\n", CYAN))

    name = input(color("Hero name: ", YELLOW)).strip() or "User"
    hero_class = _choose_hero_class(name, allow_back=allow_back)
    if hero_class is None:
        print(color("User profile creation cancelled. Returning to the previous menu.", GREEN))
        return None
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

    print(color(f"\nUser profile created. Welcome, {name} the {hero_class}!", CYAN, BOLD))
    return profile


def _print_save_slot_leaderboard() -> None:
    rows = db.get_leaderboard(limit=5)
    print(color("\n=== Current Leaderboard ===", BOLD))
    if not rows:
        print(color("No quest scores recorded yet. Start a quest to create leaderboard data.", YELLOW))
        return

    for rank, row in enumerate(rows, start=1):
        print(
            color(
                f"{rank}) {row['name']} the {row['hero_class']} | "
                f"Best {row['best_score']:.0f}% | Avg {row['average_score']:.0f}% | "
                f"Sessions {row['session_count']}",
                CYAN,
            )
        )


def load_or_create_profile() -> LearnerProfile:
    """
    If a user profile exists, let the user continue or start a new game.
    Otherwise, create a new hero user profile.
    """
    profiles = db.get_all_profiles()
    _print_tutorspark_startup_intro()

    if not profiles:
        profile = _create_new_profile()
        if profile is None:
            raise RuntimeError("A user profile is required to start TutorSpark CLI.")
        return profile

    print(color("\n=== TutorSpark Save Slot ===", BOLD))
    _print_save_slot_leaderboard()
    print(color("\n=== Choose Hero Profile ===", BOLD))
    for idx, saved_profile in enumerate(profiles, start=1):
        print(
            color(
                f"{idx}) Continue as {saved_profile.name} the {saved_profile.hero_class}",
                GREEN,
            )
        )
    create_choice = len(profiles) + 1
    reset_choice = len(profiles) + 2
    print(color(f"{create_choice}) Create a new user profile.", CYAN))
    print(color(f"{reset_choice}) Reset all local data.", YELLOW))
    print(color("Esc) Back / choose again.", GREEN))

    while True:
        choice = read_menu_choice(color(f"Choose 1-{reset_choice}, or Esc: ", YELLOW))
        if is_back_choice(choice):
            print(color("Still at save slot. Choose a user profile or option when ready.", GREEN))
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            existing = profiles[int(choice) - 1]
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
        if choice == str(create_choice):
            new_profile = _create_new_profile(allow_back=True)
            if new_profile is not None:
                return new_profile
            continue
        if choice == str(reset_choice):
            confirm = read_menu_choice(
                color(
                    "This will erase all local heroes, quiz history, and study data. "
                    "Type 'RESET' to confirm or anything else to cancel: ",
                    RED,
                )
            )
            if confirm == "RESET":
                db.reset_all_data()
                new_profile = _create_new_profile()
                if new_profile is None:
                    raise RuntimeError("A user profile is required after resetting TutorSpark CLI.")
                return new_profile
            else:
                print(color("Reset cancelled.", GREEN))
                continue
        print(color(f"Invalid choice. Please enter 1-{reset_choice}, or Esc.", RED))


def manage_hero_selection(profile: LearnerProfile) -> LearnerProfile:
    """
    Let the user view the active hero or reset into the hero creator.
    Returns the active user profile, which may be a newly created hero.
    """
    while True:
        print(color("\n=== User Profile Selection ===", BOLD))
        print(color("1) View current hero", CYAN))
        print(color("2) Switch user profile", CYAN))
        print(color("3) Create a new user profile", YELLOW))
        print(color("4) Reset all local data", RED))
        print(color("5) Return to main menu", GREEN))

        choice = read_menu_choice(color("Choose 1, 2, 3, 4, or 5: ", YELLOW))
        if choice == "1":
            show_hero_card(profile)
            continue
        if choice == "2":
            profiles = db.get_all_profiles()
            if not profiles:
                print(color("No saved user profiles found. Create a new user first.", YELLOW))
                continue
            for idx, saved_profile in enumerate(profiles, start=1):
                print(f"{idx}) {saved_profile.name} the {saved_profile.hero_class}")
            print("Esc) Back")
            selection = read_menu_choice(color("Select user number or Esc to go back: ", YELLOW))
            if is_back_choice(selection):
                continue
            if selection.isdigit() and 1 <= int(selection) <= len(profiles):
                return profiles[int(selection) - 1]
            print(color("Invalid user selection.", RED))
            continue
        if choice == "3":
            new_profile = _create_new_profile(allow_back=True)
            if new_profile is not None:
                return new_profile
            continue
        if choice == "4":
            confirm = read_menu_choice(
                color(
                    "This will erase all local heroes, quiz history, and study data. "
                    "Type 'RESET' to confirm or anything else to cancel: ",
                    RED,
                )
            )
            if confirm == "RESET":
                db.reset_all_data()
                new_profile = _create_new_profile()
                if new_profile is None:
                    raise RuntimeError("A user profile is required after resetting TutorSpark CLI.")
                return new_profile
            print(color("Reset cancelled.", GREEN))
            continue
        if choice == "5":
            return profile
        print(color("Invalid choice. Please enter 1, 2, 3, 4, or 5.", RED))
