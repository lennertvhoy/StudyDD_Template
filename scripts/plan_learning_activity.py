#!/usr/bin/env python3
"""Plan the next StudyDD learning activity.

Inspects current state, reviews, learner profile, and study skill, then
recommends one activity with a reason, expected evidence, and learner-control
phrase.

Usage:
    python3 scripts/plan_learning_activity.py --task start_session
    python3 scripts/plan_learning_activity.py --skill-id <skill_id>
    python3 scripts/plan_learning_activity.py --low-energy
    python3 scripts/plan_learning_activity.py --demo
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from next_activity_decision import (
    choose_activity_decision,
    count_due_reviews,
    find_weakest_skill,
    recent_activity_types,
)

ROOT = Path(__file__).resolve().parent.parent
ACTIVITY_STATE_PATH = ROOT / "state" / "ACTIVITY_STATE.yaml"
ACTIVITY_TEMPLATES_PATH = ROOT / "activities" / "ACTIVITY_TEMPLATES.yaml"
STUDY_STATE_PATH = ROOT / "state" / "STUDY_STATE.yaml"
SKILL_MAP_PATH = ROOT / "state" / "SKILL_MAP.yaml"
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"
MODE_PATH = ROOT / "state" / "STUDYDD_MODE.yaml"
TARGETS_DIR = ROOT / "targets"

DEMO_OUTPUT = """StudyDD recommendation: paper exercise.

Reason:
The learner has missed this skill twice and answered too quickly. A short written exercise is more useful than another chat question.

Task:
Solve 5 problems on paper and upload a photo or type your answers.

Expected evidence:
photo or typed answers

Learner control:
You can accept, modify, or override this.
"""


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
        print(f"Warning: could not read {path.relative_to(ROOT)}: {exc}")
        return {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml

    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_active_target(active_target_id: str | None) -> dict[str, Any]:
    """Load TARGET.yaml for the active target, if any."""
    if not active_target_id:
        return {}
    target_path = TARGETS_DIR / active_target_id / "TARGET.yaml"
    if not target_path.is_file():
        return {}
    return load_yaml(target_path)


def format_evidence(evidence: list[str]) -> str:
    if not evidence:
        return "typed answer or transcript"
    return " or ".join(evidence)


def plan_activity(
    task: str,
    skill_id: str | None,
    low_energy: bool,
    demo: bool,
) -> tuple[str, dict[str, Any] | None]:
    if demo:
        return DEMO_OUTPUT, None

    activity_state = load_yaml(ACTIVITY_STATE_PATH)
    review_state = load_yaml(REVIEW_STATE_PATH)
    skill_map = load_yaml(SKILL_MAP_PATH)
    study_state = load_yaml(STUDY_STATE_PATH)
    mode_data = load_yaml(MODE_PATH)
    templates_data = load_yaml(ACTIVITY_TEMPLATES_PATH)

    active_target_id = study_state.get("active_target_id")
    due_reviews = count_due_reviews(review_state)
    weakest_skill = find_weakest_skill(skill_map)

    target = load_active_target(active_target_id)
    study_skill = target.get("study_skill") or ""
    recent_types = recent_activity_types(activity_state)
    templates = templates_data.get("templates") or []

    decision = choose_activity_decision(
        skill_id,
        due_reviews,
        weakest_skill,
        low_energy,
        target,
        study_skill,
        recent_types,
        templates,
    )
    activity_type = decision.activity_type
    reason = decision.reason
    expected_evidence = decision.expected_evidence

    target_id = active_target_id or ""
    skill_for_activity = skill_id or (weakest_skill.get("id") if weakest_skill else "")

    task_description = {
        "retrieval_question": "Answer one focused question in the chat.",
        "spaced_review": "Complete the due review item(s) and submit your answer(s).",
        "recent_info_check": "Check the freshness of the relevant source, then answer the check question or summarize what changed.",
        "paper_exercise": "Solve the suggested problems on paper, then upload a photo or type your answers.",
        "external_platform_exercise": "Complete the recommended exercise on the external platform and upload your score, screenshot, or notes.",
        "video_or_reading_task": "Watch or read the selected resource, then submit a short summary or answer the check question.",
        "practical_lab": "Perform the suggested technical task and upload a screenshot, command output, or explanation.",
        "explain_back": "Explain the concept back in your own words.",
        "diagram_or_whiteboard": "Draw the requested model, flow, or map and upload a photo or screenshot.",
        "interview_prep": "Answer the realistic interview prompt with a concrete example.",
        "presentation_prep": "Rehearse the suggested segment and upload a transcript or timing notes.",
        "voice_note_review": "Record or type a transcript of your answer and submit it for review.",
        "writing_or_essay_review": "Submit the written answer, essay, or draft for feedback.",
        "upload_and_review": "Upload your work (screenshot, PDF, notes, log) for review.",
    }.get(activity_type, "Complete the suggested learning activity.")

    output = (
        f"StudyDD recommendation: {activity_type}.\n\n"
        f"Reason:\n{reason}\n\n"
        f"Task:\n{task_description}\n\n"
        f"Expected evidence:\n{format_evidence(expected_evidence)}\n\n"
        "Learner control:\n"
        "You can accept, modify, or override this.\n"
    )

    proposed_activity: dict[str, Any] | None = None
    mode = mode_data.get("mode")
    if mode == "learner_instance":
        proposed_activity = {
            "id": f"act_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "type": activity_type,
            "target_id": target_id,
            "skill_id": skill_for_activity,
            "assigned_at": now_iso(),
            "due_at": "",
            "status": "proposed",
            "reason": reason,
            "expected_evidence": expected_evidence,
            "rule_id": decision.rule_id,
            "learner_override_allowed": True,
        }

    return output, proposed_activity


def update_activity_state(proposed_activity: dict[str, Any]) -> None:
    data = load_yaml(ACTIVITY_STATE_PATH)
    recent = data.get("recent_activities") or []
    current = data.get("active_activity")
    if current and current.get("id"):
        recent.insert(0, current)
        recent = recent[:10]
    data["active_activity"] = proposed_activity
    data["recent_activities"] = recent
    data.setdefault("metadata", {})["last_updated"] = now_iso()
    save_yaml(ACTIVITY_STATE_PATH, data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan the next StudyDD learning activity")
    parser.add_argument("--task", default="start_session", help="Agent task context")
    parser.add_argument("--skill-id", help="Focus on a specific skill ID")
    parser.add_argument("--low-energy", action="store_true", help="Plan a low-energy activity")
    parser.add_argument("--demo", action="store_true", help="Print deterministic demo recommendation")
    args = parser.parse_args()

    output, proposed = plan_activity(
        task=args.task,
        skill_id=args.skill_id,
        low_energy=args.low_energy,
        demo=args.demo,
    )
    print(output, end="")

    if proposed is not None:
        update_activity_state(proposed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
