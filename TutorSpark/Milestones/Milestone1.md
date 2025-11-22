# TutorSpark CLI – Milestone 1

## Overview

TutorSpark CLI is a terminal-based, RPG-flavored learning tool for Computer Science.
In Milestone 1, the app supports:

- Creating a learner profile with a hero class (Warrior, Mage, Healer, NEO PRO)
- Saving and resuming a single profile
- Running a CS Fundamentals training session with multiple-choice questions
- Basic analytics: quiz sessions are stored in a local SQLite database

The quiz engine uses the **Strategy design pattern** to select questions.

## Tech stack

- Python 3.x
- SQLite (via `sqlite3` standard library)
- PyInstaller (for building a standalone binary)

## Project structure

- `main.py` – entry point, top-level menu
- `profile.py` – create/load hero profile, hero stories, class selection
- `engine.py` – `AdaptiveEngine`, runs quiz sessions
- `strategies.py` – `QuestionSelectionStrategy` + `SequentialStrategy`
- `quiz.py` – question bank + glue between profile and engine
- `db.py` – SQLite schema and CRUD helpers
- `models.py` – dataclasses (`LearnerProfile`, `QuizSession`, `Question`)

## How to run from source

```bash
cd TutorSpark
python main.py
```
