# TutorSpark CLI – Advanced Software Engineering Project (COS550)

TutorSpark CLI is a terminal-based, **RPG-flavored learning assistant** for Computer Science students.

You create a hero persona (Warrior, Mage, Healer, or NEO PRO) and battle through short CS quizzes as turn-based encounters. Under the hood, TutorSpark uses classic **software design patterns** and a simple **adaptive engine** to select questions and record progress to a local SQLite database.

This repository contains:

- The **TutorSpark CLI application** (in the `TutorSpark/` folder)
- Weekly **milestone deliverables** (in `milestones/` or similarly named folders), created for the COS550 Advanced Software Engineering course at Full Sail University.

---

## 1. Project Concept

**Application Title:** TutorSpark CLI  
**Goal:** Provide a lightweight, offline-friendly, gamified CLI that helps learners practice core CS topics (algorithms, data structures, complexity, software engineering, Python fundamentals).

Key ideas:

- Make practice **low-friction**: run from any terminal with Python installed.
- Integrate **software design patterns** (Strategy, etc.) as real, working code.
- Capture basic analytics in SQLite so the engine can become more adaptive over time.
- Wrap quizzes in a light **RPG “training grounds” theme** (HP, streaks, lifelines, hero classes).

---

## 2. Current Feature Set (Milestone 1)

Milestone 1 focuses on the **first playable slice** of the system:

- **Hero Profile System**

  - On first run, user creates a _Learner Profile_:
    - `name` – hero name
    - `level` – Beginner / Intermediate / Advanced / Expert
    - `focus_area` – e.g. “Python Basics”, “Data Structures”
    - `hero_class` – **Warrior, Mage, Healer, or NEO PRO**
  - Profile and history are stored in SQLite.
  - On subsequent runs, user can:
    - Continue with existing hero
    - Or reset data and start a new hero (“New Game”)

- **Hero Classes & Flavor Text**

  - **Warrior** – Beginner: high HP, more forgiving.
  - **Mage** – Intermediate: balanced HP, stronger hint power.
  - **Healer** – Advanced: trickier fights, more support flavor.
  - **NEO PRO** – Expert: low HP, minimal lifelines, maximum challenge.
  - Each class has:
    - A small **ASCII portrait**
    - A short **backstory** printed in a text box

- **CS Fundamentals Training Session**

  - Multiple-choice quiz wrapped as a **turn-based battle**:
    - HP bar, battle counter, basic text “path”/progress indicator.
    - Correct answers defeat “enemies” (Big-O Ogre, Syntax Sprite, Queue Goblin, etc.).
    - Incorrect answers cost HP.
  - Questions cover:
    - Algorithms & Big-O
    - Data structures
    - Python basics
    - Software engineering / CI concepts

- **Basic Analytics**
  - Each completed session is stored as a `QuizSession` row:
    - `profile_id`
    - `topic`
    - `total_questions`
    - `correct_answers`
    - `created_at`
  - This gives a foundation for later milestones (progress tracking, adaptive difficulty, etc.).

---

## 3. Architecture & Design Patterns

The core domain model lives in `TutorSpark/models.py` as dataclasses:

- `LearnerProfile` – maps to `learner_profiles` table.
- `QuizSession` – maps to `quiz_sessions` table.
- `Question` – in-memory question representation.

### 3.1 Strategy Pattern (Milestone 1 focus)

The quiz engine uses the **Strategy pattern** to choose questions:

- `QuestionSelectionStrategy` (in `strategies.py`)

  - Abstract base class with:
    ```python
    def select_questions(self, all_questions, profile, limit) -> List[Question]:
        ...
    ```

- `SequentialStrategy` (concrete strategy)

  - Milestone 1 implementation: return first `N` questions.
  - Future milestones can add difficulty-based, spaced-repetition, or tag-based strategies without changing the engine.

- `AdaptiveEngine` (in `engine.py`)
  - Composes a `QuestionSelectionStrategy`.
  - High-level responsibilities:
    1. Ask strategy for the next batch of questions.
    2. Run an interactive quiz “battle” loop.
    3. Track score, HP, streaks, and lifeline usage.
    4. Persist a `QuizSession` record via `db.insert_quiz_session`.

This matches the Strategy-pattern UML from the Week 2 “Pick a Pattern” assignment.

### 3.2 Persistence Layer

`TutorSpark/db.py` handles all access to SQLite:

- Creates and migrates the schema (`init_db()`).
- Reads/writes `LearnerProfile` and `QuizSession`.
- Provides a `reset_all_data()` helper for “New Game”.

The database file, `tutorspark.db`, is stored next to the Python files, so the app is self-contained.

---

## 4. Folder Structure

At a high level:

```text
cos550-FarmerSamuel-FS/
├── README.md              # This file
├── milestones/            # Week-by-week deliverables (docs, PDFs, etc.)
└── TutorSpark/            # Application source
    ├── __init__.py
    ├── main.py            # Entry point / top-level menu
    ├── profile.py         # Hero creation, save/continue, hero stories & ASCII art
    ├── engine.py          # AdaptiveEngine quiz loop
    ├── strategies.py      # Strategy interface + SequentialStrategy
    ├── quiz.py            # Question bank & glue to engine
    ├── models.py          # Dataclasses: LearnerProfile, QuizSession, Question
    ├── db.py              # SQLite schema and CRUD helpers
    ├── tutorspark.db      # Local SQLite database (generated at runtime)
    └── requirements.txt   # Packaging dependency (PyInstaller)
```

