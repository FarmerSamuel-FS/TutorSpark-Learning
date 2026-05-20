import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import LearnerProfile
from quest_lore import build_battle_intro, build_story_gift, get_hero_subject_quest_title


def make_profile(hero_class: str) -> LearnerProfile:
    return LearnerProfile(
        id=1,
        name="Test Hero",
        level="Participant",
        focus_area="Basic Math",
        hero_class=hero_class,
    )


def test_same_subject_gets_different_quest_titles_by_hero():
    warrior_title = get_hero_subject_quest_title(make_profile("Warrior"), "basic_math")
    mage_title = get_hero_subject_quest_title(make_profile("Mage"), "basic_math")

    assert warrior_title == "Shield Count at Numbergate"
    assert mage_title == "Runes of Balance"
    assert warrior_title != mage_title


def test_story_gift_includes_hero_quest_score_and_participant_code():
    profile = make_profile("Healer")

    story = build_story_gift(
        profile,
        "general_science",
        correct_answers=4,
        total_questions=5,
        participant_code="P001",
    )

    assert "Quest Story Gift" in story
    assert "Garden of Cause and Cure" in story
    assert "Test Hero the Healer" in story
    assert "4/5" in story
    assert "P001" in story


def test_battle_intro_links_hero_enemy_quest_and_topic():
    profile = make_profile("Warrior")

    intro = build_battle_intro(
        profile,
        "general_science",
        "The Trial of Living Light",
        "Life Science",
        "Lab Slime",
        question_number=2,
        total_questions=5,
    )

    assert "Encounter 2 of 5" in intro
    assert "Test Hero" in intro
    assert "The Trial of Living Light" in intro
    assert "Lab Slime" in intro
    assert "Life Science" in intro
