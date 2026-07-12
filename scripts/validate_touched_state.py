#!/usr/bin/env python3
"""Targeted StudyDD validator for fast-path state updates.

Validates only the IDs touched by an ordinary tutoring turn. This is the fast-path
gate after small updates. It is not a replacement for the full validator, which
runs at session boundaries, CI, audit, and repair.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILL_MAP_PATH = ROOT / "state" / "SKILL_MAP.yaml"
EVIDENCE_LOG_PATH = ROOT / "state" / "EVIDENCE_LOG.md"
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"
STUDY_STATE_PATH = ROOT / "state" / "STUDY_STATE.yaml"
NEXT_ACTIONS_PATH = ROOT / "NEXT_ACTIONS.md"
SESSION_LOG_PATH = ROOT / "sessions" / "SESSION_LOG.md"
ACTIVITY_LOG_PATH = ROOT / "activities" / "ACTIVITY_LOG.md"

OPERATION_REQUIREMENTS = {
    "ask_question": ("active_question",),
    "grade_answer": ("skill_id", "evidence_id"),
    "schedule_review": ("skill_id", "review_id"),
    "record_activity": ("skill_id", "evidence_id", "activity_id"),
    "close_question": ("skill_id", "evidence_id", "active_question"),
}


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
        print(f"Warning: could not read {path}: {exc}")
        return {}


def parse_iso(value: str | None) -> datetime | None:
    """Accept date-only or timezone-aware datetime strings."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        # Date-only values are valid for evidence/review timestamps in StudyDD.
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0 and dt.tzinfo is None:
            return dt
        if dt.tzinfo is None:
            return None
        return dt
    except Exception:
        return None


def load_skill_map() -> dict:
    return load_yaml(SKILL_MAP_PATH)


def load_review_state() -> dict:
    return load_yaml(REVIEW_STATE_PATH)


def load_study_state() -> dict:
    return load_yaml(STUDY_STATE_PATH)


def parse_markdown_records(path: Path, id_label: str) -> list[dict[str, str]]:
    """Parse simple StudyDD audit records beginning with ``id_label``.

    Canonical append-only logs are the validation source. Derived indexes may
    legitimately lag until session-boundary compaction.
    """

    if not path.is_file():
        return []
    field_pattern = re.compile(r"^- \*\*(?P<label>[^*]+):\*\*\s*(?P<value>.*)$")
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = field_pattern.match(raw_line.strip())
        if not match:
            continue
        label = match.group("label").strip()
        value = match.group("value").strip()
        key = label.lower().replace(" ", "_")
        if label == id_label:
            if current is not None:
                records.append(current)
            current = {key: value}
        elif current is not None:
            current[key] = value
    if current is not None:
        records.append(current)
    return records


def canonical_evidence_records() -> list[dict[str, str]]:
    return parse_markdown_records(EVIDENCE_LOG_PATH, "Evidence ID")


def evidence_matches(evidence_id: str) -> list[dict[str, str]]:
    return [
        item
        for item in canonical_evidence_records()
        if item.get("evidence_id") == evidence_id
    ]


def skill_by_id(skill_map: dict, skill_id: str) -> dict | None:
    for skill in skill_map.get("skills") or []:
        if skill.get("id") == skill_id:
            return skill
    return None


def canonical_evidence_by_id(evidence_id: str) -> dict[str, str] | None:
    matches = evidence_matches(evidence_id)
    return matches[0] if len(matches) == 1 else None


def review_by_id(review_state: dict, review_id: str) -> dict | None:
    for item in review_state.get("review_items") or []:
        if item.get("id") == review_id or item.get("review_id") == review_id:
            return item
    return None


def review_matches(review_state: dict, review_id: str) -> list[dict]:
    return [
        item
        for item in review_state.get("review_items") or []
        if item.get("id") == review_id or item.get("review_id") == review_id
    ]


def validate_skill(skill_id: str) -> list[str]:
    errors: list[str] = []
    skill_map = load_skill_map()
    skill = skill_by_id(skill_map, skill_id)
    if not skill:
        errors.append(f"Skill '{skill_id}' not found in state/SKILL_MAP.yaml")
        return errors

    readiness = skill.get("readiness")
    status = skill.get("status")
    evidence = skill.get("evidence") or []

    if readiness is not None:
        try:
            readiness_val = int(readiness)
            if not 0 <= readiness_val <= 100:
                errors.append(f"Skill '{skill_id}' readiness out of range (0-100): {readiness_val}")
        except (TypeError, ValueError):
            errors.append(f"Skill '{skill_id}' readiness is not an integer: {readiness}")

    if status in ("practiced", "confirmed", "demonstrated") and not evidence:
        errors.append(f"Skill '{skill_id}' status '{status}' has no evidence references")

    if readiness is not None:
        try:
            readiness_val = int(readiness)
            if readiness_val >= 70 and len(evidence) < 2:
                errors.append(
                    f"Skill '{skill_id}' readiness {readiness_val} has fewer than 2 evidence references; "
                    "varied evidence cannot be verified"
                )
        except (TypeError, ValueError):
            pass

    return errors


def validate_evidence(evidence_id: str) -> list[str]:
    errors: list[str] = []
    matches = evidence_matches(evidence_id)
    if not matches:
        errors.append(f"Evidence '{evidence_id}' not found in canonical state/EVIDENCE_LOG.md")
        return errors
    if len(matches) > 1:
        errors.append(
            f"Evidence '{evidence_id}' has duplicate evidence ID entries in state/EVIDENCE_LOG.md"
        )
        return errors
    item = matches[0]

    skill_id = item.get("skill_id")
    if skill_id and not skill_by_id(load_skill_map(), skill_id):
        errors.append(f"Evidence '{evidence_id}' references unknown skill '{skill_id}'")

    date = item.get("date")
    if date and not parse_iso(date):
        errors.append(f"Evidence '{evidence_id}' has malformed date '{date}'")

    return errors


def validate_review(review_id: str) -> list[str]:
    errors: list[str] = []
    review_state = load_review_state()
    matches = review_matches(review_state, review_id)
    if not matches:
        errors.append(f"Review '{review_id}' not found in reviews/REVIEW_STATE.yaml")
        return errors
    if len(matches) > 1:
        errors.append(
            f"Review '{review_id}' has duplicate review ID entries in reviews/REVIEW_STATE.yaml"
        )
        return errors
    item = matches[0]

    skill_id = item.get("skill_id")
    evidence_id = item.get("evidence_id")

    if skill_id and not skill_by_id(load_skill_map(), skill_id):
        errors.append(f"Review '{review_id}' references unknown skill '{skill_id}'")

    if evidence_id:
        matches = evidence_matches(str(evidence_id))
        if not matches:
            errors.append(f"Review '{review_id}' references unknown evidence '{evidence_id}'")
        elif len(matches) > 1:
            errors.append(
                f"Review '{review_id}' references duplicate evidence ID '{evidence_id}'"
            )

    due_at = item.get("due_at")
    if due_at and not parse_iso(due_at):
        errors.append(f"Review '{review_id}' has malformed due_at timestamp '{due_at}'")

    last_reviewed = item.get("last_reviewed_at")
    if last_reviewed and not parse_iso(last_reviewed):
        errors.append(f"Review '{review_id}' has malformed last_reviewed_at timestamp '{last_reviewed}'")

    interval = item.get("interval_days")
    if interval is not None:
        try:
            interval_value = float(interval)
            if interval_value <= 0:
                errors.append(
                    f"Review '{review_id}' interval_days must represent a positive duration"
                )
            elif interval_value < 1:
                step = item.get("learning_step") or {}
                try:
                    step_value = float(step.get("value"))
                except (TypeError, ValueError):
                    step_value = 0
                if step_value <= 0 or not step.get("unit"):
                    errors.append(
                        f"Review '{review_id}' sub-day interval requires a positive learning_step"
                    )
        except (TypeError, ValueError):
            errors.append(f"Review '{review_id}' interval_days is not numeric: {interval}")

    return errors


def validate_activity(activity_id: str) -> list[str]:
    records = parse_markdown_records(ACTIVITY_LOG_PATH, "Activity ID")
    matches = [item for item in records if item.get("activity_id") == activity_id]
    if not matches:
        return [f"Activity '{activity_id}' not found in activities/ACTIVITY_LOG.md"]
    if len(matches) > 1:
        return [
            f"Activity '{activity_id}' has duplicate activity ID entries in activities/ACTIVITY_LOG.md"
        ]
    return []


def validate_session(session_id: str) -> list[str]:
    errors: list[str] = []
    if not SESSION_LOG_PATH.is_file():
        errors.append("sessions/SESSION_LOG.md not found")
        return errors

    text = SESSION_LOG_PATH.read_text(encoding="utf-8")
    # session_id may be a date or an identifier mentioned in the session entry.
    if session_id not in text:
        errors.append(f"Session reference '{session_id}' not found in sessions/SESSION_LOG.md")
        return errors

    # Extract evidence references and validate them.
    id_pattern = r"[\w\-]*[\d\-][\w\-]*"
    for match in re.finditer(
        rf"\*\*Evidence added:\*\*[ \t]+({id_pattern}(?:,\s*{id_pattern})*)", text
    ):
        refs = [r.strip() for r in match.group(1).split(",") if r.strip()]
        for ref in refs:
            if ref.lower() in ("none", "n/a", "-", ""):
                continue
            if not canonical_evidence_by_id(ref):
                errors.append(
                    f"Session log evidence reference '{ref}' not found uniquely in canonical evidence log"
                )

    return errors


def validate_active_question(question_id: str) -> list[str]:
    errors: list[str] = []
    study_state = load_study_state()
    active_focus = study_state.get("active_focus") or {}
    state_question = active_focus.get("next_question")

    if state_question and state_question != question_id:
        errors.append(
            f"Active question ID in state/STUDY_STATE.yaml is '{state_question}', "
            f"but validation requested '{question_id}'"
        )

    if NEXT_ACTIONS_PATH.is_file():
        next_text = NEXT_ACTIONS_PATH.read_text(encoding="utf-8")
        if question_id not in next_text:
            errors.append(f"Question ID '{question_id}' not found in NEXT_ACTIONS.md")

    return errors


def validate_operation_requirements(operation: str | None, args: argparse.Namespace) -> list[str]:
    if not operation:
        return []
    errors: list[str] = []
    for field in OPERATION_REQUIREMENTS[operation]:
        if not getattr(args, field):
            errors.append(
                f"Operation '{operation}' requires --{field.replace('_', '-')}"
            )
    return errors


def validate_cross_id_consistency(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    evidence = canonical_evidence_by_id(args.evidence_id) if args.evidence_id else None
    review = review_by_id(load_review_state(), args.review_id) if args.review_id else None

    if args.skill_id and evidence and evidence.get("skill_id") != args.skill_id:
        errors.append(
            f"Evidence '{args.evidence_id}' belongs to skill '{evidence.get('skill_id')}', "
            f"not requested skill '{args.skill_id}'"
        )
    if args.skill_id and review and review.get("skill_id") != args.skill_id:
        errors.append(
            f"Review '{args.review_id}' belongs to skill '{review.get('skill_id')}', "
            f"not requested skill '{args.skill_id}'"
        )
    if evidence and review and review.get("evidence_id") not in (None, "", args.evidence_id):
        errors.append(
            f"Review '{args.review_id}' references evidence '{review.get('evidence_id')}', "
            f"not requested evidence '{args.evidence_id}'"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate only the StudyDD IDs touched in a fast-path update")
    parser.add_argument("--skill-id", help="Skill ID to validate")
    parser.add_argument("--evidence-id", help="Evidence ID to validate")
    parser.add_argument("--review-id", help="Review ID to validate")
    parser.add_argument("--activity-id", help="Activity ID to validate")
    parser.add_argument("--session-id", help="Session reference (e.g., date) to validate")
    parser.add_argument("--active-question", help="Active question ID to validate")
    parser.add_argument(
        "--operation",
        choices=sorted(OPERATION_REQUIREMENTS),
        help="Fast-path operation contract to enforce",
    )
    args = parser.parse_args()

    errors: list[str] = validate_operation_requirements(args.operation, args)

    if args.skill_id:
        errors.extend(validate_skill(args.skill_id))
    if args.evidence_id:
        errors.extend(validate_evidence(args.evidence_id))
    if args.review_id:
        errors.extend(validate_review(args.review_id))
    if args.activity_id:
        errors.extend(validate_activity(args.activity_id))
    if args.session_id:
        errors.extend(validate_session(args.session_id))
    if args.active_question:
        errors.extend(validate_active_question(args.active_question))
    errors.extend(validate_cross_id_consistency(args))

    if not any(
        [
            args.skill_id,
            args.evidence_id,
            args.review_id,
            args.activity_id,
            args.session_id,
            args.active_question,
        ]
    ):
        print(
            "No ID specified. Use --skill-id, --evidence-id, --review-id, "
            "--activity-id, --session-id, or --active-question."
        )
        return 1

    if errors:
        print("Targeted validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Targeted validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
