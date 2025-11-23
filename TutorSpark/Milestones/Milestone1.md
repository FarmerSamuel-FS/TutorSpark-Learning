# TutorSpark CLI – Milestone 2

## Overview

TutorSpark CLI is a terminal-based, RPG-flavored learning tool for Computer Science.

Milestone 2 builds on the Milestone 1 “first playable slice” and focuses on:

- Wiring the **Strategy pattern** into a real adaptive quiz engine
- Persisting **quiz session analytics** into SQLite
- Producing a **standalone macOS binary** for clean execution on a fresh machine

The user can still:

- Create or resume a learner profile with a hero class (Warrior, Mage, Healer, NEO PRO)
- Run a CS Fundamentals training session with multiple-choice questions
- See results stored as quiz sessions in a local SQLite database

On top of that, this milestone solidifies the architecture and packaging.

---

## What’s new in Milestone 2

### 1. AdaptiveEngine + Strategy pattern

- Implemented `AdaptiveEngine` in `engine.py` to drive the full quiz “battle” loop:

  - Selects questions through a pluggable strategy
  - Tracks HP, streaks, lifelines, and progress path
  - Summarizes each run at the end

- Defined `QuestionSelectionStrategy` in `strategies.py`:

  ```python
  class QuestionSelectionStrategy(ABC):
      @abstractmethod
      def select_questions(self, all_questions, profile, limit) -> list[Question]:
          ...
  ```

- Implemented `SequentialStrategy` as the Milestone 2 concrete strategy:

  - Current behavior: returns the first **N** questions for the session
  - Future milestones can swap in difficulty-based or tag-based strategies without changing `AdaptiveEngine`

- `quiz.py` now:
  - Creates a `SequentialStrategy`
  - Injects it into `AdaptiveEngine`
  - Starts “Quest 1 – CS Questline” for the active `LearnerProfile`

### 2. QuizSession persistence & analytics

- Extended the SQLite schema in `db.py` with a `quiz_sessions` table:

  - `id` (PK)
  - `profile_id` (FK to `learner_profiles`)
  - `topic`
  - `total_questions`
  - `correct_answers`
  - `created_at` (ISO timestamp)

- Added a `QuizSession` dataclass in `models.py`.

- `AdaptiveEngine` now creates and saves a `QuizSession` at the end of each run:

  ```python
  session = QuizSession(
      profile_id=profile.id,
      topic="Quest 1 – CS Questline",
      total_questions=total,
      correct_answers=correct,
      created_at=datetime.utcnow().isoformat(),
  )
  db.insert_quiz_session(session)
  ```

- Verified via:

  ```bash
  cd TutorSpark
  sqlite3 tutorspark.db     "SELECT id, profile_id, topic, total_questions, correct_answers, created_at      FROM quiz_sessions ORDER BY created_at DESC LIMIT 5;"
  ```

### 3. Standalone macOS binary (PyInstaller)

- Added `requirements.txt` in `TutorSpark/` for packaging dependencies.

- Installed and used **PyInstaller** to build a one-file macOS binary:

  ```bash
  cd TutorSpark
  python -m pip install pyinstaller
  python -m PyInstaller --onefile -n tutorspark_cli main.py
  ```

- This produces:

  - `dist/tutorspark_cli` – standalone macOS executable
  - `tutorspark_cli.spec` – PyInstaller spec file

- Packaged for submission:

  ```bash
  cd TutorSpark/dist
  zip tutorspark_cli_mac.zip tutorspark_cli
  ```

---

## Tech stack

- Python 3.x
- SQLite (via `sqlite3` standard library)
- PyInstaller (for building the standalone macOS binary)

---

## Key project files (Milestone 2 focus)

- `main.py` – entry point, top-level menu
- `profile.py` – create/load hero profile, hero stories, class selection
- `engine.py` – **AdaptiveEngine** quiz loop (new core logic in M2)
- `strategies.py` – `QuestionSelectionStrategy` + `SequentialStrategy` (Strategy pattern)
- `quiz.py` – ties profile, engine, and question bank together
- `question_bank.py` – question definitions for CS topics
- `db.py` – SQLite schema and CRUD helpers (now includes `quiz_sessions`)
- `models.py` – dataclasses (`LearnerProfile`, `QuizSession`, `Question`)
- `requirements.txt` – dependencies for dev / packaging
- `tutorspark_cli.spec` – PyInstaller build spec
- `dist/tutorspark_cli` – macOS executable (not tracked in git)
- `dist/tutorspark_cli_mac.zip` – zipped binary for FSO submission (not tracked in git)

---

## How to run from source

```bash
cd TutorSpark
python -m pip install -r requirements.txt
python main.py
```

This:

- Initializes or migrates `tutorspark.db`
- Lets you create or continue a hero profile
- Runs the CS Questline via `AdaptiveEngine` + `SequentialStrategy`
- Writes a `QuizSession` record at the end of each run

---

## How to run the standalone macOS binary

From inside `TutorSpark/dist`:

```bash
./tutorspark_cli
```

Notes:

- No additional `pip install` is required.
- The binary uses the same logic as `main.py` and writes to `tutorspark.db` in the `TutorSpark` directory.
- For FSO submission, the file `tutorspark_cli_mac.zip` is provided as the Milestone 2 executable.
