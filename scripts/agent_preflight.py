#!/usr/bin/env python3
"""Agent preflight summary for StudyDD.

Prints a quick orientation: required files, active target, current next action,
due reviews, and last session summary.

Run from the repo root or any subdirectory.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "AGENTS.md",
    "state/STUDYDD_MODE.yaml",
    "state/STUDY_STATUS.md",
    "state/STUDY_STATE.yaml",
    "NEXT_ACTIONS.md",
    "state/STUDY_BACKLOG.md",
    "state/SKILL_MAP.yaml",
    "state/EVIDENCE_LOG.md",
    "targets/README.md",
    "reviews/REVIEW_QUEUE.md",
    "sessions/SESSION_LOG.md",
    "sources/SOURCE_INDEX.md",
]

REQUIRED_PROTOCOLS = [
    "protocols/INSTANTIATE_TEMPLATE.md",
    "protocols/TUTOR_PROTOCOL.md",
    "protocols/SESSION_TEMPLATE.md",
    "protocols/START_SESSION.md",
    "protocols/SELECT_NEXT_ACTION.md",
    "protocols/ASK_QUESTION.md",
    "protocols/GRADE_ANSWER.md",
    "protocols/UPDATE_STATE.md",
    "protocols/SCHEDULE_REVIEW.md",
    "protocols/CLOSE_SESSION.md",
    "protocols/SOURCE_TRUST.md",
    "protocols/READINESS_POLICY.md",
    "protocols/QUESTION_QUALITY.md",
    "protocols/MISTAKE_TAXONOMY.md",
    "protocols/LOW_ENERGY_MODE.md",
]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def read_yaml(rel: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        print("Note: PyYAML not installed. Some checks skipped.")
        return None
    try:
        return yaml.safe_load(read(rel)) or {}
    except Exception:
        return None


def check_files() -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES + REQUIRED_PROTOCOLS:
        if not (ROOT / rel).is_file():
            missing.append(rel)
    return missing


def active_target(data: dict | None) -> str:
    if not data:
        return "(could not parse)"
    return data.get("active_target_id") or "(none — public template)"


def current_mode() -> str:
    data = read_yaml("state/STUDYDD_MODE.yaml")
    if not data:
        return "(could not parse)"
    return data.get("mode") or "(not set)"


def current_next_action() -> str:
    path = ROOT / "NEXT_ACTIONS.md"
    if not path.is_file():
        return "(missing)"
    text = read("NEXT_ACTIONS.md")
    match = re.search(r"## Current next action\n+(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return "(not found)"
    return match.group(1).strip()


def due_reviews() -> int:
    path = ROOT / "reviews/REVIEW_QUEUE.md"
    if not path.is_file():
        return 0
    text = read("reviews/REVIEW_QUEUE.md")
    today = date.today().isoformat()
    due = 0
    in_due = False
    for line in text.splitlines():
        if line.startswith("## Due now"):
            in_due = True
            continue
        if line.startswith("## "):
            in_due = False
            continue
        if in_due and "**Due date:**" in line:
            due_date = line.split("**Due date:**")[-1].strip()
            if due_date and due_date <= today:
                due += 1
    return due


def last_session() -> str:
    path = ROOT / "sessions/SESSION_LOG.md"
    if not path.is_file():
        return "(missing)"
    text = read("sessions/SESSION_LOG.md")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## Session "):
            return "\n".join(lines[i : i + 8]).strip()
    return "(none recorded)"


def main() -> int:
    print("StudyDD Agent Preflight")
    print("=======================")
    print(f"Repo root: {ROOT}")

    try:
        import yaml  # noqa: F401
    except ImportError:
        print("PyYAML not installed. Install with: pip install pyyaml")

    missing = check_files()
    if missing:
        print("\nMissing files:")
        for rel in missing:
            print(f"  - {rel}")
        return 1

    print("\nRequired files: present")

    print(f"\nMode: {current_mode()}")

    study_state = read_yaml("state/STUDY_STATE.yaml")
    print(f"\nActive target: {active_target(study_state)}")

    print("\nCurrent next action:")
    print(current_next_action())

    print(f"\nDue reviews: {due_reviews()}")

    print("\nLast session:")
    print(last_session())

    return 0


if __name__ == "__main__":
    sys.exit(main())
