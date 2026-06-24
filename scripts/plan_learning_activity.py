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

ROOT = Path(__file__).resolve().parent.parent
ACTIVITY_STATE_PATH = ROOT / "state" / "ACTIVITY_STATE.yaml"
ACTIVITY_TEMPLATES_PATH = ROOT / "activities" / "ACTIVITY_TEMPLATES.yaml"
STUDY_STATE_PATH = ROOT / "state" / "STUDY_STATE.yaml"
SKILL_MAP_PATH = ROOT / "state" / "SKILL_MAP.yaml"
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"
LEARNER_PROFILE_PATH = ROOT / "state" / "LEARNER_PROFILE.yaml"
MODE_PATH = ROOT / "state" / "STUDYDD_MODE.yaml"

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


def count_due_reviews(review_state: dict[str, Any]) -> int:
    now = datetime.now(timezone.utc)
    count = 0
    for item in review_state.get("review_items") or []:
        status = item.get("status")
        if status in ("completed", "suspended"):
            continue
        due_at_str = item.get("due_at")
        if not due_at_str:
            continue
        try:
            due_at = datetime.fromisoformat(str(due_at_str))
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=timezone.utc)
            if due_at <= now:
                count += 1
        except Exception:
            continue
    return count


def find_weakest_skill(skill_map: dict[str, Any]) -> dict[str, Any] | None:
    skills = skill_map.get("skills") or []
    candidates = [
        s for s in skills
        if s.get("status") in ("weak", "blocked", "pending")
    ]
    if not candidates:
        return None
    # Prefer weak/blocked, then lowest readiness.
    candidates.sort(
        key=lambda s: (
            0 if s.get("status") == "blocked" else (1 if s.get("status") == "weak" else 2),
            int(s.get("readiness") or 0),
        )
    )
    return candidates[0]


def choose_activity_type(
    skill_id: str | None,
    due_reviews: int,
    weakest_skill: dict[str, Any] | None,
    low_energy: bool,
) -> tuple[str, str, list[str]]:
    """Return (activity_type, reason, expected_evidence)."""
    if due_reviews > 0:
        return (
            "spaced_review",
            f"You have {due_reviews} due review item{'s' if due_reviews != 1 else ''}. Review first is the highest-retention move.",
            ["typed_answer", "transcript", "screenshot"],
        )

    if weakest_skill is not None and weakest_skill.get("status") == "weak":
        # If the learner keeps missing the same skill, vary the format.
        return (
            "paper_exercise",
            f"The skill '{weakest_skill.get('label') or weakest_skill.get('id')}' is weak. A written exercise will slow the learner down and surface hidden gaps.",
            ["photo", "typed_answers"],
        )

    if weakest_skill is not None and weakest_skill.get("status") == "blocked":
        return (
            "explain_back",
            f"The skill '{weakest_skill.get('label') or weakest_skill.get('id')}' is blocked. Explaining it back in the learner's own words helps repair the confusion before new material.",
            ["written_explanation", "transcript"],
        )

    if low_energy:
        return (
            "explain_back",
            "Low-energy mode: a short explain-back task keeps the session small while still producing evidence.",
            ["written_explanation"],
        )

    if skill_id:
        return (
            "retrieval_question",
            f"Focusing on skill '{skill_id}'. One targeted question is the fastest next move.",
            ["typed_answer"],
        )

    return (
        "retrieval_question",
        "No strong signal for another format. Start with one focused question.",
        ["typed_answer"],
    )


def get_template_evidence(activity_type: str, templates: list[dict[str, Any]]) -> list[str]:
    for template in templates:
        if template.get("activity_type") == activity_type:
            return template.get("expected_evidence") or []
    return []


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

    activity_type, reason, expected_evidence = choose_activity_type(
        skill_id,
        due_reviews,
        weakest_skill,
        low_energy,
    )

    # Prefer template-defined evidence list when available.
    templates = templates_data.get("templates") or []
    template_evidence = get_template_evidence(activity_type, templates)
    if template_evidence:
        expected_evidence = template_evidence

    target_id = active_target_id or ""
    skill_for_activity = skill_id or (weakest_skill.get("id") if weakest_skill else "")

    task_description = {
        "retrieval_question": "Answer one focused question in the chat.",
        "spaced_review": "Complete the due review item(s) and submit your answer(s).",
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
        f"StudyDD recommendation: {activity_type.replace('_', ' ')}.\n\n"
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
