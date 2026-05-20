from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import db  # noqa: E402


SURVEY_LABELS = {
    "interface_clarity": "Interface clarity",
    "support_helpfulness": "Support helpfulness",
    "cognitive_load": "Manageable cognitive load",
    "trust": "Trust",
    "touch_readiness": "Touch readiness",
    "topic_fit": "Topic fit",
    "engagement_level": "Engagement",
    "tutoring_effectiveness": "Tutoring effectiveness",
    "interaction_quality": "Interaction quality",
}


def _clean_note(value: object) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "none", "n/a", "na", "no"} else text


def _percent(correct: int, total: int) -> float:
    return (correct / total * 100.0) if total else 0.0


def _score_from_detail(detail: str) -> tuple[int, int] | None:
    match = re.search(r"score=(\d+)/(\d+)", detail or "")
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _read_local_db() -> dict[str, list[dict[str, object]]]:
    if not db.DB_PATH.exists():
        return {"participants": [], "surveys": [], "events": [], "qualitative": []}

    db.init_db()
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            ss.id AS study_session_id,
            ss.participant_code,
            ss.task_name,
            ss.started_at,
            ss.completed_at,
            lp.name AS hero_name,
            lp.hero_class,
            pd.age_range,
            pd.learning_background,
            pd.cs_experience,
            pd.primary_device,
            pd.accessibility_needs,
            pd.open_feedback,
            pd.frustration_notes,
            pd.positive_notes
        FROM study_sessions ss
        JOIN learner_profiles lp ON lp.id = ss.profile_id
        LEFT JOIN participant_demographics pd ON pd.study_session_id = ss.id
        ORDER BY ss.started_at ASC, ss.id ASC;
        """
    )
    study_rows = [dict(row) for row in cur.fetchall()]

    cur.execute(
        """
        SELECT
            ss.participant_code,
            sr.study_session_id,
            sr.question_key,
            sr.prompt,
            sr.rating,
            sr.created_at
        FROM survey_responses sr
        JOIN study_sessions ss ON ss.id = sr.study_session_id
        ORDER BY sr.created_at ASC, sr.id ASC;
        """
    )
    surveys = [dict(row) for row in cur.fetchall()]

    cur.execute(
        """
        SELECT
            ss.participant_code,
            ue.study_session_id,
            ue.event_type,
            ue.detail,
            ue.question_id,
            ue.elapsed_seconds,
            ue.metadata,
            ue.created_at
        FROM usability_events ue
        LEFT JOIN study_sessions ss ON ss.id = ue.study_session_id
        ORDER BY ue.created_at ASC, ue.id ASC;
        """
    )
    events = [dict(row) for row in cur.fetchall()]
    conn.close()

    event_scores: dict[int, tuple[int, int]] = {}
    event_counts: dict[int, Counter[str]] = defaultdict(Counter)
    elapsed_by_session: dict[int, list[float]] = defaultdict(list)
    for event in events:
        sid = int(event["study_session_id"] or 0)
        event_counts[sid][str(event["event_type"])] += 1
        if event["event_type"] == "answer_submitted" and event["elapsed_seconds"] is not None:
            elapsed_by_session[sid].append(float(event["elapsed_seconds"]))
        score = _score_from_detail(str(event["detail"]))
        if score:
            event_scores[sid] = score

    participants: list[dict[str, object]] = []
    qualitative: list[dict[str, object]] = []
    for row in study_rows:
        sid = int(row["study_session_id"])
        correct, total = event_scores.get(sid, (0, 0))
        survey_scores = [
            int(item["rating"])
            for item in surveys
            if int(item["study_session_id"]) == sid
        ]
        participants.append(
            {
                "source": "local_db",
                "participant_code": row["participant_code"],
                "hero_name": row["hero_name"],
                "hero_class": row["hero_class"],
                "task_name": row["task_name"],
                "score_correct": correct,
                "score_total": total,
                "score_percent": round(_percent(correct, total), 1),
                "average_survey_rating": round(mean(survey_scores), 2) if survey_scores else "",
                "answer_events": event_counts[sid]["answer_submitted"],
                "support_uses": sum(
                    event_counts[sid][key]
                    for key in ("hint_used", "fifty_fifty_used", "friend_call_used", "free_pass_used")
                ),
                "retry_prompts": event_counts[sid]["guardrail_retry_prompted"],
                "average_answer_seconds": round(mean(elapsed_by_session[sid]), 2)
                if elapsed_by_session[sid]
                else "",
                "age_range": row.get("age_range") or "",
                "learning_background": row.get("learning_background") or "",
                "cs_experience": row.get("cs_experience") or "",
                "primary_device": row.get("primary_device") or "",
                "started_at": row["started_at"],
                "completed_at": row["completed_at"] or "",
            }
        )
        for field, label in (
            ("accessibility_needs", "Accessibility notes"),
            ("open_feedback", "General comments"),
            ("frustration_notes", "Frustration/confusion"),
            ("positive_notes", "Compliments/what worked"),
        ):
            note = _clean_note(row.get(field))
            if note:
                qualitative.append(
                    {
                        "source": "local_db",
                        "participant_code": row["participant_code"],
                        "feedback_type": label,
                        "comment": note,
                    }
                )

    return {
        "participants": participants,
        "surveys": surveys,
        "events": events,
        "qualitative": qualitative,
    }


def _read_static_csvs(paths: list[Path]) -> dict[str, list[dict[str, object]]]:
    participants: dict[str, dict[str, object]] = {}
    surveys: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    qualitative: list[dict[str, object]] = []

    csv_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            csv_files.extend(sorted(path.glob("*.csv")))
        elif path.suffix.lower() == ".csv":
            csv_files.append(path)

    for csv_path in csv_files:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if "record_type" not in (reader.fieldnames or []):
                continue
            for row in reader:
                participant = row.get("participant_code", "")
                if not participant:
                    continue
                record = participants.setdefault(
                    participant,
                    {
                        "source": "static_csv",
                        "participant_code": participant,
                        "hero_name": "",
                        "hero_class": "",
                        "task_name": "",
                        "score_correct": 0,
                        "score_total": 0,
                        "score_percent": 0.0,
                        "average_survey_rating": "",
                        "answer_events": 0,
                        "support_uses": 0,
                        "retry_prompts": 0,
                        "average_answer_seconds": "",
                        "age_range": "",
                        "learning_background": "",
                        "cs_experience": "",
                        "primary_device": "",
                        "started_at": row.get("created_at", ""),
                        "completed_at": "",
                    },
                )
                if row["record_type"] == "quest":
                    field = row.get("field", "")
                    value = row.get("value", "")
                    if field == "hero_name":
                        record["hero_name"] = value
                    elif field == "hero_class":
                        record["hero_class"] = value
                    elif field == "quest_title":
                        record["task_name"] = value
                elif row["record_type"] == "demographic":
                    field = row.get("field", "")
                    value = row.get("value", "")
                    if field in record:
                        record[field] = value
                    if field in {"accessibility_needs", "open_feedback", "frustration_notes", "positive_notes"}:
                        note = _clean_note(value)
                        if note:
                            label = {
                                "accessibility_needs": "Accessibility notes",
                                "open_feedback": "General comments",
                                "frustration_notes": "Frustration/confusion",
                                "positive_notes": "Compliments/what worked",
                            }[field]
                            qualitative.append(
                                {
                                    "source": "static_csv",
                                    "participant_code": participant,
                                    "feedback_type": label,
                                    "comment": note,
                                }
                            )
                elif row["record_type"] == "event":
                    event_type = row.get("event_type", "")
                    events.append(row)
                    if event_type == "answer_submitted":
                        record["answer_events"] = int(record["answer_events"]) + 1
                        if "correct=true" in row.get("detail", ""):
                            record["score_correct"] = int(record["score_correct"]) + 1
                        record["score_total"] = int(record["score_total"]) + 1
                    elif event_type in {"hint_used", "fifty_fifty_used", "friend_call_used", "free_pass_used"}:
                        record["support_uses"] = int(record["support_uses"]) + 1
                    elif event_type == "guardrail_retry_prompted":
                        record["retry_prompts"] = int(record["retry_prompts"]) + 1
                elif row["record_type"] == "survey":
                    surveys.append(
                        {
                            "participant_code": participant,
                            "study_session_id": "",
                            "question_key": row.get("field", ""),
                            "prompt": row.get("detail", ""),
                            "rating": row.get("value", ""),
                            "created_at": row.get("created_at", ""),
                        }
                    )

    for record in participants.values():
        record["score_percent"] = round(
            _percent(int(record["score_correct"]), int(record["score_total"])), 1
        )
        ratings = [
            int(row["rating"])
            for row in surveys
            if row["participant_code"] == record["participant_code"] and str(row["rating"]).isdigit()
        ]
        record["average_survey_rating"] = round(mean(ratings), 2) if ratings else ""

    return {
        "participants": list(participants.values()),
        "surveys": surveys,
        "events": events,
        "qualitative": qualitative,
    }


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _build_markdown(
    output_path: Path,
    participants: list[dict[str, object]],
    surveys: list[dict[str, object]],
    events: list[dict[str, object]],
    qualitative: list[dict[str, object]],
) -> None:
    ratings_by_key: dict[str, list[int]] = defaultdict(list)
    low_rating_rows: list[dict[str, object]] = []
    for row in surveys:
        rating_text = str(row.get("rating", ""))
        if not rating_text.isdigit():
            continue
        rating = int(rating_text)
        key = str(row.get("question_key", ""))
        ratings_by_key[key].append(rating)
        if rating <= 2:
            low_rating_rows.append(row)

    event_counts = Counter(str(row.get("event_type", "")) for row in events)
    scores = [float(row["score_percent"]) for row in participants if row.get("score_total")]
    avg_score = round(mean(scores), 1) if scores else 0.0
    avg_survey = [
        float(row["average_survey_rating"])
        for row in participants
        if str(row.get("average_survey_rating", "")).replace(".", "", 1).isdigit()
    ]
    avg_survey_score = round(mean(avg_survey), 2) if avg_survey else 0.0

    lines = [
        "# TutorSpark Week 3 HCI Analysis Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Data Set",
        f"- Participants/sessions analyzed: {len(participants)}",
        f"- Survey response rows: {len(surveys)}",
        f"- Interaction event rows: {len(events)}",
        f"- Qualitative comments collected: {len(qualitative)}",
        "",
        "## Outcome Snapshot",
        f"- Average quiz score: {avg_score:.1f}%",
        f"- Average survey rating: {avg_survey_score:.2f}/5",
        f"- Support tool uses: {sum(event_counts[key] for key in ('hint_used', 'fifty_fifty_used', 'friend_call_used', 'free_pass_used'))}",
        f"- Retry/frustration prompts: {event_counts['guardrail_retry_prompted']}",
        "",
        "## Survey Averages",
    ]
    for key, ratings in sorted(ratings_by_key.items()):
        label = SURVEY_LABELS.get(key, key.replace("_", " ").title())
        lines.append(f"- {label}: {mean(ratings):.2f}/5 ({len(ratings)} responses)")

    lines.extend(["", "## Potential Frustration Signals"])
    if low_rating_rows:
        for row in low_rating_rows[:12]:
            label = SURVEY_LABELS.get(str(row.get("question_key", "")), str(row.get("question_key", "")))
            lines.append(f"- {row.get('participant_code', '')}: {label} rated {row.get('rating')}/5")
    elif event_counts["guardrail_retry_prompted"]:
        lines.append("- No low ratings found, but retry prompts should be reviewed in event_summary.csv.")
    else:
        lines.append("- No strong frustration signals were found in ratings or retry prompts.")

    lines.extend(["", "## Comments, Complaints, And Compliments"])
    if qualitative:
        for row in qualitative[:20]:
            lines.append(
                f"- {row.get('participant_code', '')} | {row.get('feedback_type', '')}: {row.get('comment', '')}"
            )
    else:
        lines.append("- No open-response comments were collected yet.")

    lines.extend(
        [
            "",
            "## 3.7 Write-Up Notes",
            "- Use `participant_summary.csv` for sample size, demographics, scores, and session-level trends.",
            "- Use `survey_summary.csv` to discuss user friendliness, interaction quality, engagement, and tutoring effectiveness.",
            "- Use `event_summary.csv` for observed behavior: support use, retries, answer timing, and completion flow.",
            "- Use `qualitative_feedback.csv` for direct comments, complaints, and compliments.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect and summarize TutorSpark Week 3 HCI data for the 3.7 project."
    )
    parser.add_argument(
        "--static-csv",
        nargs="*",
        default=[],
        help="Downloaded GitHub Pages CSV files or folders containing those CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path.home() / "Desktop" / f"TutorSpark_Week3_Analysis_{datetime.now().strftime('%Y%m%d_%H%M')}"),
        help="Folder where CSVs and the Markdown report should be written.",
    )
    args = parser.parse_args()

    local = _read_local_db()
    static = _read_static_csvs([Path(path).expanduser() for path in args.static_csv])

    participants = local["participants"] + static["participants"]
    surveys = local["surveys"] + static["surveys"]
    events = local["events"] + static["events"]
    qualitative = local["qualitative"] + static["qualitative"]

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_csv(
        output_dir / "participant_summary.csv",
        participants,
        [
            "source",
            "participant_code",
            "hero_name",
            "hero_class",
            "task_name",
            "score_correct",
            "score_total",
            "score_percent",
            "average_survey_rating",
            "answer_events",
            "support_uses",
            "retry_prompts",
            "average_answer_seconds",
            "age_range",
            "learning_background",
            "cs_experience",
            "primary_device",
            "started_at",
            "completed_at",
        ],
    )
    _write_csv(
        output_dir / "survey_summary.csv",
        surveys,
        ["participant_code", "study_session_id", "question_key", "prompt", "rating", "created_at"],
    )
    _write_csv(
        output_dir / "event_summary.csv",
        events,
        [
            "participant_code",
            "study_session_id",
            "event_type",
            "detail",
            "question_id",
            "elapsed_seconds",
            "metadata",
            "created_at",
        ],
    )
    _write_csv(
        output_dir / "qualitative_feedback.csv",
        qualitative,
        ["source", "participant_code", "feedback_type", "comment"],
    )
    _build_markdown(output_dir / "week3_analysis_summary.md", participants, surveys, events, qualitative)

    print(f"Week 3 analysis bundle written to: {output_dir}")


if __name__ == "__main__":
    main()
