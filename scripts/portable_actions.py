#!/usr/bin/env python3
"""Typed, read-only StudyDD application actions for StatePort.

The action runner never writes canonical state during planning. Applying the
single supported proposal type is a separate, explicit, transactional command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from next_activity_decision import choose_activity_decision, count_due_reviews, find_weakest_skill, recent_activity_types  # noqa: E402

FORMAT = "studydd.action-result/v1"
PROPOSAL_FORMAT = "studydd.state-change-proposal/v1"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return value if isinstance(value, dict) else {}


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def state_digest(root: Path) -> str:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.relative_to(root).as_posix().startswith(("state/", "reviews/", "activities/", "sessions/", "sources/", "targets/")):
            files[path.relative_to(root).as_posix()] = digest_bytes(path.read_bytes())
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return digest_bytes(encoded)


def due_items(review_state: dict[str, Any], *, include_completed: bool = False) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    items: list[dict[str, Any]] = []
    for item in review_state.get("review_items") or []:
        if not isinstance(item, dict) or (not include_completed and item.get("status") in {"completed", "suspended"}):
            continue
        due_at = item.get("due_at")
        if not due_at:
            continue
        try:
            parsed = datetime.fromisoformat(str(due_at))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if parsed <= now:
            items.append({"id": item.get("id", ""), "skillId": item.get("skill_id", ""), "dueAt": due_at, "status": "overdue" if parsed < now else "due"})
    return sorted(items, key=lambda item: (item["dueAt"], item["id"]))


def action_plan(root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    study_state = load_yaml(root / "state/STUDY_STATE.yaml")
    skill_map = load_yaml(root / "state/SKILL_MAP.yaml")
    activity_state = load_yaml(root / "state/ACTIVITY_STATE.yaml")
    review_state = load_yaml(root / "reviews/REVIEW_STATE.yaml")
    source_state = load_yaml(root / "sources/SOURCE_STATE.yaml")
    templates_data = load_yaml(root / "activities/ACTIVITY_TEMPLATES.yaml")
    target_id = str(study_state.get("active_target_id") or "")
    target = load_yaml(root / "targets" / target_id / "TARGET.yaml") if target_id else {}
    reviews = due_items(review_state)
    weakest = find_weakest_skill(skill_map)
    decision = choose_activity_decision(
        inputs.get("focusArea") or None,
        len(reviews) if inputs.get("includeDueReviews", True) else 0,
        weakest,
        inputs.get("intensity") == "gentle",
        target,
        target.get("study_skill") or "",
        recent_activity_types(activity_state),
        templates_data.get("templates") or [],
        source_state=source_state,
    )
    proposal = {
        "formatVersion": PROPOSAL_FORMAT,
        "proposalId": "proposal-" + hashlib.sha256((target_id + decision.activity_type + state_digest(root)).encode()).hexdigest()[:16],
        "applicationAction": "studydd.plan-next-session/v1",
        "preStateDigest": state_digest(root),
        "operations": [],
        "sensitivity": "private",
        "validation": {"command": "python3 scripts/portable_actions.py --validate-proposal"},
    }
    if inputs.get("includeFastDrillProposal"):
        proposal["operations"] = [{"type": "set_active_activity", "path": "state/ACTIVITY_STATE.yaml", "activity": {"type": "fast_drill", "status": "proposed", "target_id": target_id, "reason": "Requested as an optional bounded proposal."}}]
    return {
        "formatVersion": FORMAT,
        "actionId": "studydd.plan-next-session/v1",
        "selectedActivity": {"type": decision.activity_type, "ruleId": decision.rule_id},
        "rationale": decision.reason,
        "sourceFreshness": {"status": decision.signals.get("source_freshness_status", "not_required"), "ruleId": decision.signals.get("source_freshness_rule_id", decision.rule_id)},
        "dueReviewReferences": reviews,
        "weakAreaReferences": [{"id": weakest.get("id"), "status": weakest.get("status"), "readiness": weakest.get("readiness")} ] if weakest else [],
        "proposedDurationMinutes": max(5, min(240, int(inputs.get("timeAvailableMinutes", 30)))),
        "evidenceRequirement": decision.expected_evidence,
        "stateChangeProposals": [proposal] if proposal["operations"] else [],
        "canonicalStateDigest": state_digest(root),
    }


def review_plan(root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    items = due_items(load_yaml(root / "reviews/REVIEW_STATE.yaml"), include_completed=bool(inputs.get("includeCompleted")))
    overdue = [item for item in items if item["status"] == "overdue"]
    return {"formatVersion": FORMAT, "actionId": "studydd.inspect-due-reviews/v1", "dueCount": len(items), "overdueCount": len(overdue), "items": items, "canonicalStateDigest": state_digest(root)}


def validate_output(value: Any) -> None:
    if not isinstance(value, dict) or value.get("formatVersion") != FORMAT or not isinstance(value.get("actionId"), str):
        raise ValueError("action output must be a typed studydd.action-result/v1 object")
    if value["actionId"] == "studydd.plan-next-session/v1":
        required = {"selectedActivity", "rationale", "sourceFreshness", "dueReviewReferences", "weakAreaReferences", "proposedDurationMinutes", "evidenceRequirement", "stateChangeProposals"}
    elif value["actionId"] == "studydd.inspect-due-reviews/v1":
        required = {"dueCount", "overdueCount", "items"}
    else:
        raise ValueError("unknown StudyDD action")
    if not required <= set(value):
        raise ValueError("action output is missing required fields")


def validate_proposal(value: Any) -> None:
    if not isinstance(value, dict) or value.get("formatVersion") != PROPOSAL_FORMAT:
        raise ValueError("invalid StudyDD proposal format")
    if not isinstance(value.get("preStateDigest"), str) or not value["preStateDigest"].startswith("sha256:"):
        raise ValueError("proposal must bind a pre-state digest")
    for operation in value.get("operations", []):
        if not isinstance(operation, dict) or operation.get("type") != "set_active_activity" or operation.get("path") != "state/ACTIVITY_STATE.yaml":
            raise ValueError("unsupported StudyDD proposal operation")


def apply_proposal(root: Path, proposal: dict[str, Any]) -> dict[str, Any]:
    """Apply only the typed activity operation, with byte restoration on failure."""
    validate_proposal(proposal)
    current_digest = state_digest(root)
    if current_digest != proposal.get("preStateDigest"):
        raise ValueError("proposal pre-state digest does not match the current instance")
    target = root / "state/ACTIVITY_STATE.yaml"
    before = target.read_bytes() if target.is_file() else None
    activity_state = load_yaml(target)
    operations = proposal.get("operations") or []
    if len(operations) != 1:
        raise ValueError("exactly one typed activity operation is required")
    activity = dict(operations[0].get("activity") or {})
    activity.setdefault("assigned_at", datetime.now(timezone.utc).isoformat())
    recent = list(activity_state.get("recent_activities") or [])
    current = activity_state.get("active_activity")
    if isinstance(current, dict) and current.get("id"):
        recent.insert(0, current)
    activity_state["active_activity"] = activity
    activity_state["recent_activities"] = recent[:10]
    activity_state.setdefault("metadata", {})["last_updated"] = datetime.now(timezone.utc).isoformat()
    encoded = yaml.safe_dump(activity_state, sort_keys=False).encode("utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".activity.", delete=False) as handle:
        handle.write(encoded)
        temporary = Path(handle.name)
    try:
        temporary.replace(target)
        check = subprocess.run(["python3", "scripts/check_studydd.py"], cwd=root, capture_output=True, text=True, timeout=30)
        if check.returncode != 0:
            raise ValueError("StudyDD validation failed after proposal apply")
    except Exception:
        if before is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(before)
        raise
    return {"formatVersion": "studydd.state-change-receipt/v1", "proposalId": proposal.get("proposalId"), "preStateDigest": current_digest, "postStateDigest": state_digest(root), "appliedOperation": "set_active_activity", "validation": "passed", "appliedAt": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--action", choices=["plan-next-session", "inspect-due-reviews"], default="plan-next-session")
    parser.add_argument("--inputs", default="{}")
    parser.add_argument("--validate-output", action="store_true")
    parser.add_argument("--validate-proposal", action="store_true")
    parser.add_argument("--apply-proposal", action="store_true")
    args = parser.parse_args()
    if args.validate_output or args.validate_proposal:
        value = json.load(sys.stdin)
        (validate_output if args.validate_output else validate_proposal)(value)
        print(json.dumps({"valid": True, "formatVersion": FORMAT if args.validate_output else PROPOSAL_FORMAT}, sort_keys=True))
        return 0
    if args.apply_proposal:
        print(json.dumps(apply_proposal(args.root, json.load(sys.stdin)), sort_keys=True, separators=(",", ":")))
        return 0
    inputs = json.loads(args.inputs)
    result = action_plan(args.root, inputs) if args.action == "plan-next-session" else review_plan(args.root, inputs)
    validate_output(result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
