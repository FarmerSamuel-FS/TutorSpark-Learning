from __future__ import annotations

import html
import os
import random
import secrets
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import db
from asset_manifest import (
    ENEMY_ASSETS,
    HERO_ASSETS,
    SCENE_ASSETS,
    get_enemy_for_topic,
    get_scene_for_subject,
)
from engine import apply_fifty_fifty, friend_suggestion, get_hint_for_question, get_reflection_prompt, hero_stats
from models import (
    LearnerProfile,
    ParticipantDemographic,
    QuizSession,
    StudySession,
    SurveyResponse,
    UsabilityEvent,
)
from question_bank import (
    SUBJECT_CATEGORIES,
    SUBJECT_QUIZZES,
    get_questions_for_subject,
    get_subject_title,
    get_subjects_for_category,
)
from quest_lore import build_battle_intro, build_story_gift, get_hero_subject_quest_title


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
QUIZ_LENGTH = 5

SURVEY_PROMPTS = [
    ("interface_clarity", "The interface was easy to understand."),
    ("support_helpfulness", "The hints and support tools helped me reason through the answers."),
    ("cognitive_load", "The tutoring flow felt manageable and not overwhelming."),
    ("trust", "I trusted the tutoring feedback during the session."),
    ("touch_readiness", "The controls and prompts would work well on a touchscreen."),
    ("topic_fit", "The subject/category choices matched what I expected to study."),
    ("engagement_level", "The quest kept me engaged during the session."),
    ("tutoring_effectiveness", "The tutoring condition helped me understand the material."),
    ("interaction_quality", "The interaction quality felt smooth and useful."),
]

SESSIONS: dict[str, dict] = {}
ASSET_ROOT = Path(__file__).resolve().parent

HERO_WEB_CARDS = {
    "Warrior": {
        "class": "warrior",
        "asset": HERO_ASSETS["Warrior"]["idle"],
        "tagline": "High HP, steady progress, built for brave first steps.",
    },
    "Mage": {
        "class": "mage",
        "asset": HERO_ASSETS["Mage"]["idle"],
        "tagline": "Extra insight, pattern power, and curious problem solving.",
    },
    "Healer": {
        "class": "healer",
        "asset": HERO_ASSETS["Healer"]["idle"],
        "tagline": "Calm support, recovery, and careful learning.",
    },
    "NEO PRO": {
        "class": "neo",
        "asset": HERO_ASSETS["NEO PRO"]["idle"],
        "tagline": "Fast missions, fewer assists, maximum focus.",
    },
}


def _page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #52616f;
      --line: #d8e1e8;
      --paper: #f6f8fb;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --warn: #b45309;
      --gold: #f59e0b;
      --violet: #7c3aed;
      --blue: #2563eb;
      --green: #15803d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--paper);
      font-size: 18px;
      line-height: 1.45;
    }}
    main {{
      width: min(920px, 100%);
      margin: 0 auto;
      padding: 20px;
    }}
    header {{
      padding: 22px 20px;
      background: #111827;
      color: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{ margin: 0; font-size: 30px; }}
    h2 {{ margin-top: 28px; font-size: 24px; }}
    p.hint {{ color: #cbd5e1; margin-top: 6px; }}
    label {{ display: block; margin: 16px 0 6px; font-weight: 700; }}
    input, select {{
      width: 100%;
      min-height: 52px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      font-size: 18px;
      background: #ffffff;
    }}
    .panel {{
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 16px 0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }}
    .lobby {{
      display: grid;
      gap: 18px;
    }}
    .welcome {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
      gap: 18px;
      align-items: stretch;
    }}
    .welcome-copy {{
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .welcome-title {{
      margin: 0;
      font-size: 38px;
      line-height: 1.05;
    }}
    .topic-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 16px 0;
    }}
    .topic-pill {{
      display: inline-flex;
      padding: 8px 10px;
      border-radius: 999px;
      background: #e0f2fe;
      color: #0c4a6e;
      font-weight: 700;
      font-size: 15px;
    }}
    .welcome-stage {{
      min-height: 310px;
      border-radius: 8px;
      background-size: cover;
      background-position: center;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
    }}
    .welcome-stage::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(15,23,42,0.05), rgba(15,23,42,0.3));
    }}
    .welcome-hero {{
      display: block;
      position: absolute;
      z-index: 1;
      width: min(42vw, 280px);
      height: min(28vw, 190px);
      background-repeat: no-repeat;
      background-size: contain;
      background-position: center bottom;
      image-rendering: pixelated;
      left: 8%;
      bottom: 4%;
      filter: drop-shadow(0 10px 10px rgba(15, 23, 42, 0.3));
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
      margin: 10px 0 18px;
    }}
    .hero-card {{
      display: block;
      border: 2px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #ffffff;
      min-height: 250px;
      cursor: pointer;
    }}
    .hero-card input {{
      width: auto;
      min-height: auto;
      margin-right: 8px;
    }}
    .hero-card:has(input:checked) {{
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.22);
    }}
    .hero-card.warrior strong {{ color: var(--blue); }}
    .hero-card.mage strong {{ color: var(--violet); }}
    .hero-card.healer strong {{ color: var(--green); }}
    .hero-card.neo strong {{ color: #0f172a; }}
    .hero-art {{
      display: block;
      width: 100%;
      height: 150px;
      margin: 8px 0;
      padding: 10px;
      background: #0f172a;
      border-radius: 8px;
      background-repeat: no-repeat;
      background-size: contain;
      background-position: center bottom;
      image-rendering: pixelated;
    }}
    .quest-preview {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 8px;
      padding: 14px;
    }}
    .battle-stage {{
      position: relative;
      min-height: 430px;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--line);
      background-size: cover;
      background-position: center;
      margin: 14px 0;
    }}
    .battle-stage::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(15,23,42,0.1));
      pointer-events: none;
    }}
    .battle-sprite {{
      display: block;
      position: absolute;
      z-index: 1;
      width: min(26vw, 220px);
      height: min(22vw, 180px);
      background-repeat: no-repeat;
      background-size: contain;
      background-position: center bottom;
      image-rendering: pixelated;
      filter: drop-shadow(0 10px 10px rgba(15, 23, 42, 0.25));
    }}
    .hero-sprite {{
      left: 15%;
      bottom: 22%;
    }}
    .enemy-sprite {{
      right: 15%;
      bottom: 24%;
    }}
    .battle-dialogue {{
      border: 3px solid #111827;
      border-radius: 8px;
      background: #fffdf3;
      box-shadow: 0 4px 0 #111827;
      padding: 14px 16px;
      margin: 12px 0 18px;
      color: #111827;
      font-family: "Courier New", Courier, monospace;
      font-size: 17px;
      font-weight: 700;
      line-height: 1.45;
    }}
    .story-scroll {{
      position: relative;
      border: 4px solid #3b2f1d;
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(120, 72, 28, 0.18), transparent 10%, transparent 90%, rgba(120, 72, 28, 0.18)),
        #fff7dc;
      box-shadow: 0 6px 0 #111827, inset 0 0 0 2px #f3d99b;
      padding: 22px 24px;
      margin: 18px 0 24px;
      color: #1f2937;
      font-family: "Courier New", Courier, monospace;
      font-size: 17px;
      font-weight: 700;
      line-height: 1.5;
    }}
    .story-scroll::before,
    .story-scroll::after {{
      content: "";
      position: absolute;
      left: 18px;
      right: 18px;
      height: 8px;
      border-radius: 999px;
      background: #8b5e34;
    }}
    .story-scroll::before {{ top: -8px; }}
    .story-scroll::after {{ bottom: -8px; }}
    .story-scroll h2 {{
      margin-top: 0;
      font-family: inherit;
      color: #3b2f1d;
    }}
    .story-scroll p {{ margin-bottom: 0; }}
    .menu-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
      margin: 16px 0;
    }}
    .menu-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #f8fafc;
    }}
    .menu-card strong {{
      display: block;
      margin-bottom: 6px;
    }}
    .stat-line {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #e2e8f0;
      padding: 8px 0;
    }}
    .stat-line:last-child {{ border-bottom: 0; }}
    .dojo-list {{
      display: grid;
      gap: 12px;
      padding: 0;
      list-style: none;
    }}
    .dojo-card {{
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px;
      background: #fffdf5;
    }}
    .dojo-answer {{
      margin-top: 8px;
      color: #166534;
      font-weight: 700;
    }}
    .ability-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 8px;
      margin: 12px 0;
    }}
    .ability-bar button {{
      margin: 0;
      min-height: 48px;
      background: #334155;
      font-size: 15px;
    }}
    .ability-bar button:disabled,
    .grid button:disabled {{
      background: #94a3b8;
      cursor: not-allowed;
      opacity: 0.7;
    }}
    .battle-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0;
    }}
    .battle-pill {{
      border-radius: 999px;
      background: #e0f2fe;
      color: #0c4a6e;
      padding: 6px 10px;
      font-weight: 700;
      font-size: 14px;
    }}
    .battle-pill.danger {{
      background: #fee2e2;
      color: #991b1b;
    }}
    .hp-note {{
      margin: 4px 0 12px;
      color: #52616f;
      font-weight: 700;
      font-size: 15px;
    }}
    button, .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 56px;
      width: 100%;
      margin: 8px 0;
      padding: 12px 16px;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: #ffffff;
      font-size: 18px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    button.secondary {{ background: #334155; }}
    button.warning {{ background: var(--warn); }}
    button:hover, .button:hover {{ background: var(--accent-dark); }}
    .result-ok {{ color: #166534; font-weight: 700; }}
    .result-miss {{ color: #991b1b; font-weight: 700; }}
    .meta {{ color: var(--muted); font-size: 16px; }}
    @media (max-width: 700px) {{
      body {{ font-size: 20px; }}
      h1 {{ font-size: 28px; }}
      main {{ padding: 14px; }}
      button, .button, input, select {{ min-height: 60px; font-size: 20px; }}
      .welcome {{ grid-template-columns: 1fr; }}
      .welcome-title {{ font-size: 34px; }}
      .welcome-stage {{ min-height: 260px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>TutorSpark</h1>
    <p class="hint">An interactive RPG learning application for curious adventurers.</p>
  </header>
  <main>{body}</main>
</body>
</html>""".encode("utf-8")


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _misses_remaining(hp: int, damage_on_hit: int) -> int:
    if hp <= 0:
        return 0
    return max(1, (hp + damage_on_hit - 1) // damage_on_hit)


def _hp_warning_text(hp: int, damage_on_hit: int) -> str:
    misses_left = _misses_remaining(hp, damage_on_hit)
    if misses_left <= 0:
        return "HP is empty. The quest run is over."
    if misses_left == 1:
        return "Danger: the next missed answer ends this quest run."
    return f"{misses_left} missed answers left before HP runs out."


def _redirect(handler: BaseHTTPRequestHandler, path: str) -> None:
    handler.send_response(303)
    handler.send_header("Location", path)
    handler.end_headers()


def _read_form(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    size = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(size).decode("utf-8")
    parsed = parse_qs(raw)
    return {key: values[0] for key, values in parsed.items() if values}


def _record_event(
    profile_id: int,
    study_session_id: int,
    event_type: str,
    detail: str,
    question_id: int | None = None,
    elapsed_seconds: float | None = None,
    metadata: str | None = None,
) -> None:
    db.insert_usability_event(
        UsabilityEvent(
            id=None,
            profile_id=profile_id,
            session_id=None,
            event_type=event_type,
            detail=detail,
            created_at=datetime.utcnow(),
            question_id=question_id,
            elapsed_seconds=elapsed_seconds,
            metadata=metadata,
            study_session_id=study_session_id,
        )
    )


class TutorSparkWebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        route = urlparse(self.path)
        if route.path == "/":
            self._send_home()
        elif route.path == "/dashboard":
            self._send_dashboard(parse_qs(route.query).get("hero_name", [""])[0])
        elif route.path == "/dojo":
            query = parse_qs(route.query)
            self._send_dojo(
                query.get("hero_name", [""])[0],
                query.get("subject_key", ["cs_fundamentals"])[0],
            )
        elif route.path.startswith("/assets/"):
            self._send_asset(route.path)
        elif route.path == "/quiz":
            self._send_quiz(parse_qs(route.query).get("sid", [""])[0])
        elif route.path == "/survey":
            self._send_survey(parse_qs(route.query).get("sid", [""])[0])
        elif route.path == "/thanks":
            self._send_thanks(parse_qs(route.query).get("sid", [""])[0])
        else:
            self.send_error(404, "Not found")

    def do_POST(self) -> None:
        route = urlparse(self.path)
        if route.path == "/start":
            self._start_session(_read_form(self))
        elif route.path == "/hero":
            self._create_or_load_hero(_read_form(self))
        elif route.path == "/answer":
            self._answer_question(_read_form(self))
        elif route.path == "/survey":
            self._save_survey(_read_form(self))
        else:
            self.send_error(404, "Not found")

    def _send_bytes(self, content: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_asset(self, request_path: str) -> None:
        relative_path = request_path.lstrip("/")
        asset_path = (ASSET_ROOT / relative_path).resolve()
        if not str(asset_path).startswith(str((ASSET_ROOT / "assets").resolve())):
            self.send_error(403, "Forbidden")
            return
        if not asset_path.exists() or not asset_path.is_file():
            self.send_error(404, "Asset not found")
            return

        content = asset_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_home(self) -> None:
        home_leaderboard_rows = []
        for row in db.get_leaderboard(limit=5):
            home_leaderboard_rows.append(
                f"<li>{_escape(row['hero_class'])} hero "
                f"| Best {row['best_score']:.0f}% | Avg {row['average_score']:.0f}% | Sessions {row['session_count']}</li>"
            )
        hero_cards = []
        for idx, (hero_class, card) in enumerate(HERO_WEB_CARDS.items()):
            checked = "checked" if idx == 0 else ""
            hero_cards.append(
                f"""
<label class="hero-card {card['class']}">
  <input type="radio" name="hero_class" value="{_escape(hero_class)}" {checked}>
  <strong>{_escape(hero_class)}</strong>
  <span class="hero-art" style="background-image: url('/{_escape(card['asset'])}')" aria-label="{_escape(hero_class)} hero sprite"></span>
  <span>{_escape(card['tagline'])}</span>
</label>
"""
            )
        body = f"""
<section class="lobby">
  <section class="panel welcome">
    <div class="welcome-copy">
      <h2 class="welcome-title">Learn Through Quests, Battles, And Story Rewards</h2>
      <p>
        TutorSpark turns short learning quizzes into a retro RPG adventure.
        Choose a hero, enter a subject quest, answer challenge prompts, and
        unlock a custom story after the final survey.
      </p>
      <div class="topic-list">
        <span class="topic-pill">Math</span>
        <span class="topic-pill">Science</span>
        <span class="topic-pill">History</span>
        <span class="topic-pill">Tech</span>
        <span class="topic-pill">Computer Knowledge</span>
      </div>
      <p class="meta">
        Computer Knowledge includes the original TutorSpark CS quizzes:
        algorithms, data structures, Python, software engineering, and version control.
      </p>
    </div>
    <div class="welcome-stage" style="background-image: url('/{_escape(SCENE_ASSETS["computer_knowledge"])}')">
      <span class="welcome-hero" style="background-image: url('/{_escape(HERO_ASSETS["Warrior"]["idle"])}')" aria-label="TutorSpark Warrior hero"></span>
    </div>
  </section>

  <section class="panel">
    <h2>Public Leaderboard</h2>
    <p class="meta">Hero names stay private on this welcome screen. Returning players load progress by typing the exact hero name below.</p>
    <ol>{''.join(home_leaderboard_rows) or '<li>No leaderboard scores yet.</li>'}</ol>
  </section>

  <form class="panel" method="post" action="/hero">
    <h2>Create Or Load Your Hero</h2>
    <p class="meta">
      Enter a hero name before choosing a class. Returning heroes keep their
      saved class and quest history when the same name is used again.
    </p>
    <label for="hero_name">Hero name</label>
    <input id="hero_name" name="hero_name" required maxlength="40" autocomplete="off" placeholder="Type the exact returning hero name, or create a new one">
    <h2>Choose Your Hero</h2>
    <p class="meta">
      New heroes use the class selected here. If the hero name already exists,
      TutorSpark loads that hero's saved class automatically.
    </p>
    <div class="hero-grid">{''.join(hero_cards)}</div>
    <button type="submit">Enter Hero Menu</button>
  </form>
</section>
"""
        self._send_bytes(_page("TutorSpark Study", body))

    def _subject_options(self) -> str:
        options = []
        for category_key, category in SUBJECT_CATEGORIES.items():
            for subject_key, subject in get_subjects_for_category(category_key):
                options.append(
                    f'<option value="{_escape(subject_key)}">'
                    f'{_escape(category["title"])} - {_escape(subject["title"])}</option>'
                )
        return "".join(options)

    def _create_or_load_hero(self, form: dict[str, str]) -> None:
        db.init_db()
        hero_name = " ".join(form.get("hero_name", "").strip().split())
        if not hero_name:
            self.send_error(400, "Hero name is required")
            return
        selected_hero_class = form.get("hero_class", "Warrior")
        profile = db.get_profile_by_name(hero_name)
        if profile is None:
            profile = db.insert_profile(
                LearnerProfile(
                    id=None,
                    name=hero_name,
                    level="Participant",
                    focus_area="TutorSpark Learning",
                    hero_class=selected_hero_class,
                )
            )
        elif profile.hero_class != selected_hero_class and profile.id is not None:
            db.update_profile_hero_class(profile.id, selected_hero_class)
            profile.hero_class = selected_hero_class
        _redirect(self, f"/dashboard?hero_name={quote(profile.name, safe='')}")

    def _send_dashboard(self, hero_name_text: str) -> None:
        db.init_db()
        hero_name = " ".join(hero_name_text.strip().split())
        if not hero_name:
            self.send_error(400, "Exact hero name is required")
            return
        profile = db.get_profile_by_name(hero_name)
        if profile is None:
            self.send_error(404, "Hero profile not found")
            return

        profile_id = profile.id or 0
        summary = db.get_profile_progress_summary(profile_id)
        recent_rows = []
        for session in summary["recent_sessions"]:
            score = session.correct_answers / session.total_questions * 100 if session.total_questions else 0
            recent_rows.append(
                f"<li>{_escape(session.topic)}: {session.correct_answers}/{session.total_questions} ({score:.0f}%)</li>"
            )
        leaderboard_rows = []
        for row in db.get_leaderboard(limit=5):
            leaderboard_rows.append(
                f"<li>{_escape(row['name'])} the {_escape(row['hero_class'])} "
                f"| Best {row['best_score']:.0f}% | Sessions {row['session_count']}</li>"
            )

        body = f"""
<section class="panel">
  <h2>{_escape(profile.name)}'s Hero Menu</h2>
  <p class="meta">{_escape(profile.name)} the {_escape(profile.hero_class)} | CLI-style menu adapted for touch and web testing.</p>
  <div class="menu-grid">
    <div class="menu-card"><strong>Start Subject Quiz</strong><span>Pick a category and begin a five-question RPG battle quest.</span></div>
    <div class="menu-card"><strong>Dojo Practice Run</strong><span>Study the question pool with correct answers before starting the randomized battle.</span></div>
    <div class="menu-card"><strong>View / Select User Profile</strong><span>Return to the welcome screen to load a different exact hero name or create a new hero.</span></div>
    <div class="menu-card"><strong>Progress Report</strong><span>{summary['session_count']} sessions | {summary['correct_answers']}/{summary['total_questions']} correct | Avg {summary['average_score']:.0f}% | Best {summary['best_score']:.0f}%</span></div>
    <div class="menu-card"><strong>Leaderboard</strong><span>Compare completed quest scores from saved heroes below.</span></div>
    <div class="menu-card"><strong>Export Study CSV</strong><span>On Pi/CLI, option 6 exports the full study bundle after completed quests.</span></div>
    <div class="menu-card"><strong>Learning Analysis Bundle</strong><span>On Pi/CLI, option 7 creates the analysis report from completed quests.</span></div>
  </div>
  <div class="stat-line"><span>Average answer time</span><strong>{summary['average_answer_seconds']:.1f}s</strong></div>
  <div class="stat-line"><span>Slowest answer time</span><strong>{summary['slowest_answer_seconds']:.1f}s</strong></div>
</section>

<section class="panel">
  <h2>Dojo Practice Run</h2>
  <form method="post" action="/start">
    <input type="hidden" name="hero_name" value="{_escape(profile.name)}">
    <input type="hidden" name="hero_class" value="{_escape(profile.hero_class)}">
    <label for="subject">Category and topic</label>
    <select id="subject" name="subject_key" required>{self._subject_options()}</select>
    <div class="quest-preview">
      <strong>Dojo briefing:</strong>
      Open the practice run to study the subject question pool with correct answers,
      then begin a randomized five-question quest battle.
    </div>
    <button class="secondary" type="submit" formaction="/dojo" formmethod="get">Open Dojo Practice Run</button>
    <button type="submit">Begin Randomized Quest Battle</button>
  </form>
</section>

<section class="panel">
  <h2>Recent Progress</h2>
  <ul>{''.join(recent_rows) or '<li>No completed quests yet.</li>'}</ul>
</section>

<section class="panel">
  <h2>Leaderboard</h2>
  <ol>{''.join(leaderboard_rows) or '<li>No leaderboard data yet.</li>'}</ol>
  <a class="button secondary" href="/">View / Select User Profile</a>
</section>
"""
        self._send_bytes(_page("TutorSpark Hero Menu", body))

    def _send_dojo(self, hero_name_text: str, subject_key: str) -> None:
        db.init_db()
        hero_name = " ".join(hero_name_text.strip().split())
        if not hero_name:
            self.send_error(400, "Exact hero name is required")
            return
        profile = db.get_profile_by_name(hero_name)
        if profile is None:
            self.send_error(404, "Hero profile not found")
            return

        subject_title = get_subject_title(subject_key)
        questions = get_questions_for_subject(subject_key)
        dojo_rows = []
        for number, question in enumerate(questions, start=1):
            correct_answer = question.options[question.correct_index]
            dojo_rows.append(
                f"""
<li class="dojo-card">
  <strong>{number}. {_escape(question.topic)}</strong>
  <p>{_escape(question.prompt)}</p>
  <div class="dojo-answer">Correct answer: {_escape(correct_answer)}</div>
</li>
"""
            )

        body = f"""
<section class="panel">
  <h2>Dojo Practice Run: {_escape(subject_title)}</h2>
  <p class="meta">
    {_escape(profile.name)} the {_escape(profile.hero_class)} can study the full question pool here.
    The quest battle still draws a randomized five-question set.
  </p>
  <ol class="dojo-list">{''.join(dojo_rows) or '<li>No practice questions available for this subject yet.</li>'}</ol>
  <form method="post" action="/start">
    <input type="hidden" name="hero_name" value="{_escape(profile.name)}">
    <input type="hidden" name="hero_class" value="{_escape(profile.hero_class)}">
    <input type="hidden" name="subject_key" value="{_escape(subject_key)}">
    <button type="submit">Begin Randomized Quest Battle</button>
  </form>
  <a class="button secondary" href="/dashboard?hero_name={quote(profile.name, safe='')}">Back To Hero Menu</a>
</section>
"""
        self._send_bytes(_page("TutorSpark Dojo Practice Run", body))

    def _start_session(self, form: dict[str, str]) -> None:
        subject_key = form.get("subject_key", "cs_fundamentals")
        questions = get_questions_for_subject(subject_key)
        if not questions:
            self.send_error(400, "No questions available for that subject")
            return

        db.init_db()
        participant_code = db.next_participant_code()
        hero_class = form.get("hero_class", "Warrior")
        hero_name = " ".join(form.get("hero_name", "").strip().split())
        if not hero_name:
            self.send_error(400, "Hero name is required")
            return
        profile = db.get_profile_by_name(hero_name)
        profile_status = "loaded"
        if profile is None:
            profile = db.insert_profile(
                LearnerProfile(
                    id=None,
                    name=hero_name,
                    level="Participant",
                    focus_area=get_subject_title(subject_key),
                    hero_class=hero_class,
                )
            )
            profile_status = "created"
        elif profile.hero_class != hero_class and profile.id is not None:
            db.update_profile_hero_class(profile.id, hero_class)
            profile.hero_class = hero_class
        quest_title = get_hero_subject_quest_title(profile, subject_key)
        max_hp, damage_on_hit, hints_left, fifty_left, calls_left, free_passes = hero_stats(profile)
        study_id = db.insert_study_session(
            StudySession(
                id=None,
                profile_id=profile.id or 0,
                participant_code=participant_code,
                task_name=f"{quest_title} web usability task",
                started_at=datetime.utcnow(),
            )
        )
        selected = random.sample(questions, k=min(QUIZ_LENGTH, len(questions)))
        sid = secrets.token_urlsafe(16)
        SESSIONS[sid] = {
            "profile_id": profile.id or 0,
            "study_id": study_id,
            "participant_code": participant_code,
            "hero_name": profile.name,
            "hero_class": profile.hero_class,
            "profile_status": profile_status,
            "quest_title": quest_title,
            "hero_assets": HERO_ASSETS.get(profile.hero_class, HERO_ASSETS["Warrior"]),
            "scene_asset": get_scene_for_subject(subject_key),
            "subject_key": subject_key,
            "question_ids": [question.id for question in selected],
            "questions": selected,
            "index": 0,
            "correct": 0,
            "hp": max_hp,
            "max_hp": max_hp,
            "damage_on_hit": damage_on_hit,
            "hints_left": hints_left,
            "fifty_left": fifty_left,
            "calls_left": calls_left,
            "free_passes": free_passes,
            "streak": 0,
            "hidden_indices": [],
            "used_hint": False,
            "used_fifty": False,
            "used_friend": False,
            "started_at": datetime.utcnow(),
            "question_started_at": datetime.utcnow(),
            "hint": "",
            "result": "",
        }
        _record_event(
            profile.id or 0,
            study_id,
            "study_started",
            f"participant={participant_code}; web=true; profile={profile_status}",
            metadata=f"subject={get_subject_title(subject_key)}; quest={quest_title}; hero={profile.hero_class}; hero_name={profile.name}",
        )
        _redirect(self, f"/quiz?sid={sid}")

    def _send_quiz(self, sid: str) -> None:
        state = SESSIONS.get(sid)
        if state is None:
            self.send_error(404, "Study session not found")
            return
        if state["index"] >= len(state["questions"]):
            _redirect(self, f"/survey?sid={sid}")
            return

        question = state["questions"][state["index"]]
        enemy_name = get_enemy_for_topic(question.topic)
        enemy_asset = ENEMY_ASSETS[enemy_name]
        battle_intro = build_battle_intro(
            LearnerProfile(
                id=state["profile_id"],
                name=state["hero_name"],
                level="Participant",
                focus_area=get_subject_title(state["subject_key"]),
                hero_class=state["hero_class"],
            ),
            state["subject_key"],
            state["quest_title"],
            question.topic,
            enemy_name,
            state["index"] + 1,
            len(state["questions"]),
        )
        result = state.get("result", "")
        hint = state.get("hint", "")
        result_class = "result-miss" if state.get("result_type") == "miss" else "result-ok"
        result_html = f'<p class="{result_class}">{_escape(result)}</p>' if result else ""
        hint_html = f'<div class="panel"><strong>Hint:</strong> {_escape(hint)}</div>' if hint else ""
        misses_left = _misses_remaining(state["hp"], state["damage_on_hit"])
        hp_pill_class = "battle-pill danger" if misses_left <= 1 else "battle-pill"
        hp_warning = _hp_warning_text(state["hp"], state["damage_on_hit"])
        option_buttons = []
        hidden_indices = set(state.get("hidden_indices", []))
        for idx, option in enumerate(question.options):
            disabled = "disabled" if idx in hidden_indices else ""
            label = "[eliminated]" if idx in hidden_indices else _escape(option)
            option_buttons.append(
                f"""
<button name="answer" value="{idx}" type="submit" {disabled}>{label}</button>
"""
            )
        ability_buttons = f"""
<div class="ability-bar">
  <button class="secondary" name="action" value="hint" type="submit" {"disabled" if state["hints_left"] <= 0 or state["used_hint"] else ""}>Hint ({state["hints_left"]})</button>
  <button class="secondary" name="action" value="fifty" type="submit" {"disabled" if state["fifty_left"] <= 0 or state["used_fifty"] else ""}>50/50 ({state["fifty_left"]})</button>
  <button class="secondary" name="action" value="call" type="submit" {"disabled" if state["calls_left"] <= 0 or state["used_friend"] else ""}>Call ({state["calls_left"]})</button>
  <button class="secondary" name="action" value="pass" type="submit" {"disabled" if state["free_passes"] <= 0 else ""}>Free Pass ({state["free_passes"]})</button>
</div>
"""
        body = f"""
<section class="panel">
  <p class="meta">{_escape(state["hero_name"])} | Participant {_escape(state["participant_code"])} | {_escape(state["hero_class"])} Quest: {_escape(state["quest_title"])} | Question {state["index"] + 1} of {len(state["questions"])}</p>
  <div class="battle-stats">
    <span class="battle-pill">HP {state["hp"]}/{state["max_hp"]}</span>
    <span class="{hp_pill_class}">Misses Left {misses_left}</span>
    <span class="battle-pill">Streak {state["streak"]}</span>
    <span class="battle-pill">Hints {state["hints_left"]}</span>
    <span class="battle-pill">50/50 {state["fifty_left"]}</span>
    <span class="battle-pill">Calls {state["calls_left"]}</span>
    <span class="battle-pill">Passes {state["free_passes"]}</span>
  </div>
  <p class="hp-note">{_escape(hp_warning)}</p>
  <div class="battle-stage" style="background-image: url('/{_escape(state["scene_asset"])}')">
    <span class="battle-sprite hero-sprite" style="background-image: url('/{_escape(state["hero_assets"]["idle"])}')" aria-label="{_escape(state["hero_class"])} hero"></span>
    <span class="battle-sprite enemy-sprite" style="background-image: url('/{_escape(enemy_asset)}')" aria-label="{_escape(enemy_name)} enemy"></span>
  </div>
  <div class="battle-dialogue">{_escape(battle_intro)}</div>
  <h2>{_escape(question.prompt)}</h2>
  {result_html}
  {hint_html}
  <form method="post" action="/answer">
    <input type="hidden" name="sid" value="{_escape(sid)}">
    <div class="grid">{''.join(option_buttons)}</div>
    {ability_buttons}
  </form>
</section>
"""
        self._send_bytes(_page("TutorSpark Quiz", body))

    def _answer_question(self, form: dict[str, str]) -> None:
        sid = form.get("sid", "")
        state = SESSIONS.get(sid)
        if state is None:
            self.send_error(404, "Study session not found")
            return
        question = state["questions"][state["index"]]
        elapsed = (datetime.utcnow() - state["question_started_at"]).total_seconds()

        if form.get("action") == "hint":
            state["hint"] = get_hint_for_question(question)
            state["hints_left"] -= 1
            state["used_hint"] = True
            _record_event(
                state["profile_id"],
                state["study_id"],
                "hint_used",
                f"question_index={state['index'] + 1}",
                question_id=question.id,
                elapsed_seconds=round(elapsed, 2),
            )
            _redirect(self, f"/quiz?sid={sid}")
            return

        if form.get("action") == "fifty":
            hidden = set(state.get("hidden_indices", []))
            msg = apply_fifty_fifty(question, hidden)
            state["hidden_indices"] = sorted(hidden)
            state["fifty_left"] -= 1
            state["used_fifty"] = True
            state["result"] = msg
            state["result_type"] = "ok"
            _record_event(
                state["profile_id"],
                state["study_id"],
                "fifty_fifty_used",
                f"question_index={state['index'] + 1}; hidden={state['hidden_indices']}",
                question_id=question.id,
                elapsed_seconds=round(elapsed, 2),
                metadata=f"remaining_fifty_fifty={state['fifty_left']}",
            )
            _redirect(self, f"/quiz?sid={sid}")
            return

        if form.get("action") == "call":
            suggestion = friend_suggestion(question)
            state["calls_left"] -= 1
            state["used_friend"] = True
            state["result"] = f"Your study ally suggests option {suggestion + 1}: {question.options[suggestion]}"
            state["result_type"] = "ok"
            _record_event(
                state["profile_id"],
                state["study_id"],
                "friend_call_used",
                f"question_index={state['index'] + 1}; suggestion={suggestion + 1}",
                question_id=question.id,
                elapsed_seconds=round(elapsed, 2),
                metadata=f"remaining_calls={state['calls_left']}",
            )
            _redirect(self, f"/quiz?sid={sid}")
            return

        if form.get("action") == "pass":
            state["free_passes"] -= 1
            state["correct"] += 1
            state["result"] = "Free Pass used. No damage taken; moving to the next encounter."
            state["result_type"] = "ok"
            _record_event(
                state["profile_id"],
                state["study_id"],
                "free_pass_used",
                f"question_index={state['index'] + 1}",
                question_id=question.id,
                elapsed_seconds=round(elapsed, 2),
                metadata=f"remaining_free_passes={state['free_passes']}",
            )
            self._advance_question_or_finish(sid, state)
            return

        raw_answer = form.get("answer")
        if raw_answer is None:
            _redirect(self, f"/quiz?sid={sid}")
            return
        chosen = int(raw_answer)
        if chosen in set(state.get("hidden_indices", [])):
            state["result"] = "That option has been eliminated. Pick another."
            state["result_type"] = "miss"
            _record_event(
                state["profile_id"],
                state["study_id"],
                "guardrail_retry_prompted",
                "learner_selected_eliminated_option",
                question_id=question.id,
                elapsed_seconds=round(elapsed, 2),
            )
            _redirect(self, f"/quiz?sid={sid}")
            return
        is_correct = chosen == question.correct_index
        if is_correct:
            state["correct"] += 1
            state["streak"] += 1
            state["result"] = "Correct! The enemy is defeated."
            state["result_type"] = "ok"
            if state["streak"] > 0 and state["streak"] % 3 == 0:
                state["free_passes"] += 1
                state["result"] += " Hot streak! You earned a Free Pass."
        else:
            state["hp"] = max(0, state["hp"] - state["damage_on_hit"])
            state["streak"] = 0
            state["result"] = (
                f"Not quite. {get_reflection_prompt(question)} "
                f"Correct answer: {question.options[question.correct_index]} "
                f"{_hp_warning_text(state['hp'], state['damage_on_hit'])}"
            )
            state["result_type"] = "miss"
        _record_event(
            state["profile_id"],
            state["study_id"],
            "answer_submitted",
            f"question_index={state['index'] + 1}; correct={str(is_correct).lower()}",
            question_id=question.id,
            elapsed_seconds=round(elapsed, 2),
            metadata=f"chosen={chosen + 1}; correct_option={question.correct_index + 1}",
        )
        self._advance_question_or_finish(sid, state)

    def _advance_question_or_finish(self, sid: str, state: dict) -> None:
        state["index"] += 1
        state["hint"] = ""
        state["hidden_indices"] = []
        state["used_hint"] = False
        state["used_fifty"] = False
        state["used_friend"] = False
        state["question_started_at"] = datetime.utcnow()
        if state["index"] >= len(state["questions"]) or state["hp"] <= 0:
            db.insert_quiz_session(
                QuizSession(
                    id=None,
                    profile_id=state["profile_id"],
                    topic=f"Web Study - {state['quest_title']}",
                    total_questions=len(state["questions"]),
                    correct_answers=state["correct"],
                    created_at=datetime.utcnow(),
                )
            )
            _record_event(
                state["profile_id"],
                state["study_id"],
                "task_completed",
                f"score={state['correct']}/{len(state['questions'])}",
            )
            _redirect(self, f"/survey?sid={sid}")
            return
        _redirect(self, f"/quiz?sid={sid}")

    def _send_survey(self, sid: str) -> None:
        state = SESSIONS.get(sid)
        if state is None:
            self.send_error(404, "Study session not found")
            return
        rows = []
        demographic_fields = """
<h2>Adventurer Feedback</h2>
<p class="meta">These final questions help us understand who tested TutorSpark. Do not enter names or private details.</p>
<label for="age_range">Age range</label>
<select id="age_range" name="age_range" required>
  <option>under 18</option><option>18-24</option><option>25-34</option>
  <option>35-44</option><option>45+</option><option>prefer not to say</option>
</select>
<label for="learning_background">Learning background</label>
<select id="learning_background" name="learning_background" required>
  <option>K-12</option><option>college</option><option>self-taught</option>
  <option>professional</option><option>other</option>
</select>
<label for="cs_experience">Computer/CS experience</label>
<select id="cs_experience" name="cs_experience" required>
  <option>none</option><option>beginner</option><option>intermediate</option><option>advanced</option>
</select>
<label for="primary_device">Device used today</label>
<select id="primary_device" name="primary_device" required>
  <option>phone</option><option>tablet</option><option>laptop</option>
  <option>desktop</option><option>Raspberry Pi touchscreen</option>
</select>
<label for="accessibility_needs">Accessibility notes</label>
<input id="accessibility_needs" name="accessibility_needs" value="none">
<label for="open_feedback">Comments about TutorSpark</label>
<input id="open_feedback" name="open_feedback" value="none">
<label for="frustration_notes">Anything confusing, frustrating, or hard to use?</label>
<input id="frustration_notes" name="frustration_notes" value="none">
<label for="positive_notes">What did you like, or what worked well?</label>
<input id="positive_notes" name="positive_notes" value="none">
"""
        for key, prompt in SURVEY_PROMPTS:
            options = "".join(f"<option>{value}</option>" for value in range(1, 6))
            rows.append(
                f"""
<label for="{_escape(key)}">{_escape(prompt)}</label>
<select id="{_escape(key)}" name="{_escape(key)}" required>{options}</select>
"""
            )
        body = f"""
<form class="panel" method="post" action="/survey">
  <h2>Quest Complete: Final Survey</h2>
  <p class="meta">1 = strongly disagree, 5 = strongly agree</p>
  <input type="hidden" name="sid" value="{_escape(sid)}">
  {demographic_fields}
  {''.join(rows)}
  <button type="submit">Unlock Story Reward</button>
</form>
"""
        self._send_bytes(_page("TutorSpark Survey", body))

    def _save_survey(self, form: dict[str, str]) -> None:
        sid = form.get("sid", "")
        state = SESSIONS.get(sid)
        if state is None:
            self.send_error(404, "Study session not found")
            return
        responses = []
        for key, prompt in SURVEY_PROMPTS:
            responses.append(
                SurveyResponse(
                    id=None,
                    study_session_id=state["study_id"],
                    profile_id=state["profile_id"],
                    question_key=key,
                    prompt=prompt,
                    rating=int(form.get(key, "3")),
                    created_at=datetime.utcnow(),
                )
            )
        db.insert_survey_responses(responses)
        db.insert_participant_demographic(
            ParticipantDemographic(
                id=None,
                study_session_id=state["study_id"],
                profile_id=state["profile_id"],
                age_range=form.get("age_range", "not provided"),
                learning_background=form.get("learning_background", "not provided"),
                cs_experience=form.get("cs_experience", "not provided"),
                primary_device=form.get("primary_device", "not provided"),
                accessibility_needs=form.get("accessibility_needs", "none") or "none",
                created_at=datetime.utcnow(),
                open_feedback=form.get("open_feedback", "none") or "none",
                frustration_notes=form.get("frustration_notes", "none") or "none",
                positive_notes=form.get("positive_notes", "none") or "none",
            )
        )
        db.complete_study_session(state["study_id"])
        _record_event(
            state["profile_id"],
            state["study_id"],
            "study_completed",
            f"participant={state['participant_code']}; web=true",
        )
        _redirect(self, f"/thanks?sid={sid}")

    def _send_thanks(self, sid: str) -> None:
        state = SESSIONS.get(sid, {})
        score = ""
        story = ""
        if state:
            score = f"<p>Your score was {_escape(state['correct'])}/{_escape(len(state['questions']))}.</p>"
            profile = LearnerProfile(
                id=state["profile_id"],
                name=state["hero_name"],
                level="Participant",
                focus_area=get_subject_title(state["subject_key"]),
                hero_class=state["hero_class"],
            )
            story_text = _escape(
                build_story_gift(
                    profile,
                    state["subject_key"],
                    state["correct"],
                    len(state["questions"]),
                    state["participant_code"],
                )
            ).replace(chr(10), "<br>")
            story = (
                "<div class=\"story-scroll\"><h2>Quest Story Gift</h2>"
                f"<p>{story_text}</p>"
                "</div>"
            )
        body = f"""
<section class="panel">
  <h2>Thank You</h2>
  {score}
  <p>Your anonymous learning data and survey feedback were recorded for TutorSpark Learning.</p>
  {story}
  <a class="button" href="/">Start Another Session</a>
</section>
"""
        self._send_bytes(_page("TutorSpark Complete", body))


def run() -> None:
    db.init_db()
    server = ThreadingHTTPServer((HOST, PORT), TutorSparkWebHandler)
    print(f"TutorSpark web study server running at http://127.0.0.1:{PORT}")
    print("On a Raspberry Pi touchscreen, open Chromium to that address.")
    server.serve_forever()


if __name__ == "__main__":
    run()
