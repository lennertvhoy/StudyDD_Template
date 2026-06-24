#!/usr/bin/env python3
"""Create or update a StudyDD review item with a simple, transparent schedule.

Usage:
    python3 scripts/schedule_review.py \
        --skill-id skill_example \
        --evidence-id ev_001 \
        --target-id target_example \
        --grade partial \
        --confidence low \
        --now "2026-06-24T18:30:00+02:00"

Grade: wrong | partial | correct
Confidence: low | medium | high
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"
REVIEW_QUEUE_PATH = ROOT / "reviews" / "REVIEW_QUEUE.md"


def parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def compute_interval(grade: str, confidence: str, lapses: int = 0) -> int:
    grade = grade.lower()
    confidence = confidence.lower()

    if grade in ("wrong", "incorrect"):
        if confidence == "low":
            interval = 0
        else:
            interval = 1
    elif grade == "partial":
        interval = 1
    elif grade == "correct":
        if confidence == "low":
            interval = 2
        elif confidence == "medium":
            interval = 4
        else:  # high
            interval = 7
    else:
        interval = 1

    if lapses > 0:
        # A lapse resets the interval to the shortest meaningful window.
        interval = min(interval, 1)

    return interval


def make_review_id(skill_id: str, now: datetime) -> str:
    stamp = now.strftime("%Y%m%d_%H%M%S")
    safe_skill = re.sub(r"[^a-zA-Z0-9_-]", "_", skill_id)
    return f"rev_{safe_skill}_{stamp}"


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    if not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"Error reading {path}: {exc}")
        sys.exit(1)


def save_yaml(path: Path, data: dict) -> None:
    import yaml
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def add_to_queue(review_id: str, skill_id: str, evidence_id: str | None, due_at: str, interval: int, prompt: str) -> None:
    if not REVIEW_QUEUE_PATH.is_file():
        return

    text = REVIEW_QUEUE_PATH.read_text(encoding="utf-8")
    entry = (
        f"\n- **Review ID:** {review_id}\n"
        f"- **Skill ID:** {skill_id}\n"
    )
    if evidence_id:
        entry += f"- **Evidence ID:** {evidence_id}\n"
    entry += (
        f"- **Prompt:** {prompt}\n"
        f"- **Due date:** {due_at[:10]}\n"
        f"- **Interval days:** {interval}\n"
    )

    # Place newly scheduled items under Scheduled. The selector will move them
    # to Due now when they become due.
    marker = "## Scheduled\n\n- None."
    if marker in text:
        text = text.replace(marker, "## Scheduled" + entry)
    else:
        text += entry

    REVIEW_QUEUE_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Schedule a StudyDD review item")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--evidence-id", default=None)
    parser.add_argument("--target-id", default=None)
    parser.add_argument("--grade", required=True, choices=["wrong", "incorrect", "partial", "correct"])
    parser.add_argument("--confidence", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--now", default=None, help="ISO 8601 timestamp with timezone")
    parser.add_argument("--prompt", default="Review this skill using a question in a different mode than the original.")
    parser.add_argument("--source", default="missed_question", help="Why the review was scheduled")
    args = parser.parse_args()

    now = parse_now(args.now)
    interval = compute_interval(args.grade, args.confidence)
    due_at = now + timedelta(days=interval)
    due_at_str = due_at.isoformat()

    review_id = make_review_id(args.skill_id, now)

    state = load_yaml(REVIEW_STATE_PATH)
    items = state.setdefault("review_items", [])

    item = {
        "id": review_id,
        "skill_id": args.skill_id,
        "evidence_id": args.evidence_id,
        "target_id": args.target_id,
        "due_at": due_at_str,
        "last_reviewed_at": None,
        "interval_days": interval,
        "stability": None,
        "difficulty": None,
        "lapses": 0,
        "priority": "normal",
        "status": "scheduled",
        "source": args.source,
        "override_count": 0,
    }
    items.append(item)
    save_yaml(REVIEW_STATE_PATH, state)

    add_to_queue(review_id, args.skill_id, args.evidence_id, due_at_str, interval, args.prompt)

    print(f"Scheduled review {review_id}")
    print(f"  skill_id: {args.skill_id}")
    print(f"  evidence_id: {args.evidence_id}")
    print(f"  grade: {args.grade}")
    print(f"  confidence: {args.confidence}")
    print(f"  interval_days: {interval}")
    print(f"  due_at: {due_at_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
