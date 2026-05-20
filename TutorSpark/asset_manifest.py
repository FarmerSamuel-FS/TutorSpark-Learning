from __future__ import annotations


HERO_ASSETS = {
    "Warrior": {
        "idle": "assets/frames/heroes/warrior/hero_warrior_idle_frame.png",
        "attack": "assets/frames/heroes/warrior/hero_warrior_attack_frame.png",
        "hurt": "assets/frames/heroes/warrior/hero_warrior_hurt_frame.png",
        "victory": "assets/frames/heroes/warrior/hero_warrior_victory_frame.png",
    },
    "Mage": {
        "idle": "assets/frames/heroes/mage/hero_mage_idle_frame.png",
        "attack": "assets/frames/heroes/mage/hero_mage_attack_frame.png",
        "hurt": "assets/frames/heroes/mage/hero_mage_hurt_frame.png",
        "victory": "assets/frames/heroes/mage/hero_mage_victory_frame.png",
    },
    "Healer": {
        "idle": "assets/frames/heroes/healer/hero_healer_idle_frame.png",
        "attack": "assets/frames/heroes/healer/hero_healer_attack_frame.png",
        "hurt": "assets/frames/heroes/healer/hero_healer_hurt_frame.png",
        "victory": "assets/frames/heroes/healer/hero_healer_victory_frame.png",
    },
    "NEO PRO": {
        "idle": "assets/frames/heroes/neo/hero_neo_idle_frame.png",
        "attack": "assets/frames/heroes/neo/hero_neo_attack_frame.png",
        "hurt": "assets/frames/heroes/neo/hero_neo_hurt_frame.png",
        "victory": "assets/frames/heroes/neo/hero_neo_victory_frame.png",
    },
}


SCENE_ASSETS = {
    "math": "assets/scenes/scene_math_numbergate_storybook.png",
    "science": "assets/scenes/scene_science_living_light_storybook.png",
    "history": "assets/scenes/scene_history_archive_hall_storybook.png",
    "tech": "assets/scenes/scene_tech_signal_grid_storybook.png",
    "computer_knowledge": "assets/scenes/scene_computer_knowledge_coding_dungeon_storybook.png",
}


ENEMY_ASSETS = {
    "Number Wraith": "assets/frames/enemies/number_wraith/enemy_number_wraith_idle_frame.png",
    "Lab Slime": "assets/frames/enemies/lab_slime/enemy_lab_slime_idle_frame.png",
    "Timeline Phantom": "assets/frames/enemies/timeline_phantom/enemy_timeline_phantom_idle_frame.png",
    "Glitch Imp": "assets/frames/enemies/glitch_imp/enemy_glitch_imp_idle_frame.png",
    "Sorting Slime": "assets/frames/enemies/sorting_slime/enemy_sorting_slime_idle_frame.png",
    "Queue Goblin": "assets/frames/enemies/queue_goblin/enemy_queue_goblin_idle_frame.png",
    "Syntax Sprite": "assets/frames/enemies/syntax_sprite/enemy_syntax_sprite_idle_frame.png",
    "Big-O Ogre": "assets/frames/enemies/big_o_ogre/enemy_big_o_ogre_idle_frame.png",
    "Regression Wraith": "assets/frames/enemies/regression_wraith/enemy_regression_wraith_idle_frame.png",
    "Merge Goblin": "assets/frames/enemies/merge_goblin/enemy_merge_goblin_idle_frame.png",
    "Logic Gremlin": "assets/frames/enemies/logic_gremlin/enemy_logic_gremlin_idle_frame.png",
}


TOPIC_ENEMIES = {
    "Arithmetic": "Number Wraith",
    "Fractions": "Number Wraith",
    "Geometry": "Number Wraith",
    "Algebra": "Number Wraith",
    "Data Literacy": "Number Wraith",
    "Life Science": "Lab Slime",
    "Earth Science": "Lab Slime",
    "Physical Science": "Lab Slime",
    "Space Science": "Lab Slime",
    "Scientific Method": "Lab Slime",
    "U.S. History": "Timeline Phantom",
    "World History": "Timeline Phantom",
    "Civics": "Timeline Phantom",
    "Geography": "Timeline Phantom",
    "Digital Literacy": "Glitch Imp",
    "Internet Safety": "Glitch Imp",
    "Hardware Basics": "Glitch Imp",
    "Software Basics": "Glitch Imp",
    "Productivity Tools": "Glitch Imp",
    "Algorithms": "Sorting Slime",
    "Data Structures": "Queue Goblin",
    "Programming Fundamentals": "Syntax Sprite",
    "Python": "Syntax Sprite",
    "OOP": "Syntax Sprite",
    "Complexity": "Big-O Ogre",
    "Software Engineering": "Regression Wraith",
    "Software Testing": "Regression Wraith",
    "Software Design": "Regression Wraith",
    "Version Control": "Merge Goblin",
}


SUBJECT_SCENES = {
    "basic_math": "math",
    "general_science": "science",
    "history_civics": "history",
    "digital_literacy": "tech",
    "internet_safety": "tech",
    "cs_fundamentals": "computer_knowledge",
    "algorithms_complexity": "computer_knowledge",
    "data_structures": "computer_knowledge",
    "python_programming": "computer_knowledge",
    "software_engineering": "computer_knowledge",
}


def get_enemy_for_topic(topic: str) -> str:
    return TOPIC_ENEMIES.get(topic, "Logic Gremlin")


def get_scene_for_subject(subject_key: str) -> str:
    scene_key = SUBJECT_SCENES.get(subject_key, "computer_knowledge")
    return SCENE_ASSETS[scene_key]
