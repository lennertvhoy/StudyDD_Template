#!/usr/bin/env python3
"""Recommend the next StudyDD action based on current time and review state.

Usage:
    python3 scripts/select_next_study_action.py \
        --now "2026-06-25T10:00:00+02:00"
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"
SKILL_MAP_PATH = ROOT / "state" / "SKILL_MAP.yaml"
STUDY_STATE_PATH = ROOT / "state" / "STUDY_STATE.yaml"
NEXT_ACTIONS_PATH = ROOT / "NEXT_ACTIONS.md"


def parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


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


def classify_due(item: dict, now: datetime) -> str:
    due_at_str = item.get("due_at")
    status = item.get("status")
    if status in ("completed", "suspended"):
        return status
    if not due_at_str:
        return "scheduled"
    try:
        due_at = datetime.fromisoformat(due_at_str)
    except Exception:
        return "scheduled"
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)

    if due_at <= now:
        if due_at < now - timedelta(days=1):
            return "overdue"
        return "due"
    return "scheduled"


def skill_label(skill_id: str, skill_map: dict) -> str:
    for skill in skill_map.get("skills") or []:
        if skill.get("id") == skill_id:
            return skill.get("label") or skill_id
    return skill_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the next StudyDD study action")
    parser.add_argument("--now", default=None, help="ISO 8601 timestamp with timezone")
    args = parser.parse_args()

    now = parse_now(args.now)
    review_state = load_yaml(REVIEW_STATE_PATH)
    skill_map = load_yaml(SKILL_MAP_PATH)
    study_state = load_yaml(STUDY_STATE_PATH)

    items = review_state.get("review_items") or []

    # Refresh statuses in place.
    for item in items:
        item["status"] = classify_due(item, now)
    save_yaml(REVIEW_STATE_PATH, review_state)

    due = [item for item in items if item.get("status") == "due"]
    overdue = [item for item in items if item.get("status") == "overdue"]
    total_due = len(due) + len(overdue)

    if total_due == 0:
        print("StudyDD recommendation: new material is allowed.")
        print("")
        print("Due reviews: 0")
        print("Overdue reviews: 0")
        print("Recommended action: continue with the active target's next question.")
        print("Reason: no reviews are currently due or overdue.")
        return 0

    # Pick the best candidate: overdue first, then earliest due, then highest priority.
    candidates = overdue or due
    candidates.sort(key=lambda item: (item.get("due_at") or "", item.get("priority") or "normal"))
    chosen = candidates[0]
    chosen_id = chosen.get("id", "<unknown>")
    chosen_skill = chosen.get("skill_id", "<unknown>")
    label = skill_label(chosen_skill, skill_map)

    print("StudyDD recommendation: review first.")
    print("")
    print(f"Due reviews: {len(due)}")
    print(f"Overdue reviews: {len(overdue)}")
    print(f"Recommended action: review {chosen_id} ({label}) before new material.")

    if overdue:
        print("Reason: this review is overdue and has weak or stale evidence.")
    else:
        print("Reason: this review is due today and spaced retrieval is the highest-retention move.")

    print("")
    print('Override allowed:')
    print('Say "override review because <reason>" and the agent must record the override.')
    print("")
    print('Recommended by StudyDD: review first. You can override, but this is the highest-retention move.')

    # Surface in NEXT_ACTIONS.md if an overdue item is not already mentioned.
    if NEXT_ACTIONS_PATH.is_file() and overdue:
        next_text = NEXT_ACTIONS_PATH.read_text(encoding="utf-8")
        if chosen_id not in next_text:
            # We do not rewrite NEXT_ACTIONS.md automatically; the agent should
            # propose the update. This script only reports the recommendation.
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
