#!/usr/bin/env python3
"""Record a completed source freshness check for a StudyDD instance.

This writer records source metadata only. It does not fetch sources, update
learner evidence, or alter canonical study status. Freshness is classified by
``scripts/check_source_freshness.py``; this module only records the completed
check and its provenance.
"""

from __future__ import annotations

import argparse
import copy
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - repository requirements provide it.
    yaml = None  # type: ignore[assignment]

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from check_source_freshness import (  # noqa: E402
    AUTHORITY_ORDER,
    SOURCE_CHECK_OUTCOMES,
    VOLATILITY_MAX_AGE_DAYS,
)
from studydd_runtime import RuntimeBoundaryError, repository_mode  # noqa: E402


ROOT = SCRIPT_DIR.parent
SOURCE_STATE_RELATIVE = Path("sources/SOURCE_STATE.yaml")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
VOLATILITY_VALUES = set(VOLATILITY_MAX_AGE_DAYS) | {"stable"}
class SourceCheckError(ValueError):
    """Raised for invalid source-check input or state."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SourceCheckError("PyYAML is required")
    if not path.is_file():
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SourceCheckError(f"could not read {path}: {exc}") from exc
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise SourceCheckError(f"{path} must contain a YAML mapping")
    return value


def parse_iso_timestamp(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SourceCheckError(f"{field} must be a non-empty ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise SourceCheckError(f"{field} is not a valid ISO 8601 timestamp: {exc}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_id(value: str, field: str) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise SourceCheckError(
            f"{field} must match ^[A-Za-z0-9][A-Za-z0-9_-]*$"
        )


def validate_inputs(
    source_id: str,
    target_id: str | None,
    outcome: str,
    checked_at: str,
    expires_at: str | None,
    authority: str,
    volatility: str | None,
    checked_by: str,
    freshness_window_days: int | None,
) -> tuple[datetime, datetime | None]:
    validate_id(source_id, "source_id")
    if target_id is not None:
        validate_id(target_id, "target_id")
    if outcome not in SOURCE_CHECK_OUTCOMES:
        raise SourceCheckError(
            f"outcome must be one of {sorted(SOURCE_CHECK_OUTCOMES)}"
        )
    if authority not in AUTHORITY_ORDER:
        raise SourceCheckError(f"authority must be one of {AUTHORITY_ORDER}")
    if volatility is not None and volatility not in VOLATILITY_VALUES:
        raise SourceCheckError(f"volatility must be one of {sorted(VOLATILITY_VALUES)}")
    if checked_by not in {"agent", "learner"}:
        raise SourceCheckError("checked_by must be 'agent' or 'learner'")
    if freshness_window_days is not None and freshness_window_days <= 0:
        raise SourceCheckError("freshness_window_days must be a positive integer")

    checked = parse_iso_timestamp(checked_at, "checked_at")
    expires = None
    if expires_at is not None:
        expires = parse_iso_timestamp(expires_at, "expires_at")
        if expires < checked:
            raise SourceCheckError("expires_at must be >= checked_at")
    return checked, expires


def normalize_state(value: dict[str, Any]) -> dict[str, Any]:
    state = copy.deepcopy(value)
    sources = state.setdefault("sources", [])
    if not isinstance(sources, list):
        raise SourceCheckError("sources/SOURCE_STATE.yaml 'sources' must be a list")
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise SourceCheckError("source entries must be mappings")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise SourceCheckError("source entries require a non-empty id")
        if source_id in seen:
            raise SourceCheckError(f"duplicate source id: {source_id}")
        seen.add(source_id)
    metadata = state.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        raise SourceCheckError("metadata must be a mapping")
    return state


def find_source(state: dict[str, Any], source_id: str) -> dict[str, Any] | None:
    return next(
        (source for source in state["sources"] if source.get("id") == source_id),
        None,
    )


def resolve_target_id(existing: dict[str, Any] | None, target_id: str | None) -> str | None:
    if existing is None:
        if target_id is None:
            raise SourceCheckError("target_id is required when creating a source")
        return target_id
    target_ids = existing.get("target_ids")
    if isinstance(target_ids, list) and target_ids:
        if not all(isinstance(item, str) and item for item in target_ids):
            raise SourceCheckError("existing source target_ids must be non-empty strings")
        return target_ids[0]
    if target_id is None:
        raise SourceCheckError("existing source has no target_id; provide target_id")
    return target_id


def build_source_entry(
    source_id: str,
    target_id: str,
    *,
    existing: dict[str, Any] | None,
    outcome: str,
    summary: str,
    evidence_id: str,
    activity_id: str,
    checked_by: str,
    checked_at: str,
    expires_at: str | None,
    authority: str,
    volatility: str | None,
    freshness_window_days: int | None,
    usable_for_questions: bool | None,
) -> dict[str, Any]:
    if existing is None:
        source: dict[str, Any] = {
            "id": source_id,
            "target_ids": [target_id],
            "authority": authority,
            "volatility": volatility or "moderate",
            "usable_for_questions": True if usable_for_questions is None else usable_for_questions,
        }
        if freshness_window_days is not None:
            source["freshness_window_days"] = freshness_window_days
    else:
        source = copy.deepcopy(existing)
        if not source.get("target_ids"):
            source["target_ids"] = [target_id]

    if volatility is not None:
        source["volatility"] = volatility
    if usable_for_questions is not None:
        source["usable_for_questions"] = usable_for_questions

    if outcome == "fresh":
        source["last_checked_at"] = checked_at
        if expires_at is None:
            source.pop("expires_at", None)
        else:
            source["expires_at"] = expires_at

    source["last_check"] = {
        "checked_at": checked_at,
        "outcome": outcome,
        "summary": summary,
        "evidence_id": evidence_id,
        "activity_id": activity_id,
        "checked_by": checked_by,
    }
    return source


def atomic_write_yaml(path: Path, value: dict[str, Any]) -> bool:
    """Replace a YAML file atomically, skipping byte-identical content."""
    if yaml is None:
        raise SourceCheckError("PyYAML is required")
    content = yaml.safe_dump(value, sort_keys=False, allow_unicode=False)
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        temporary = None
        try:
            directory_fd = os.open(path.parent, os.O_DIRECTORY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
    return True


def demo() -> str:
    return (
        "Source check demo (no file written)\n"
        "  source_id: demo-official\n"
        "  target_id: demo-target\n"
        "  outcome: fresh\n"
        "  checked_at: 2026-07-01T12:00:00+00:00\n"
    )


def record_source_check(
    source_id: str,
    *,
    target_id: str | None = None,
    outcome: str = "fresh",
    summary: str = "",
    evidence_id: str = "",
    activity_id: str = "",
    checked_by: str = "agent",
    checked_at: str | None = None,
    expires_at: str | None = None,
    authority: str = "official",
    volatility: str | None = None,
    freshness_window_days: int | None = None,
    usable_for_questions: bool | None = None,
    dry_run: bool = False,
    repo_root: str | Path | None = None,
) -> int:
    checked_at = checked_at or now_iso()
    try:
        _checked, _expires = validate_inputs(
            source_id,
            target_id,
            outcome,
            checked_at,
            expires_at,
            authority,
            volatility,
            checked_by,
            freshness_window_days,
        )
        root = Path(repo_root).resolve() if repo_root else ROOT
        try:
            mode = repository_mode(root)
        except RuntimeBoundaryError as exc:
            raise SourceCheckError(str(exc)) from exc
        state_path = root / SOURCE_STATE_RELATIVE
        state = normalize_state(load_yaml(state_path))
        existing = find_source(state, source_id)
        resolved_target_id = resolve_target_id(existing, target_id)
        assert resolved_target_id is not None
        source = build_source_entry(
            source_id,
            resolved_target_id,
            existing=existing,
            outcome=outcome,
            summary=summary,
            evidence_id=evidence_id,
            activity_id=activity_id,
            checked_by=checked_by,
            checked_at=checked_at,
            expires_at=expires_at,
            authority=authority,
            volatility=volatility,
            freshness_window_days=freshness_window_days,
            usable_for_questions=usable_for_questions,
        )
        if dry_run:
            print("Dry-run: no file written")
            print(yaml.safe_dump(source, sort_keys=False), end="")
            return 0
        if mode != "learner_instance":
            print(
                f"Write refused: repository mode is {mode!r}; "
                "source checks may only be recorded in learner_instance mode."
            )
            return 2

        next_state = copy.deepcopy(state)
        if existing is None:
            next_state["sources"].append(source)
        else:
            for index, item in enumerate(next_state["sources"]):
                if item.get("id") == source_id:
                    next_state["sources"][index] = source
                    break
        next_state["metadata"]["last_updated"] = checked_at
        next_state["metadata"]["updated_by"] = "record_source_check.py"
        changed = atomic_write_yaml(state_path, next_state)
        print(f"{'Recorded' if changed else 'Already recorded'} source check for {source_id}")
        print(f"  outcome: {outcome}")
        print(f"  source_state: {SOURCE_STATE_RELATIVE}")
        return 0
    except (OSError, SourceCheckError) as exc:
        print(f"Source check failed: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_id", nargs="?")
    parser.add_argument("--target-id")
    parser.add_argument("--outcome", default="fresh")
    parser.add_argument("--summary", default="")
    parser.add_argument("--evidence-id", default="")
    parser.add_argument("--activity-id", default="")
    parser.add_argument("--checked-by", default="agent")
    parser.add_argument("--checked-at", default=None)
    parser.add_argument("--expires-at", default=None)
    parser.add_argument("--authority", default="official")
    parser.add_argument("--volatility", default=None)
    parser.add_argument("--freshness-window-days", type=int, default=None)
    usable = parser.add_mutually_exclusive_group()
    usable.add_argument("--usable-for-questions", dest="usable_for_questions", action="store_true")
    usable.add_argument("--not-usable-for-questions", dest="usable_for_questions", action="store_false")
    parser.set_defaults(usable_for_questions=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.demo:
        print(demo(), end="")
        return 0
    if not args.source_id:
        parser.error("source_id is required unless --demo is used")
    return record_source_check(
        args.source_id,
        target_id=args.target_id,
        outcome=args.outcome,
        summary=args.summary,
        evidence_id=args.evidence_id,
        activity_id=args.activity_id,
        checked_by=args.checked_by,
        checked_at=args.checked_at,
        expires_at=args.expires_at,
        authority=args.authority,
        volatility=args.volatility,
        freshness_window_days=args.freshness_window_days,
        usable_for_questions=args.usable_for_questions,
        dry_run=args.dry_run,
        repo_root=args.repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
