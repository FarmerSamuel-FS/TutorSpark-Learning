# Milestone 2 – TutorSpark CLI

---

## 1. Milestone Goal

Milestone 2 extends the “first playable slice” from Milestone 1 into a more robust, testable feature set with:

- A real adaptive quiz engine wired through the **Strategy pattern**.
- Persistent **quiz session analytics** stored in SQLite.
- A **standalone macOS binary** built via PyInstaller for clean execution and grading.

This milestone mainly addresses the following Jira items:

- SFTC-4 – Adaptive Engine & Strategy Pattern
- SFTC-6 – Quiz Session Persistence & Analytics
- SFTC-7 / SFTC-14 – Standalone TutorSpark CLI Executable

---

## 2. Implemented Features

### 2.1 Adaptive Engine & Strategy Pattern (SFTC-4)

**Goal:** Drive quiz sessions through a pluggable selection strategy instead of hard-coded question flow.

**Key work:**

- Defined a `QuestionSelectionStrategy` abstraction in `strategies.py`:

  class QuestionSelectionStrategy(ABC):
  @abstractmethod
  def select_questions(self, all_questions, profile, limit) -> list[Question]:
  ...

- Implemented `SequentialStrategy` (Milestone 2 concrete strategy):

  - Current behavior:
    - Takes `all_questions`, the active `profile`, and a `limit`.
    - Returns the first `N` questions, where `N = limit`.
  - This isolates question selection logic in one place.
  - Future strategies (difficulty-based, tag-based, spaced repetition, etc.) can be added without modifying the engine.

- Implemented `AdaptiveEngine` in `engine.py`:

  - Composes a `QuestionSelectionStrategy` instance.
  - High-level responsibilities:

    1. Pull all questions from `question_bank.py`.
    2. Ask the strategy for a batch:

       selected = strategy.select_questions(all_questions, profile, limit)

    3. Run the turn-based “battle” loop:
       - Tracks HP, battle index, and a simple path indicator.
       - Applies lifelines (hint, 50/50, call a friend, free pass).
       - Prints RPG-style enemy names and feedback for correct/incorrect answers.
    4. Tracks `total_questions` and `correct_answers`.
    5. When the quest ends (win or loss), calls the DB layer to persist a `QuizSession`.

- Updated `quiz.py` orchestration:

  - Loads or creates the active `LearnerProfile`.
  - Chooses a strategy and engine:

        strategy = SequentialStrategy()
        engine = AdaptiveEngine(strategy=strategy)

  - Starts “Quest 1 – CS Questline” with a fixed number of questions.
  - Bridges user interaction, profile, strategy, and DB logging.

**Result:**  
The quiz loop is now fully driven by a Strategy-based engine rather than ad-hoc logic. This matches the Strategy pattern design from the HLDD and “Pick a Pattern” assignment.

---

### 2.2 Quiz Session Persistence & Analytics (SFTC-6)

**Goal:** Log each completed quiz run so future milestones can analyze performance trends.

**Key work:**

- DB schema and dataclass:

  - `db.py` now includes schema and CRUD for `quiz_sessions` table with columns:

        id              INTEGER PRIMARY KEY
        profile_id      INTEGER  -- FK to learner_profiles
        topic           TEXT
        total_questions INTEGER
        correct_answers INTEGER
        created_at      TEXT  -- ISO timestamp

  - `models.py` defines a matching `QuizSession` dataclass.

- Engine writes quiz session summaries:

  After each completed training run, `AdaptiveEngine` constructs a `QuizSession` and persists it:

  session = QuizSession(
  profile_id=profile.id,
  topic="Quest 1 – CS Questline",
  total_questions=total,
  correct_answers=correct,
  created_at=datetime.utcnow().isoformat(),
  )
  db.insert_quiz_session(session)

- Manual verification (from terminal):

  cd TutorSpark
  sqlite3 tutorspark.db \
   "SELECT id, profile_id, topic, total_questions, correct_answers, created_at \
   FROM quiz_sessions ORDER BY created_at DESC LIMIT 5;"

  Example result:

  1|1|Quest 1 – CS Questline|10|8|2025-11-23T05:42:50.566424

**Result:**  
Each training session now leaves a compact analytics record, which can later be used for progress dashboards, adaptive difficulty adjustments, or V&V reporting.

---

### 2.3 Standalone macOS Binary (SFTC-7 / SFTC-14)

**Goal:** Provide a self-contained executable so the instructor can run TutorSpark CLI on a clean machine without manual setup.

**Key work:**

- Added `requirements.txt` in `TutorSpark/` to capture dependencies needed for packaging (PyInstaller).

- Installed PyInstaller into the environment:

  cd TutorSpark
  python -m pip install pyinstaller

- Built a one-file macOS binary:

  cd TutorSpark
  python -m PyInstaller --onefile -n tutorspark_cli main.py

  This produced:

  TutorSpark/
  build/
  dist/
  tutorspark_cli <-- macOS executable
  tutorspark_cli.spec <-- PyInstaller spec file

- Tested the binary locally:

  cd TutorSpark
  ./dist/tutorspark_cli

  Verified behavior:

  - Launch screen prompts for a hero profile (or continues existing).
  - Runs the full “CS Questline” training session:
    - Enemies, HP, path indicator, lifelines.
  - On completion, writes `QuizSession` row into `tutorspark.db`.

- Packaged the binary for submission:

  cd TutorSpark/dist
  zip tutorspark_cli_mac.zip tutorspark_cli

**Result:**  
TutorSpark CLI can now be executed on a macOS system via a single binary file (`tutorspark_cli`), with a zip (`tutorspark_cli_mac.zip`) ready for upload to FSO as the Milestone 2 executable.

---

## 3. How to Run (for Instructor / Reviewer)

### 3.1 Option A – From Source (Development)

Requirements: Python 3.10+.

From repository root:

    cd TutorSpark
    python -m pip install -r requirements.txt
    python main.py

This:

- Initializes or migrates the `tutorspark.db` SQLite database.
- Prompts the user to create or continue a hero profile.
- Starts a CS Questline session through the `AdaptiveEngine` + `SequentialStrategy`.
- Logs a `QuizSession` row upon completion.

### 3.2 Option B – Standalone macOS Binary

From `TutorSpark/dist`:

    ./tutorspark_cli

Notes:

- No additional `pip install` is required; the binary is self-contained.
- The binary will create/modify `tutorspark.db` in the `TutorSpark` directory.
- For grading, the file `tutorspark_cli_mac.zip` can be unzipped and run directly.

---

## 4. V&V Coverage (Milestone 2)

Below is a mapping from Milestone 2 functionality to the HLDD V&V items:

- V&V-A1 – Strategy pattern used for question selection

  - Verified by code review in `strategies.py` and `engine.py`:
    - `AdaptiveEngine` depends on the `QuestionSelectionStrategy` abstraction.
    - `SequentialStrategy` implements that interface and can be swapped without modifying the engine.

- V&V-A2 – Engine can swap strategies without code changes

  - Verified by temporarily wiring a different (stub) strategy in `quiz.py`.
  - Only the instantiation in `quiz.py` needs to change; `AdaptiveEngine` logic remains untouched.

- V&V-P1 – Quiz session persistence

  - Verified by running a full training session, then querying:

        sqlite3 tutorspark.db \
          "SELECT COUNT(*) FROM quiz_sessions;"

  - At least one row appears after completing a run.

- V&V-P2 – Summary data matches user behavior

  - After a run with 10 questions where 8 were answered correctly, inspected the latest row:

        SELECT topic, total_questions, correct_answers
        FROM quiz_sessions
        ORDER BY created_at DESC
        LIMIT 1;

    - Confirmed `topic = "Quest 1 – CS Questline"`, `total_questions = 10`, `correct_answers = 8`.

- V&V-B1 – Binary executes without runtime errors
  - Verified by running `./dist/tutorspark_cli` from a clean shell and completing a full session without crashes.

---

## 5. Screencast Checklist (for Milestone 2 Submission)

For the Milestone 2 screencast, this is the plan to fully address rubric and feedback:

1. **Intro (10–20 seconds)**

   - State name, project title (“TutorSpark CLI”), and Milestone 2 focus (Strategy-based engine, persistence, standalone binary).

2. **Clean build & run from source**

   - Show `git status` (clean).
   - Run:

     cd TutorSpark
     python -m pip install -r requirements.txt (mention this step, no need to wait if already installed)
     python main.py

   - Briefly explain how `main.py` wires profiles, engine, and DB.

3. **Live feature demo**

   - Create or load a hero profile.
   - Run a CS Questline session, showing:
     - Strategy-driven question flow.
     - HP changes, path display, lifeline usage.
     - End-of-session summary.

4. **Code walkthrough**

   - Open `strategies.py`:
     - Show `QuestionSelectionStrategy` and `SequentialStrategy`.
   - Open `engine.py`:
     - Show `AdaptiveEngine` constructor, main loop, and where `QuizSession` is created.
   - Open `db.py` and `models.py`:
     - Show `QuizSession` dataclass and DB insert logic.

5. **Show persistence in SQLite**

   - From terminal:

     sqlite3 tutorspark.db \
      "SELECT id, profile_id, topic, total_questions, correct_answers, created_at \
      FROM quiz_sessions ORDER BY created_at DESC LIMIT 3;"

   - Highlight that the latest row matches the run from the demo.

6. **Show standalone binary build & run**

   - Briefly show `tutorspark_cli.spec` and `dist/tutorspark_cli`.
   - Run `./dist/tutorspark_cli` and demonstrate that the same behavior works without installing dependencies.
   - Mention that `tutorspark_cli_mac.zip` is what will be uploaded as the Milestone 2 executable.

7. **Retrospective (1–2 minutes)**
   - Discuss:
     - Research on Strategy pattern and testable design.
     - Hurdles:
       - Packaging with PyInstaller and handling environment/permissions.
       - Making sure SQLite file path and persistence work both from source and from the binary.
     - How Jira tasks (SFTC-4, 6, 7, 14) guided the work this week.

---

## 6. Files Touched in Milestone 2

- `TutorSpark/strategies.py`

  - Added `QuestionSelectionStrategy` abstraction.
  - Implemented `SequentialStrategy`.

- `TutorSpark/engine.py`

  - Implemented `AdaptiveEngine` quiz loop.
  - Added logic to construct and save `QuizSession` summaries.

- `TutorSpark/db.py`

  - Added `quiz_sessions` table creation.
  - Added insert/query helpers for `QuizSession`.

- `TutorSpark/models.py`

  - Added `QuizSession` dataclass.

- `TutorSpark/quiz.py`

  - Wired `AdaptiveEngine` + `SequentialStrategy` into the CS Questline flow.

- `TutorSpark/requirements.txt`

  - Added packaging dependency (PyInstaller) and any needed runtime libraries.

- `TutorSpark/tutorspark_cli.spec`

  - PyInstaller spec file generated/used for building the standalone binary.

- `TutorSpark/dist/tutorspark_cli` and `TutorSpark/dist/tutorspark_cli_mac.zip`
  - Built binary and zipped artifact for submission (not tracked in git due to `.gitignore`).

---

_End of Milestone 2 report_
