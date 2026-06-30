#!/usr/bin/env python3
"""Fast Drill Mode checkpoint helper for StudyDD.

Lightweight speed layer for active question drills. Canonical state is reconciled
at session end; during the drill only a single append-only checkpoint is updated.

See docs/superpowers/specs/FAST_DRILL_MODE.md for the full spec.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

VALID_VERDICTS = {"correct", "partial", "incorrect", "unclear", "override"}
RECOVERY_AGE_HOURS = 4


def _state_path(repo_root: Path | str | None, rel: str) -> Path:
    root = Path(repo_root) if repo_root else ROOT
    return root / rel


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

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_mode(repo_root: Path | str | None = None) -> str:
    mode_data = load_yaml(_state_path(repo_root, "state/STUDYDD_MODE.yaml"))
    return mode_data.get("mode", "unknown")


def _refuse_template(repo_root: Path | str | None, demo: bool = False) -> bool:
    if demo:
        return False
    if repo_mode(repo_root) == "template":
        print("Error: fast_drill_mode checkpoint operations are not allowed in template mode.")
        print("Create a learner instance with scripts/create_instance.py first.")
        return True
    return False


def start_drill(
    session_id: str,
    target_id: str,
    mode: str = "normal",
    drill_type: str = "retrieval_question",
    source_ref: str = "",
    repo_root: Path | str | None = None,
    demo: bool = False,
) -> int:
    """Create a new active drill checkpoint."""
    root = Path(repo_root) if repo_root else ROOT
    if _refuse_template(root, demo):
        return 2

    path = _state_path(root, "state/ACTIVE_DRILL_SESSION.md")
    if path.is_file():
        print(
            f"Error: an active drill already exists at {path.relative_to(root)}. "
            "Run 'recover' or 'end' first."
        )
        return 1

    import yaml

    metadata = {
        "session_id": session_id,
        "target_id": target_id,
        "mode": mode,
        "drill_type": drill_type,
        "started_at": now_iso(),
        "source_ref": source_ref or "",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n"
    path.write_text(header, encoding="utf-8")
    print(f"Started drill: {session_id}")
    return 0


def append_checkpoint(
    question_id: str,
    skill_id: str,
    concept: str,
    answer_summary: str,
    verdict: str,
    correction_summary: str,
    confidence: str,
    evidence_marker: str,
    repo_root: Path | str | None = None,
) -> int:
    """Append one graded-answer line to the active checkpoint."""
    root = Path(repo_root) if repo_root else ROOT
    if _refuse_template(root):
        return 2

    path = _state_path(root, "state/ACTIVE_DRILL_SESSION.md")
    if not path.is_file():
        print("Error: no active drill. Start one with 'start' first.")
        return 1

    if verdict not in VALID_VERDICTS:
        print(f"Error: invalid verdict '{verdict}'. Must be one of {sorted(VALID_VERDICTS)}.")
        return 1

    entry = {
        "ts": now_iso(),
        "question_id": question_id,
        "skill_id": skill_id,
        "concept": concept,
        "answer_summary": answer_summary,
        "verdict": verdict,
        "correction_summary": correction_summary or "",
        "confidence": confidence,
        "evidence_marker": evidence_marker,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Appended checkpoint: {evidence_marker}")
    return 0


def load_checkpoint(repo_root: Path | str | None = None) -> dict[str, Any]:
    """Parse the active checkpoint into metadata and entries."""
    root = Path(repo_root) if repo_root else ROOT
    path = _state_path(root, "state/ACTIVE_DRILL_SESSION.md")
    if not path.is_file():
        raise FileNotFoundError(f"No active drill checkpoint at {path}")

    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", text, flags=re.MULTILINE, maxsplit=2)
    if len(parts) < 3:
        raise ValueError(f"Invalid checkpoint format in {path}")

    import yaml

    metadata = yaml.safe_load(parts[1]) or {}
    entries: list[dict[str, Any]] = []
    for line in parts[2].splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return {"metadata": metadata, "entries": entries}


def is_drill_active(repo_root: Path | str | None = None) -> bool:
    return _state_path(repo_root, "state/ACTIVE_DRILL_SESSION.md").is_file()


def _checkpoint_age_hours(metadata: dict[str, Any]) -> float | None:
    started = metadata.get("started_at")
    if not started:
        return None
    try:
        dt = datetime.fromisoformat(started)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return None


def _compute_skill_updates(
    repo_root: Path | str | None, skill_effects: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, Any] | None]:
    skill_map = load_yaml(_state_path(repo_root, "state/SKILL_MAP.yaml"))
    existing = {s.get("id"): s for s in skill_map.get("skills", []) if s.get("id")}
    updates: dict[str, dict[str, Any] | None] = {}

    for sid, entries in skill_effects.items():
        skill = existing.get(sid)
        if not skill:
            updates[sid] = None
            continue

        current_readiness = int(skill.get("readiness") or 0)
        had_repair = any(e.get("correction_summary") for e in entries)
        verdicts = [e.get("verdict") for e in entries]

        if any(v in ("incorrect", "unclear") for v in verdicts):
            status = "weak"
            readiness = min(current_readiness, 30)
            confidence = "low"
        elif any(v == "partial" for v in verdicts):
            status = "weak" if current_readiness < 40 else "practiced"
            readiness = min(max(current_readiness, 35), 50)
            confidence = "low"
        elif any(v == "correct" for v in verdicts):
            status = "practiced"
            readiness = min(max(current_readiness, 40), 55)
            confidence = "medium"
        else:
            updates[sid] = None
            continue

        if had_repair:
            readiness = min(readiness, 55)
            if status != "weak":
                status = "practiced"

        evidence_refs = skill.get("evidence") or []
        new_refs = [e.get("evidence_marker") for e in entries if e.get("evidence_marker")]
        evidence_refs = list(dict.fromkeys(evidence_refs + new_refs))

        updates[sid] = {
            "status": status,
            "readiness": readiness,
            "confidence": confidence,
            "evidence": evidence_refs,
        }
    return updates


def _compute_next_action(
    repo_root: Path | str | None, skill_updates: dict[str, dict[str, Any] | None]
) -> str:
    root = Path(repo_root) if repo_root else ROOT
    skill_map = load_yaml(_state_path(root, "state/SKILL_MAP.yaml"))
    skills = skill_map.get("skills", [])

    # Prefer a weak or blocked skill.
    weak = [s for s in skills if s.get("status") in ("weak", "blocked")]
    if weak:
        s = weak[0]
        return f"Review weak skill {s.get('id')} ({s.get('label') or 'no label'})"

    # Then a due review.
    review_state = load_yaml(_state_path(root, "reviews/REVIEW_STATE.yaml"))
    now = datetime.now(timezone.utc)
    due: list[dict[str, Any]] = []
    for item in review_state.get("review_items", []):
        due_at = item.get("due_at")
        if not due_at:
            continue
        try:
            dt = datetime.fromisoformat(due_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt <= now:
                due.append(item)
        except Exception:
            continue
    if due:
        item = due[0]
        return f"Do due review {item.get('id')} for skill {item.get('skill_id')}"

    # Then a pending skill.
    pending = [s for s in skills if s.get("status") == "pending"]
    if pending:
        s = pending[0]
        return f"Practice pending skill {s.get('id')} ({s.get('label') or 'no label'})"

    return "Choose next study action based on current state."


def build_reconciliation(repo_root: Path | str | None = None) -> dict[str, Any]:
    """Return a reconciliation proposal from the active checkpoint."""
    root = Path(repo_root) if repo_root else ROOT
    checkpoint = load_checkpoint(root)
    metadata = checkpoint["metadata"]
    entries = checkpoint["entries"]

    evidence_items: list[dict[str, Any]] = []
    skill_effects: dict[str, list[dict[str, Any]]] = {}

    for entry in entries:
        ev_id = entry.get("evidence_marker") or entry.get("question_id", "unknown")
        evidence_items.append(
            {
                "evidence_id": ev_id,
                "date": entry.get("ts", now_iso())[:10],
                "target_id": metadata.get("target_id", "unknown"),
                "skill_id": entry.get("skill_id", "unknown"),
                "question_id": entry.get("question_id", "unknown"),
                "question_summary": entry.get("concept", "unknown"),
                "learner_answer_summary": entry.get("answer_summary", ""),
                "verdict": entry.get("verdict", "unclear"),
                "mistake_type": "",
                "explanation": f"Fast-drill entry. Correction: {entry.get('correction_summary') or 'none'}",
                "confidence": entry.get("confidence", "low"),
            }
        )
        sid = entry.get("skill_id")
        if sid:
            skill_effects.setdefault(sid, []).append(entry)

    skill_updates = _compute_skill_updates(root, skill_effects)
    next_action = _compute_next_action(root, skill_updates)

    return {
        "metadata": metadata,
        "evidence_items": evidence_items,
        "skill_updates": skill_updates,
        "study_state_updates": {
            "active_focus.current_topic": metadata.get("drill_type", "drill"),
            "active_focus.next_question": next_action,
        },
        "next_action": next_action,
    }


def _append_evidence_items(repo_root: Path | str | None, items: list[dict[str, Any]]) -> None:
    path = _state_path(repo_root, "state/EVIDENCE_LOG.md")
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    else:
        text = "# Evidence Log\n\n## Evidence items\n\nNone yet."

    for item in items:
        entry = (
            f"\n- **Evidence ID:** {item['evidence_id']}\n"
            f"- **Date:** {item['date']}\n"
            f"- **Target ID:** {item['target_id']}\n"
            f"- **Skill ID:** {item['skill_id']}\n"
            f"- **Question ID:** {item['question_id']}\n"
            f"- **Question summary:** {item['question_summary']}\n"
            f"- **Learner answer summary:** {item['learner_answer_summary']}\n"
            f"- **Verdict:** {item['verdict']}\n"
        )
        if item.get("mistake_type"):
            entry += f"- **Mistake type:** {item['mistake_type']}\n"
        entry += (
            f"- **Explanation:** {item['explanation']}\n"
            f"- **Confidence:** {item['confidence']}\n"
        )

        marker = "## Evidence items\n\nNone yet."
        if marker in text:
            text = text.replace(marker, "## Evidence items" + entry)
        else:
            text += entry
    path.write_text(text, encoding="utf-8")


def _apply_skill_updates(
    repo_root: Path | str | None, updates: dict[str, dict[str, Any] | None]
) -> None:
    path = _state_path(repo_root, "state/SKILL_MAP.yaml")
    skill_map = load_yaml(path)
    for skill in skill_map.get("skills", []):
        sid = skill.get("id")
        update = updates.get(sid)
        if update:
            skill.update(update)
    skill_map.setdefault("metadata", {})["last_updated"] = now_iso()
    save_yaml(path, skill_map)


def _apply_study_state_updates(
    repo_root: Path | str | None,
    study_state_updates: dict[str, Any],
    next_action: str,
) -> None:
    path = _state_path(repo_root, "state/STUDY_STATE.yaml")
    study_state = load_yaml(path)
    active_focus = study_state.setdefault("active_focus", {})
    active_focus["current_topic"] = study_state_updates["active_focus.current_topic"]
    active_focus["next_question"] = next_action
    study_state.setdefault("metadata", {})["last_updated"] = now_iso()
    save_yaml(path, study_state)


def _apply_next_action(repo_root: Path | str | None, next_action: str) -> None:
    path = _state_path(repo_root, "NEXT_ACTIONS.md")
    header = (
        "# NEXT_ACTIONS — Active Queue\n\n"
        "> **Agent-maintained.** This is the single canonical next-action file for the repo.\n\n"
        "## Current next action\n\n"
    )
    path.write_text(header + next_action + "\n", encoding="utf-8")


def write_reconciliation(proposal: dict[str, Any], repo_root: Path | str | None = None) -> None:
    """Write a reconciliation proposal to canonical state files."""
    _append_evidence_items(repo_root, proposal["evidence_items"])
    _apply_skill_updates(repo_root, proposal["skill_updates"])
    _apply_study_state_updates(repo_root, proposal["study_state_updates"], proposal["next_action"])
    _apply_next_action(repo_root, proposal["next_action"])


def print_reconciliation(proposal: dict[str, Any]) -> None:
    print(f"Session: {proposal['metadata'].get('session_id')}")
    print(f"Evidence items to append: {len(proposal['evidence_items'])}")
    for item in proposal["evidence_items"]:
        print(f"  - {item['evidence_id']}: {item['skill_id']} -> {item['verdict']}")
    print("Skill updates:")
    for sid, update in proposal["skill_updates"].items():
        if update:
            print(f"  - {sid}: status={update['status']}, readiness={update['readiness']}")
        else:
            print(f"  - {sid}: unknown skill, evidence only")
    print(f"Next action: {proposal['next_action']}")


def end_drill(apply: bool = False, repo_root: Path | str | None = None) -> tuple[dict[str, Any] | None, int]:
    """Reconcile the active checkpoint. If apply is True, write canonical state."""
    root = Path(repo_root) if repo_root else ROOT
    if _refuse_template(root):
        return None, 2

    path = _state_path(root, "state/ACTIVE_DRILL_SESSION.md")
    if not path.is_file():
        print("No active drill to end.")
        return None, 1

    proposal = build_reconciliation(root)
    if not apply:
        print_reconciliation(proposal)
        print("\nRun with --apply to write canonical state.")
        return proposal, 0

    write_reconciliation(proposal, root)
    path.unlink()
    print("Drill reconciled and checkpoint removed.")
    return proposal, 0


def recover_drill(repo_root: Path | str | None = None) -> tuple[dict[str, Any] | None, int]:
    """Inspect an active checkpoint and recommend resume/reconcile/abort."""
    root = Path(repo_root) if repo_root else ROOT
    path = _state_path(root, "state/ACTIVE_DRILL_SESSION.md")
    if not path.is_file():
        print("No active drill checkpoint to recover.")
        return None, 0

    try:
        checkpoint = load_checkpoint(root)
    except Exception as exc:
        print(f"Error reading checkpoint: {exc}")
        print("Recommendation: abort with audit (log the failure, delete the checkpoint, fall back to normal mode).")
        return None, 1

    metadata = checkpoint["metadata"]
    age_hours = _checkpoint_age_hours(metadata)
    if age_hours is not None and age_hours <= RECOVERY_AGE_HOURS:
        recommendation = "resume"
    else:
        recommendation = "reconcile"

    print(f"Active drill found: {metadata.get('session_id')}")
    print(f"Target ID: {metadata.get('target_id')}")
    print(f"Started at: {metadata.get('started_at')}")
    print(f"Entries: {len(checkpoint['entries'])}")
    if age_hours is not None:
        print(f"Age: {age_hours:.1f} hours")
    print(f"Recommendation: {recommendation}")

    return {
        "checkpoint": checkpoint,
        "recommendation": recommendation,
        "age_hours": age_hours,
    }, 0


def fast_drill_enabled(repo_root: Path | str | None = None) -> bool:
    profile = load_yaml(_state_path(repo_root, "state/LEARNER_PROFILE.yaml"))
    prefs = profile.get("learner_preferences", {})
    return bool(prefs.get("fast_drill_mode", False))


def auto_state_update_during_drills(repo_root: Path | str | None = None) -> bool:
    profile = load_yaml(_state_path(repo_root, "state/LEARNER_PROFILE.yaml"))
    prefs = profile.get("learner_preferences", {})
    return bool(prefs.get("auto_state_update_during_drills", False))


def requires_immediate_reconciliation(
    entry: dict[str, Any], repo_root: Path | str | None = None
) -> bool:
    """Return True if a new checkpoint entry triggers a major state transition."""
    root = Path(repo_root) if repo_root else ROOT
    if entry.get("verdict") not in ("correct", "partial"):
        # Incorrect/unclear answers on weak skills can block promotion; not a major
        # transition, but the caller may still reconcile for safety.
        return False

    skill_map = load_yaml(_state_path(root, "state/SKILL_MAP.yaml"))
    skill = next(
        (s for s in skill_map.get("skills", []) if s.get("id") == entry.get("skill_id")),
        None,
    )
    if not skill:
        return False

    status = skill.get("status")
    readiness = skill.get("readiness")
    if status in ("weak", "blocked") and entry.get("verdict") == "correct":
        # A weak skill answering correctly is a notable event; reconcile to avoid
        # stale canonical state overstating weakness.
        return True
    if isinstance(readiness, (int, float)) and readiness >= 70 and entry.get("verdict") == "partial":
        # A high-readiness skill producing a partial answer is a material change.
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast Drill Mode checkpoint helper for StudyDD")
    sub = parser.add_subparsers(dest="command", required=True)

    start_p = sub.add_parser("start", help="Start a new drill checkpoint")
    start_p.add_argument("--session-id", required=True)
    start_p.add_argument("--target-id", required=True)
    start_p.add_argument("--mode", default="normal")
    start_p.add_argument("--drill-type", default="retrieval_question")
    start_p.add_argument("--source-ref", default="")
    start_p.add_argument(
        "--demo",
        action="store_true",
        help="Allow operation in template mode for testing",
    )

    append_p = sub.add_parser("append", help="Append one graded-answer line")
    append_p.add_argument("--question-id", required=True)
    append_p.add_argument("--skill-id", required=True)
    append_p.add_argument("--concept", required=True)
    append_p.add_argument("--answer-summary", required=True)
    append_p.add_argument("--verdict", required=True)
    append_p.add_argument("--correction-summary", default="")
    append_p.add_argument("--confidence", required=True)
    append_p.add_argument("--evidence-marker", required=True)

    sub.add_parser("status", help="Show active drill status")

    end_p = sub.add_parser("end", help="Reconcile the active checkpoint")
    end_p.add_argument("--apply", action="store_true", help="Write canonical state")

    sub.add_parser("recover", help="Inspect active checkpoint and recommend next step")

    args = parser.parse_args()

    if args.command == "start":
        return start_drill(
            session_id=args.session_id,
            target_id=args.target_id,
            mode=args.mode,
            drill_type=args.drill_type,
            source_ref=args.source_ref,
            demo=args.demo,
        )
    if args.command == "append":
        return append_checkpoint(
            question_id=args.question_id,
            skill_id=args.skill_id,
            concept=args.concept,
            answer_summary=args.answer_summary,
            verdict=args.verdict,
            correction_summary=args.correction_summary,
            confidence=args.confidence,
            evidence_marker=args.evidence_marker,
        )
    if args.command == "status":
        if is_drill_active():
            cp = load_checkpoint()
            print(
                f"Active drill: {cp['metadata'].get('session_id')} "
                f"({len(cp['entries'])} entries)"
            )
            return 0
        print("No active drill.")
        return 0
    if args.command == "end":
        _, rc = end_drill(apply=args.apply)
        return rc
    if args.command == "recover":
        _, rc = recover_drill()
        return rc

    return 1


if __name__ == "__main__":
    sys.exit(main())
