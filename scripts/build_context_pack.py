#!/usr/bin/env python3
"""Build a task-specific StudyDD context pack.

The context pack is the agent's normal runtime context. It loads compact state,
relevant evidence, and task-specific files while skipping raw audit logs unless
the task is audit or references cannot be resolved.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_PACK_DIR = ROOT / ".studydd"
CONTEXT_PACK_PATH = CONTEXT_PACK_DIR / "context_pack.md"

CANONICAL_STATE_FILES = [
    "state/STUDY_STATE.yaml",
    "state/SKILL_MAP.yaml",
    "reviews/REVIEW_STATE.yaml",
    "state/STUDYDD_MODE.yaml",
    "state/STUDYDD_TEMPLATE_VERSION.yaml",
    "state/STATE_MANIFEST.yaml",
]

SUMMARY_FILES = [
    "state/CURRENT_CONTEXT.md",
    "state/EVIDENCE_INDEX.yaml",
    "sessions/SESSION_SUMMARIES.md",
    "NEXT_ACTIONS.md",
]

RAW_AUDIT_FILES = [
    "state/EVIDENCE_LOG.md",
    "sessions/SESSION_LOG.md",
    "reviews/REVIEW_OVERRIDES.md",
]


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


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except Exception:
        return 0


def read_text(path: Path, max_chars: int | None = None) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[Error reading {path}: {exc}]"
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + f"\n\n[... truncated at {max_chars} characters; full file in {path.relative_to(ROOT)}]"
    return text


def active_target_id(study_state: dict) -> str | None:
    return study_state.get("active_target_id") or None


def active_target_path(study_state: dict) -> Path | None:
    tid = active_target_id(study_state)
    if not tid:
        return None
    path = ROOT / "targets" / tid / "TARGET.yaml"
    if path.is_file():
        return path
    return None


def active_study_skill(target_path: Path | None) -> str | None:
    if not target_path:
        return None
    data = load_yaml(target_path)
    return data.get("study_skill") or None


def relevant_skill_ids(study_state: dict, skill_map: dict, review_state: dict) -> set[str]:
    relevant: set[str] = set()

    active_focus = study_state.get("active_focus") or {}
    if active_focus.get("current_topic"):
        # Heuristic: include skills whose label/id/topic appears in current_topic.
        topic = active_focus["current_topic"].lower()
        for skill in skill_map.get("skills") or []:
            tokens = " ".join(
                filter(
                    None,
                    [
                        str(skill.get("id", "")),
                        str(skill.get("label", "")),
                        str(skill.get("next_validation_question", "")),
                    ],
                )
            ).lower()
            if any(part in tokens for part in topic.split()):
                relevant.add(skill.get("id"))

    for skill in skill_map.get("skills") or []:
        if skill.get("status") in ("weak", "blocked"):
            relevant.add(skill.get("id"))

    for item in review_state.get("review_items") or []:
        sid = item.get("skill_id")
        if sid:
            relevant.add(sid)

    return relevant


def relevant_evidence_excerpts(evidence_index: dict, skill_ids: set[str], max_items: int = 5) -> list[dict]:
    items = evidence_index.get("items") or []
    relevant = [item for item in items if item.get("skill_id") in skill_ids]
    # Prefer weak/partial verdicts and most recent.
    relevant.sort(
        key=lambda item: (
            item.get("verdict", "") not in ("partial", "incorrect", "weak"),
            item.get("date", ""),
        ),
        reverse=True,
    )
    return relevant[:max_items]


def build_context_pack(task: str) -> tuple[str, list[tuple[str, str]], list[tuple[str, str]]]:
    """Return (pack body, included list with reasons, skipped list with reasons)."""
    included: list[tuple[str, str]] = []
    skipped: list[tuple[str, str]] = []
    body_lines: list[str] = []

    now = datetime.now(timezone.utc).isoformat()

    body_lines.extend([
        "# StudyDD Context Pack",
        "",
        f"- **Task:** {task}",
        f"- **Generated at:** {now}",
        f"- **Repo root:** {ROOT}",
        "",
        "## Loading policy",
        "",
        "This pack loads compact canonical state and derived summaries first. "
        "Raw append-only audit logs are referenced only when needed for the task.",
        "",
    ])

    # Load canonical state.
    study_state: dict = {}
    skill_map: dict = {}
    review_state: dict = {}
    mode_data: dict = {}

    for rel in CANONICAL_STATE_FILES:
        path = ROOT / rel
        if path.is_file():
            included.append((rel, "canonical state or manifest"))
        else:
            skipped.append((rel, "file missing"))

    study_state = load_yaml(ROOT / "state" / "STUDY_STATE.yaml")
    skill_map = load_yaml(ROOT / "state" / "SKILL_MAP.yaml")
    review_state = load_yaml(ROOT / "reviews" / "REVIEW_STATE.yaml")
    mode_data = load_yaml(ROOT / "state" / "STUDYDD_MODE.yaml")

    target_path = active_target_path(study_state)
    study_skill = active_study_skill(target_path)

    body_lines.extend([
        "## Mode and remote",
        "",
        f"- **Mode:** {mode_data.get('mode', 'unknown')}",
        f"- **Template remote:** {mode_data.get('template_remote', 'unknown')}",
        f"- **Public safe:** {mode_data.get('public_safe', 'unknown')}",
        "",
        "## Active target",
        "",
    ])

    if target_path:
        included.append((str(target_path.relative_to(ROOT)), "active target metadata"))
        body_lines.append(f"- **Target ID:** {active_target_id(study_state)}")
        body_lines.append(f"- **Target file:** {target_path.relative_to(ROOT)}")
        target_data = load_yaml(target_path)
        body_lines.append(f"- **Target type:** {target_data.get('type', 'not set')}")
        if study_skill:
            body_lines.append(f"- **Study skill:** {study_skill}")
            skill_file = ROOT / "study_skills" / study_skill / "SKILL.md"
            if skill_file.is_file():
                included.append((str(skill_file.relative_to(ROOT)), f"active study skill policy for {study_skill}"))
            else:
                body_lines.append(f"- **Warning:** declared study skill '{study_skill}' has no SKILL.md at {skill_file.relative_to(ROOT)}")
                skipped.append((str(skill_file.relative_to(ROOT)), "declared study skill file missing"))
        else:
            body_lines.append("- **Study skill:** generic (none declared)")
            generic_file = ROOT / "study_skills" / "generic" / "SKILL.md"
            if generic_file.is_file():
                included.append((str(generic_file.relative_to(ROOT)), "generic fallback study skill"))
    else:
        body_lines.append("- **Target ID:** none")
        skipped.append(("targets/<active>/TARGET.yaml", "no active target"))

    body_lines.append("")

    # Summary files.
    for rel in SUMMARY_FILES:
        path = ROOT / rel
        if path.is_file():
            included.append((rel, "derived summary or index"))
        else:
            skipped.append((rel, "derived summary missing"))

    # Relevant skills.
    relevant_ids = relevant_skill_ids(study_state, skill_map, review_state)
    body_lines.extend([
        "## Relevant skills for this task",
        "",
    ])
    if relevant_ids:
        for skill in skill_map.get("skills") or []:
            if skill.get("id") in relevant_ids:
                body_lines.append(
                    f"- **{skill.get('id')}** ({skill.get('label') or 'no label'}): "
                    f"status {skill.get('status')}, readiness {skill.get('readiness')}, confidence {skill.get('confidence')}"
                )
    else:
        body_lines.append("- No specific skills selected for this task.")
    body_lines.append("")

    # Evidence excerpts for non-audit tasks.
    evidence_index = load_yaml(ROOT / "state" / "EVIDENCE_INDEX.yaml")
    if task in ("audit",):
        included.append(("state/EVIDENCE_LOG.md", "full audit log required for audit task"))
        included.append(("sessions/SESSION_LOG.md", "full audit log required for audit task"))
        included.append(("reviews/REVIEW_OVERRIDES.md", "full audit log required for audit task"))
    else:
        excerpts = relevant_evidence_excerpts(evidence_index, relevant_ids)
        body_lines.extend([
            "## Relevant evidence excerpts",
            "",
        ])
        if excerpts:
            for item in excerpts:
                body_lines.append(
                    f"- **{item.get('evidence_id') or 'unknown'}** "
                    f"({item.get('skill_id')}, {item.get('verdict')}, {item.get('date')}): "
                    f"see state/EVIDENCE_LOG.md"
                )
        else:
            body_lines.append("- No relevant evidence excerpts selected.")
        body_lines.append("")
        skipped.append(("state/EVIDENCE_LOG.md", "raw audit log; indexed evidence is enough"))
        skipped.append(("sessions/SESSION_LOG.md", "raw audit log; session summaries are enough"))
        skipped.append(("reviews/REVIEW_OVERRIDES.md", "raw audit log; not needed for this task"))

    # Task-specific notes.
    body_lines.extend([
        "## Task-specific guidance",
        "",
    ])
    if task == "start_session":
        body_lines.append("Load the active target, due reviews, weak skills, last session summary, and current next action. Do not open full raw logs unless the validator reports a conflict.")
    elif task == "ask_question":
        body_lines.append("Include active target, weak skills, due reviews, and question bank metadata. Do not load unrelated target history or full evidence log.")
    elif task == "grade_answer":
        body_lines.append("Include active question, rubric, learner answer, and relevant skill evidence only. Skip unrelated skill history.")
    elif task == "schedule_review":
        body_lines.append("Include review state, confidence, grade, previous interval, and lapses for the relevant skill.")
    elif task == "close_session":
        body_lines.append("Update compact state and summaries after writing logs. Run compact_state.py after appending evidence and session entries.")
    elif task == "upgrade_instance":
        body_lines.append("Load version/protocol files and generic template structure. Do not load learner logs.")
    elif task == "demo":
        body_lines.append("Load enough state to demonstrate the learning loop. Raw logs may be referenced for display but are not the default context.")
    elif task == "audit":
        body_lines.append("Open raw logs and scan indexes and references. Compare compact state against append-only audit trail. Report conflicts instead of guessing.")
    else:
        body_lines.append(f"No specific guidance for task '{task}'. Use the smallest context that contains the needed truth.")
    body_lines.append("")

    # File contents.
    body_lines.extend([
        "## Included file contents",
        "",
    ])

    def emit(rel_path: str, reason: str) -> None:
        path = ROOT / rel_path
        body_lines.append(f"### {rel_path}")
        body_lines.append(f"_Reason: {reason}_")
        body_lines.append("")
        body_lines.append(read_text(path))
        body_lines.append("")

    for rel, reason in included:
        emit(rel, reason)

    # Size estimate.
    total_size = sum(file_size(ROOT / rel) for rel, _ in included)
    rough_tokens = total_size // 4

    body_lines.extend([
        "## Pack summary",
        "",
        f"- **Files included:** {len(included)}",
        f"- **Files skipped:** {len(skipped)}",
        f"- **Approximate bytes loaded:** {total_size}",
        f"- **Rough token estimate:** {rough_tokens}",
        "",
        "### Included files",
        "",
    ])
    for rel, reason in included:
        body_lines.append(f"- `{rel}` — {reason}")
    body_lines.extend([
        "",
        "### Skipped files",
        "",
    ])
    for rel, reason in skipped:
        body_lines.append(f"- `{rel}` — {reason}")
    body_lines.append("")

    return "\n".join(body_lines), included, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a task-specific StudyDD context pack")
    parser.add_argument(
        "--task",
        required=True,
        choices=[
            "start_session",
            "ask_question",
            "grade_answer",
            "schedule_review",
            "close_session",
            "upgrade_instance",
            "demo",
            "audit",
        ],
        help="StudyDD agent task",
    )
    args = parser.parse_args()

    pack, included, skipped = build_context_pack(args.task)

    CONTEXT_PACK_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_PACK_PATH.write_text(pack, encoding="utf-8")

    print("StudyDD context pack built.")
    print("")
    print(f"Task: {args.task}")
    print("Included:")
    for rel, reason in included:
        print(f"- {rel}: {reason}")
    if skipped:
        print("")
        print("Skipped:")
        for rel, reason in skipped:
            print(f"- {rel}: {reason}")
    print("")
    print(f"Output: {CONTEXT_PACK_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
