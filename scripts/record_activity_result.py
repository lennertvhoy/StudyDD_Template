#!/usr/bin/env python3
"""Record the result of a StudyDD learning activity.

Updates the activity state, activity log, evidence log, skill map, and review
state. Keeps readiness upgrades conservative.

Usage:
    python3 scripts/record_activity_result.py \
      --activity-id act_001 \
      --result partial \
      --evidence-id ev_001 \
      --mistake-tags denominator_confusion
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ACTIVITY_STATE_PATH = ROOT / "state" / "ACTIVITY_STATE.yaml"
ACTIVITY_LOG_PATH = ROOT / "activities" / "ACTIVITY_LOG.md"
EVIDENCE_LOG_PATH = ROOT / "state" / "EVIDENCE_LOG.md"
SKILL_MAP_PATH = ROOT / "state" / "SKILL_MAP.yaml"
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"

VALID_RESULTS = {"correct", "partial", "incorrect", "unclear", "insufficient_evidence"}


def load_yaml(path: Path) -> dict[str, Any]:
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


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml

    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def update_activity_state(activity_id: str, result: str, evidence_id: str) -> dict[str, Any] | None:
    data = load_yaml(ACTIVITY_STATE_PATH)
    active = data.get("active_activity") or {}
    if active.get("id") != activity_id:
        return None

    active["status"] = "completed" if result != "insufficient_evidence" else "insufficient_evidence"
    active["submitted_evidence_id"] = evidence_id
    active["completed_at"] = now_iso()
    data["active_activity"] = active

    recent = data.get("recent_activities") or []
    recent.insert(0, {
        "id": active.get("id"),
        "type": active.get("type"),
        "target_id": active.get("target_id"),
        "skill_id": active.get("skill_id"),
        "result": result,
        "evidence_id": evidence_id,
        "completed_at": active["completed_at"],
    })
    data["recent_activities"] = recent[:20]
    data.setdefault("metadata", {})["last_updated"] = now_iso()
    save_yaml(ACTIVITY_STATE_PATH, data)
    return active


def append_activity_log(activity: dict[str, Any], result: str, evidence_id: str, mistake_tags: list[str], notes: str) -> None:
    if not ACTIVITY_LOG_PATH.is_file():
        return

    text = ACTIVITY_LOG_PATH.read_text(encoding="utf-8")
    entry = (
        f"\n- **Activity ID:** {activity.get('id')}\n"
        f"- **Timestamp:** {now_iso()}\n"
        f"- **Type:** {activity.get('type')}\n"
        f"- **Target ID:** {activity.get('target_id')}\n"
        f"- **Skill ID:** {activity.get('skill_id')}\n"
        f"- **Status:** {activity.get('status')}\n"
        f"- **Reason:** {activity.get('reason')}\n"
        f"- **Task:** (see active_activity record)\n"
        f"- **Expected evidence:** {', '.join(activity.get('expected_evidence') or [])}\n"
        f"- **Submitted evidence:** {evidence_id}\n"
        f"- **Verdict:** {result}\n"
    )
    if mistake_tags:
        entry += f"- **Mistake tags:** {', '.join(mistake_tags)}\n"
    if notes:
        entry += f"- **Notes:** {notes}\n"

    marker = "## Activities\n\nNone yet."
    if marker in text:
        text = text.replace(marker, "## Activities" + entry)
    else:
        text += entry
    ACTIVITY_LOG_PATH.write_text(text, encoding="utf-8")


def append_evidence_log(
    activity: dict[str, Any],
    result: str,
    evidence_id: str,
    mistake_tags: list[str],
    notes: str,
) -> None:
    if not EVIDENCE_LOG_PATH.is_file():
        return

    text = EVIDENCE_LOG_PATH.read_text(encoding="utf-8")
    confidence = {
        "correct": "medium",
        "partial": "low",
        "incorrect": "low",
        "unclear": "low",
        "insufficient_evidence": "low",
    }.get(result, "low")

    entry = (
        f"\n- **Evidence ID:** {evidence_id}\n"
        f"- **Date:** {now_iso()[:10]}\n"
        f"- **Target ID:** {activity.get('target_id') or 'unknown'}\n"
        f"- **Skill ID:** {activity.get('skill_id') or 'unknown'}\n"
        f"- **Activity ID:** {activity.get('id')}\n"
        f"- **Activity type:** {activity.get('type')}\n"
        f"- **Question summary:** Activity result for {activity.get('type')}\n"
        f"- **Learner answer summary:** Submitted evidence reviewed.\n"
        f"- **Verdict:** {result}\n"
    )
    if mistake_tags:
        entry += f"- **Mistake type:** {', '.join(mistake_tags)}\n"
    entry += (
        f"- **Explanation:** Recorded from activity {activity.get('id')}. {notes}\n"
        f"- **Confidence:** {confidence}\n"
    )

    marker = "## Evidence items\n\nNone yet."
    if marker in text:
        text = text.replace(marker, "## Evidence items" + entry)
    else:
        text += entry
    EVIDENCE_LOG_PATH.write_text(text, encoding="utf-8")


def update_skill_map(skill_id: str, result: str) -> None:
    if not skill_id:
        return

    data = load_yaml(SKILL_MAP_PATH)
    skills = data.get("skills") or []
    for skill in skills:
        if skill.get("id") != skill_id:
            continue

        current_readiness = int(skill.get("readiness") or 0)
        if result == "correct":
            skill["status"] = "practiced"
            skill["readiness"] = min(max(current_readiness, 50), 55)
            skill["confidence"] = "medium"
        elif result == "partial":
            skill["status"] = "weak" if current_readiness < 40 else "practiced"
            skill["readiness"] = min(max(current_readiness, 35), 50)
            skill["confidence"] = "low"
        elif result in ("incorrect", "unclear"):
            skill["status"] = "weak"
            skill["readiness"] = min(current_readiness, 30)
            skill["confidence"] = "low"
        # insufficient_evidence does not change readiness.

        evidence = skill.get("evidence") or []
        # Do not duplicate; append placeholder reference if needed.
        skill["evidence"] = evidence
        break

    save_yaml(SKILL_MAP_PATH, data)


def schedule_review_if_needed(skill_id: str, evidence_id: str, result: str) -> None:
    if result not in ("partial", "incorrect", "unclear", "insufficient_evidence"):
        return
    if not skill_id:
        return

    confidence = "low" if result in ("incorrect", "unclear", "insufficient_evidence") else "medium"
    cmd = [
        sys.executable,
        "scripts/schedule_review.py",
        "--skill-id",
        skill_id,
        "--evidence-id",
        evidence_id,
        "--grade",
        "wrong" if result in ("incorrect", "unclear", "insufficient_evidence") else "partial",
        "--confidence",
        confidence,
        "--source",
        "activity_result",
        "--prompt",
        "Review the skill using a different activity type than the original submission.",
    ]
    subprocess.run(cmd, cwd=ROOT, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a StudyDD activity result")
    parser.add_argument("--activity-id", required=True)
    parser.add_argument("--result", required=True, choices=sorted(VALID_RESULTS))
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--mistake-tags", default="", help="Comma-separated mistake tags")
    parser.add_argument("--notes", default="", help="Optional notes")
    args = parser.parse_args()

    activity = update_activity_state(args.activity_id, args.result, args.evidence_id)
    if activity is None:
        print(f"Error: activity ID '{args.activity_id}' not found in active_activity.")
        return 1

    mistake_tags = [t.strip() for t in args.mistake_tags.split(",") if t.strip()]
    append_activity_log(activity, args.result, args.evidence_id, mistake_tags, args.notes)
    append_evidence_log(activity, args.result, args.evidence_id, mistake_tags, args.notes)
    update_skill_map(activity.get("skill_id"), args.result)
    schedule_review_if_needed(activity.get("skill_id"), args.evidence_id, args.result)

    print(f"Recorded activity result for {args.activity_id}")
    print(f"  result: {args.result}")
    print(f"  evidence_id: {args.evidence_id}")
    print(f"  skill_id: {activity.get('skill_id') or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
