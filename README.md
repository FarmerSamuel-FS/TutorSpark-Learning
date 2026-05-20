# TutorSpark CLI - Advanced Software Engineering Project (COS550)

TutorSpark CLI is a terminal-based, **RPG-flavored learning assistant** for Computer Science students and general learners.

You create a hero persona (Warrior, Mage, Healer, or NEO PRO) and battle through short CS quizzes as turn-based encounters. Under the hood, TutorSpark uses classic **software design patterns** and a simple **adaptive engine** to select questions and record progress to a local SQLite database.

This repository contains:

- The **TutorSpark CLI application** (in the `TutorSpark/` folder)
- Weekly **milestone deliverables** (in `TutorSpark/Milestones/`), created for the COS550 Advanced Software Engineering course at Full Sail University.

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

## 2. Current Feature Set

Milestone 1 focuses on the **first playable slice** of the system:

### Hero Profile System

- On first run, user creates a _Learner Profile_:
  - `name` – hero name
  - `level` – Beginner / Intermediate / Advanced / Expert
  - `focus_area` – e.g. “Python Basics”, “Data Structures”
  - `hero_class` – **Warrior, Mage, Healer, or NEO PRO**
- Profile and history are stored in SQLite.
- On subsequent runs, user can:
  - Continue with existing hero
  - Or reset data and start a new hero (“New Game”).

### Hero Classes & Flavor Text

- **Warrior** – Beginner: high HP, more forgiving.
- **Mage** – Intermediate: balanced HP, stronger hint power.
- **Healer** – Advanced: trickier fights, more support flavor.
- **NEO PRO** – Expert: low HP, minimal lifelines, maximum challenge.

Each class has:

- A small **ASCII portrait**
- A short **backstory** printed in a text box

### CS Fundamentals Training Session

- Multiple-choice quiz wrapped as a **turn-based battle**:
  - HP bar, battle counter, basic text “path”/progress indicator.
  - Correct answers defeat “enemies” (Big-O Ogre, Syntax Sprite, Queue Goblin, etc.).
  - Incorrect answers cost HP.
- Week 3 category-first quiz navigation:
  - Math
  - Science
  - History
  - Tech
  - Computer Knowledge
- Existing CS quizzes now live under Computer Knowledge:
  - CS Fundamentals
  - Algorithms & Complexity
  - Data Structures
  - Python Programming
  - Software Engineering

### Basic Analytics

Each completed session is stored as a `QuizSession` row:

- `profile_id`
- `topic`
- `total_questions`
- `correct_answers`
- `created_at`

This gives a foundation for later milestones (progress tracking, adaptive difficulty, HCI testing, etc.).

### Week 3 HCI Study Mode

Week 3 adds formal user-testing support for a group of 3-5 participants:

- Hero-specific quest framing, so each subject becomes a different named quest
  depending on whether the learner chooses Warrior, Mage, Healer, or NEO PRO.
- A post-survey "Quest Story Gift" that gives participants a short custom recap
  of their hero's adventure as a thank-you for completing the survey.
- Anonymous participant codes such as `P001`
- Demographic/background capture:
  - age range
  - learning background
  - computer/CS experience
  - device used
  - accessibility notes
- Post-task survey ratings for:
  - interface clarity
  - support/helpfulness
  - cognitive load
  - trust
  - touchscreen readiness
  - topic/category fit
- CSV export bundle for paper analysis:
  - `usability_events.csv`
  - `survey_responses.csv`
  - `participant_demographics.csv`

---

## 3. Architecture & Design Patterns

The core domain model lives in `TutorSpark/models.py` as dataclasses:

- `LearnerProfile` – maps to `learner_profiles` table.
- `QuizSession` – maps to `quiz_sessions` table.
- `Question` – in-memory question representation.

### 3.1 Strategy Pattern (Milestone 1 focus)

The quiz engine uses the **Strategy pattern** to choose questions:

- `QuestionSelectionStrategy` (in `strategies.py`):

  ```python
  def select_questions(self, all_questions, profile, limit) -> list[Question]:
      ...

    SequentialStrategy (concrete strategy):
  •	Milestone 1 implementation: return first N questions.
  •	Future milestones can add difficulty-based, spaced-repetition, or tag-based strategies without changing the engine.
  AdaptiveEngine (in engine.py):
  •	Composes a QuestionSelectionStrategy.
  •	High-level responsibilities:
  1.	Ask strategy for the next batch of questions.
  2.	Run an interactive quiz “battle” loop.
  3.	Track score, HP, streaks, and lifeline usage.
  4.	Persist a QuizSession record via db.insert_quiz_session.
  ```

### 3.2 Persistence Layer

TutorSpark/db.py handles all access to SQLite:
• Creates and migrates the schema (init_db()).
• Reads/writes LearnerProfile and QuizSession.
• Provides a reset_all_data() helper for “New Game”.

The database file, tutorspark.db, is stored next to the Python files, so the app is self-contained.

### 4 Folder Structure:

At a high-level:

cos550-FarmerSamuel-FS/
├── README.md
└── TutorSpark/ # Application source
├── **init**.py
├── main.py # Entry point / top-level menu
├── profile.py # Hero creation, save/continue, hero stories & ASCII art
├── engine.py # AdaptiveEngine quiz loop
├── strategies.py # Strategy interface + SequentialStrategy
├── quiz.py # Quiz orchestration + battle flow
├── question_bank.py # Question definitions for CS topics
├── hero_art.py # ASCII art + UI helpers
├── models.py # Dataclasses: LearnerProfile, QuizSession, Question
├── db.py # SQLite schema and CRUD helpers
├── tutorspark.db # Local SQLite database (generated at runtime)
├── requirements.txt # Dependencies (for dev / packaging)
├── Milestones/ # HLDD, UML diagrams, and other course deliverables
├── tutorspark_cli.spec # PyInstaller build spec (standalone binary)
├── build/ # PyInstaller build artifacts (ignored by git)
└── dist/ # Standalone binary output (ignored by git)
└── tutorspark_cli # macOS executable (Milestone 2)

### 5 Running TutorSpark CLI

Option 1 - Run from source (dev)

1. Make sure Python 3.10+ is installed.
2. From the repo root:

   cd TutorSpark
   python -m pip install -r requirements.txt
   python main.py

This launches the CLI, lets you create/load your hero profile, choose a learning category, run a quiz, complete study mode, and export Week 3 HCI data.

Option 2 - Browser study mode for online testers and touchscreen use

1. From the repo root:

   cd TutorSpark
   python web_app.py

2. Open:

   http://127.0.0.1:8080

The browser version uses large buttons and a single-column responsive layout so it works on phones, tablets, laptops, and a Raspberry Pi 4B with the official 7-inch touchscreen.

Option 3 - GitHub Pages online test deployment

TutorSpark includes a static browser version in `docs/index.html`. This is the easiest free public deployment for remote Week 3 testers because GitHub Pages can publish static HTML, CSS, and JavaScript directly from the repo.

To publish it:

1. Push this repository to GitHub.
2. In the repository, open Settings > Pages.
3. Set Source to "Deploy from a branch".
4. Set Branch to `master` and folder to `/docs`.
5. Save and wait for GitHub to publish the site.

Your project URL will usually look like:

   https://<github-username>.github.io/<repository-name>/

Important data note: GitHub Pages is static hosting, so it cannot write to TutorSpark's SQLite database. The Pages version lets each online participant download a CSV at the end of the study. Use one of these collection methods:

- Ask each tester to send back the downloaded CSV.
- Pair the GitHub Pages app with a Google Form/Microsoft Form upload question.
- Use the Raspberry Pi/local Python web version when you need automatic SQLite logging.

Option 4 - Render online test deployment

TutorSpark includes `render.yaml` for a simple Render web-service deployment. Push this repository to GitHub, create a new Render web service from that repo, and use the free instance type. Render provides an `onrender.com` URL that can be shared with Week 3 testers.

Suggested study workflow:

1. Recruit 3-5 participants with different backgrounds.
2. Send them the TutorSpark web link.
3. Ask each participant to complete one quiz and the post-quiz survey.
4. Export the CSV bundle from the CLI after testing.
5. Summarize patterns in demographics, score, answer time, hint use, and survey ratings.

Option 5 - Raspberry Pi 4B touchscreen

1. Install Python 3 on Raspberry Pi OS.
2. Copy or clone the `TutorSpark` folder onto the Pi. If you use the included desktop launcher unchanged, place it at `~/TutorSpark`.
3. Run:

   cd TutorSpark
   bash scripts/raspi_start.sh

4. Open Chromium on the Pi to:

   http://127.0.0.1:8080

5. For kiosk-style testing, run:

   bash scripts/raspi_kiosk.sh

6. Optional desktop launcher:

   cp scripts/tutorspark-kiosk.desktop ~/.local/share/applications/

The Raspberry Pi version uses `web_app.py`, stores local SQLite data, and is the best version for your homemade tablet setup.

Option 6 - Standalone macOS binary (PyInstaller)

Standalone Binary Provided, built with PyInstaller's --onefile mode:

    cd TutorSpark
    ./dist/tutorspark_cli

This runs TutorSpark CLI without having to install Python dependencies separately. The binary is rebuilt from main.py when needed using tutorspark_cli.spec.
