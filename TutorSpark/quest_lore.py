from __future__ import annotations

from models import LearnerProfile
from question_bank import SUBJECT_QUIZZES, get_subject_title


HERO_SUBJECT_QUESTS = {
    "warrior": {
        "basic_math": "Shield Count at Numbergate",
        "general_science": "The Trial of Living Light",
        "history_civics": "Banner Oath of the First Council",
        "digital_literacy": "The Device Armory Drill",
        "internet_safety": "Gatewatch Against False Links",
        "cs_fundamentals": "Training Grounds of Code",
        "algorithms_complexity": "The Path-Splitter Arena",
        "data_structures": "Vaults of Ordered Storage",
        "python_programming": "Syntax Sword Forms",
        "software_engineering": "The Refactor Keep",
    },
    "mage": {
        "basic_math": "Runes of Balance",
        "general_science": "Circle of Elements",
        "history_civics": "Chronicle Hall of Echoes",
        "digital_literacy": "The Signal Scriptorium",
        "internet_safety": "Wards of the Trusted Link",
        "cs_fundamentals": "First Spells of Code",
        "algorithms_complexity": "The Recursive Spiral",
        "data_structures": "Crystal Archives of Order",
        "python_programming": "Python Grimoire Trial",
        "software_engineering": "The Pattern Forge",
    },
    "healer": {
        "basic_math": "Clinic of Careful Counts",
        "general_science": "Garden of Cause and Cure",
        "history_civics": "Archive of Community Memory",
        "digital_literacy": "The Helpful Tools Ward",
        "internet_safety": "Sanctuary of Safe Signals",
        "cs_fundamentals": "Foundations of Clear Thinking",
        "algorithms_complexity": "Triage of Many Paths",
        "data_structures": "Shelves of Steady Order",
        "python_programming": "Remedy Scripts Lab",
        "software_engineering": "Regression Recovery Ward",
    },
    "neo pro": {
        "basic_math": "Quantum Count Protocol",
        "general_science": "Systems Scan of Matter",
        "history_civics": "Timeline Integrity Mission",
        "digital_literacy": "Interface Command Deck",
        "internet_safety": "Zero-Trust Link Sweep",
        "cs_fundamentals": "Core Logic Boot Sequence",
        "algorithms_complexity": "Optimization Grid Run",
        "data_structures": "Memory Array Deep Dive",
        "python_programming": "Runtime Command Trial",
        "software_engineering": "Production Readiness Run",
    },
}


HERO_MOTIFS = {
    "warrior": {
        "role": "steadfast Warrior",
        "opening": "lifted a book-shaped shield and crossed the bright gate",
        "method": "met each challenge one step at a time, turning careful choices into steady progress",
        "ally": "The shield glowed whenever the path became clearer.",
        "gift": "a steel-marked quest badge",
    },
    "mage": {
        "role": "curious Mage",
        "opening": "opened a field journal of bright runes and followed the first spark of the trail",
        "method": "looked for patterns, tested ideas, and shaped each answer like a helpful spell",
        "ally": "The journal shimmered when a hidden pattern came into view.",
        "gift": "a page of glowing quest notes",
    },
    "healer": {
        "role": "patient Healer",
        "opening": "entered the study ward with a lantern of calm light",
        "method": "used each answer to restore clarity, confidence, and a little more courage",
        "ally": "The lantern warmed the room whenever a lesson started to make sense.",
        "gift": "a care-sealed quest record",
    },
    "neo pro": {
        "role": "focused NEO PRO",
        "opening": "activated the command deck and watched the mission map come alive",
        "method": "scanned each prompt, tested the options, and adjusted course with focus",
        "ally": "The visor flashed whenever the next route became easier to read.",
        "gift": "a mission-grade quest log",
    },
}


SUBJECT_STAKES = {
    "basic_math": "At Numbergate, missing numbers had scattered across the stones, and the path forward opened only when the hero rebuilt the pattern.",
    "general_science": "In the Hall of Living Light, small discoveries powered the lamps that protected the village library.",
    "history_civics": "Inside the Archive of Echoes, old maps and community stories waited for someone to connect them with care.",
    "digital_literacy": "Across the Signal Grid, tools, screens, and messages needed a guide who could choose the right action.",
    "internet_safety": "At the Linkwatch Gate, safe choices kept the trail clear and helped future travelers avoid traps.",
    "cs_fundamentals": "In the Core Logic chamber, every clear idea helped the old machines wake up and work together.",
    "algorithms_complexity": "On the Path-Splitter floor, every decision changed the route, so the hero searched for the smartest way through.",
    "data_structures": "Deep in the Ordered Vaults, scattered treasures had to be stored where anyone could find them again.",
    "python_programming": "In the Python Lab, tiny commands became tools that could solve problems one line at a time.",
    "software_engineering": "At Refactor Keep, the hero repaired a working machine so it could stay strong for the next learner.",
}


SUBJECT_BATTLE_PLACES = {
    "basic_math": "the Numbergate platform",
    "general_science": "the Hall of Living Light",
    "history_civics": "the Archive of Echoes",
    "digital_literacy": "the Signal Grid",
    "internet_safety": "the Linkwatch Gate",
    "cs_fundamentals": "the Core Logic chamber",
    "algorithms_complexity": "the Path-Splitter floor",
    "data_structures": "the Ordered Vaults",
    "python_programming": "the Python Lab",
    "software_engineering": "Refactor Keep",
}


HERO_BATTLE_ACTIONS = {
    "warrior": "steps forward, shield raised, ready to turn a careful answer into a brave strike",
    "mage": "opens the rune journal, looking for the pattern hidden inside the challenge",
    "healer": "lifts the calm lantern, ready to restore the path with a thoughtful choice",
    "neo pro": "checks the visor display, scanning the prompt for the cleanest route ahead",
}


ENEMY_BATTLE_SCRIPTS = {
    "Number Wraith": "scatters glowing digits across the arena",
    "Lab Slime": "bubbles beside the experiment table and blocks the next discovery",
    "Timeline Phantom": "swirls through old maps and tries to blur the order of events",
    "Glitch Imp": "scrambles the signal panels with a burst of static",
    "Sorting Slime": "splits the path into messy routes that need a clear method",
    "Queue Goblin": "jumbles the waiting line of clues out of order",
    "Syntax Sprite": "darts around the code runes, hiding one important detail",
    "Big-O Ogre": "stomps onto the grid and challenges the hero to find the efficient path",
    "Regression Wraith": "shakes the repaired machine, testing whether the fix still holds",
    "Merge Goblin": "slides two paths together and dares the hero to keep the history clear",
    "Logic Gremlin": "twists the logic gate and waits for a precise answer",
}


def _hero_key(hero_class: str) -> str:
    return hero_class.strip().lower()


def get_hero_subject_quest_title(profile: LearnerProfile, subject_key: str) -> str:
    hero_key = _hero_key(profile.hero_class)
    titles = HERO_SUBJECT_QUESTS.get(hero_key, HERO_SUBJECT_QUESTS["warrior"])
    return titles.get(subject_key, get_subject_title(subject_key))


def get_subject_category_title(subject_key: str) -> str:
    subject = SUBJECT_QUIZZES.get(subject_key, {})
    category_key = subject.get("category", "computer_knowledge")
    return {
        "math": "Math",
        "science": "Science",
        "history": "History",
        "tech": "Tech",
        "computer_knowledge": "Computer Knowledge",
    }.get(category_key, "Computer Knowledge")


def build_battle_intro(
    profile: LearnerProfile,
    subject_key: str,
    quest_title: str,
    question_topic: str,
    enemy_name: str,
    question_number: int,
    total_questions: int,
) -> str:
    hero_key = _hero_key(profile.hero_class)
    hero_action = HERO_BATTLE_ACTIONS.get(hero_key, HERO_BATTLE_ACTIONS["warrior"])
    place = SUBJECT_BATTLE_PLACES.get(subject_key, "the quest arena")
    enemy_action = ENEMY_BATTLE_SCRIPTS.get(
        enemy_name,
        "guards the next clue and waits for a careful answer",
    )
    return (
        f"Encounter {question_number} of {total_questions}: During {quest_title}, "
        f"{profile.name} enters {place}. A {enemy_name} {enemy_action}. "
        f"{profile.name} {hero_action}. This {question_topic} challenge decides "
        "whether the path opens."
    )


def build_story_gift(
    profile: LearnerProfile,
    subject_key: str,
    correct_answers: int,
    total_questions: int,
    participant_code: str | None = None,
) -> str:
    hero_key = _hero_key(profile.hero_class)
    motif = HERO_MOTIFS.get(hero_key, HERO_MOTIFS["warrior"])
    quest_title = get_hero_subject_quest_title(profile, subject_key)
    subject_title = get_subject_title(subject_key)
    category_title = get_subject_category_title(subject_key)
    score_line = f"{correct_answers}/{total_questions}"
    participant_line = (
        f"Anonymous study code: {participant_code}\n"
        if participant_code
        else ""
    )

    if total_questions and correct_answers == total_questions:
        outcome = (
            "The final score was perfect, and every trial crystal lit up from start to finish."
        )
    elif total_questions and correct_answers >= max(1, int(total_questions * 0.7)):
        outcome = (
            "The final score showed strong progress, and most of the trial crystals stayed bright."
        )
    else:
        outcome = (
            "The final score became a useful map, showing exactly where practice can make the next run stronger."
        )

    stakes = SUBJECT_STAKES.get(
        subject_key,
        "The quest path asked for attention, patience, and a brave try from beginning to end.",
    )

    return (
        "\n=== Quest Story Gift ===\n"
        f"{participant_line}"
        f"Quest: {quest_title}\n"
        f"Hero: {profile.name} the {profile.hero_class}\n"
        f"Topic path: {category_title} / {subject_title}\n\n"
        f"{profile.name}, a {motif['role']}, {motif['opening']} for {quest_title}. "
        f"{stakes} The {subject_title} trials did not ask for perfection; they asked for "
        "attention, patience, and the courage to try the next prompt.\n\n"
        f"Through the adventure, {profile.name} {motif['method']}. {motif['ally']} "
        f"By the final prompt, the quest record showed {score_line}. {outcome}\n\n"
        f"As thanks for completing the survey, TutorSpark awards {profile.name} "
        f"{motif['gift']}. It is proof that this learning path was tested by a real user, "
        "and that the next traveler will have a clearer, friendlier adventure because of it."
    )
