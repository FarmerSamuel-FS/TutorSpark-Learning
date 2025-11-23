import db
from models import LearnerProfile


def test_learner_profile_dataclass_basic_fields():
    """
    Unit test: LearnerProfile correctly stores the fields we pass in.
    This validates the core data structure used across the app.
    """
    profile = LearnerProfile(
        id=None,
        name="Unit Test Hero",
        level="Intermediate",
        focus_area="Data Structures",
        hero_class="Mage",
    )

    assert profile.name == "Unit Test Hero"
    assert profile.level == "Intermediate"
    assert profile.focus_area == "Data Structures"
    assert profile.hero_class == "Mage"


def test_profile_persistence_round_trip(temp_db_path):
    """
    Integration test: insert a profile into SQLite and load it back.
    Ensures DB + model wiring is correct (id + hero_class persisted).
    The temp_db_path fixture points DB_PATH to a temporary file.
    """
    new_profile = LearnerProfile(
        id=None,
        name="Persistent Hero",
        level="Beginner",
        focus_area="Python Basics",
        hero_class="Warrior",
    )

    saved = db.insert_profile(new_profile)
    assert saved.id is not None

    loaded = db.load_single_profile()
    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.name == "Persistent Hero"
    assert loaded.hero_class == "Warrior"
