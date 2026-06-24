#!/usr/bin/env python3
"""Source freshness gate for StudyDD targets.

Reads sources/SOURCE_STATE.yaml, computes freshness per source for a target,
and reports whether new authoritative questions can be generated.

Does not perform web search or any network calls.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE_STATE_PATH = ROOT / "sources" / "SOURCE_STATE.yaml"
TARGETS_DIR = ROOT / "targets"

VOLATILITY_MAX_AGE_DAYS = {
    "stable": 3650,
    "slow_changing": 730,
    "moderate": 90,
    "volatile": 30,
    "live": 1,
}

AUTHORITY_ORDER = [
    "official",
    "high_authority",
    "instructor",
    "textbook",
    "learner_notes",
    "unverified",
]


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


def parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def read_target_volatility(target_id: str) -> tuple[str, bool]:
    """Return (volatility_class, declared_explicitly)."""
    target_yaml = TARGETS_DIR / target_id / "TARGET.yaml"
    if not target_yaml.is_file():
        return "moderate", False
    data = load_yaml(target_yaml)
    volatility = data.get("volatility")
    if volatility and volatility in VOLATILITY_MAX_AGE_DAYS:
        return volatility, True
    return "moderate", False


def target_id_from_question(question_id: str) -> str | None:
    """Find target_id by scanning target question banks."""
    if not TARGETS_DIR.is_dir():
        return None
    for target_dir in TARGETS_DIR.iterdir():
        if not target_dir.is_dir() or target_dir.name.startswith("."):
            continue
        question_file = target_dir / "questions" / f"{question_id}.yaml"
        if question_file.is_file():
            data = load_yaml(question_file)
            return data.get("target_id") or target_dir.name
    return None


def classify_source(
    source: dict[str, Any], now: datetime, target_volatility: str
) -> tuple[str, str | None]:
    """Return (freshness_status, reason).

    Statuses:
        fresh              — usable and within freshness window.
        stale              — usable but expired or beyond max age.
        unverified         — explicitly marked unusable for questions.
        missing_timestamp  — no expiry or check timestamp available.
    """
    if source.get("usable_for_questions") is False:
        return "unverified", "usable_for_questions is false"

    expires_at = source.get("expires_at")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(str(expires_at))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if now <= expiry:
                return "fresh", None
            return "stale", f"expired at {expires_at}"
        except Exception as exc:
            return "missing_timestamp", f"invalid expires_at: {exc}"

    last_checked_at = source.get("last_checked_at")
    if last_checked_at:
        try:
            checked = datetime.fromisoformat(str(last_checked_at))
            if checked.tzinfo is None:
                checked = checked.replace(tzinfo=timezone.utc)
        except Exception as exc:
            return "missing_timestamp", f"invalid last_checked_at: {exc}"

        volatility = source.get("volatility") or target_volatility
        max_age_days = VOLATILITY_MAX_AGE_DAYS.get(volatility, 90)
        expiry = checked + timedelta(days=max_age_days)
        if now <= expiry:
            return "fresh", None
        return "stale", f"last checked {last_checked_at}; volatility {volatility} max age {max_age_days} days"

    return "missing_timestamp", "no expires_at or last_checked_at"


def authority_rank(authority: str | None) -> int:
    try:
        return AUTHORITY_ORDER.index(str(authority).lower())
    except ValueError:
        return len(AUTHORITY_ORDER)


def build_report(
    target_id: str,
    volatility: str,
    volatility_declared: bool,
    sources: list[dict[str, Any]],
    now: datetime,
) -> tuple[list[str], int]:
    fresh_sources: list[dict[str, Any]] = []
    stale_sources: list[tuple[dict[str, Any], str | None]] = []
    unverified_sources: list[tuple[dict[str, Any], str | None]] = []
    missing_timestamp_sources: list[tuple[dict[str, Any], str | None]] = []

    for source in sources:
        status, reason = classify_source(source, now, volatility)
        if status == "fresh":
            fresh_sources.append(source)
        elif status == "stale":
            stale_sources.append((source, reason))
        elif status == "unverified":
            unverified_sources.append((source, reason))
        else:
            missing_timestamp_sources.append((source, reason))

    lines: list[str] = []
    lines.append("Source freshness check")
    lines.append("")
    lines.append(f"Target: {target_id}")
    lines.append(f"Volatility: {volatility}")
    if not volatility_declared:
        lines.append(
            "Warning: target does not declare volatility; defaulting to moderate."
        )
    lines.append("")

    lines.append("Fresh usable sources:")
    if fresh_sources:
        for source in sorted(fresh_sources, key=lambda s: authority_rank(s.get("authority"))):
            lines.append(f"- {source.get('source_id', '<unknown>')}")
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("Stale sources:")
    if stale_sources:
        for source, reason in stale_sources:
            reason_text = f" — {reason}" if reason else ""
            lines.append(f"- {source.get('source_id', '<unknown>')}{reason_text}")
    else:
        lines.append("(none)")
    lines.append("")

    all_unverified = unverified_sources + missing_timestamp_sources
    lines.append("Unverified sources:")
    if all_unverified:
        for source, reason in all_unverified:
            reason_text = f" — {reason}" if reason else ""
            lines.append(f"- {source.get('source_id', '<unknown>')}{reason_text}")
    else:
        lines.append("(none)")
    lines.append("")

    # Recommendation: prefer highest-authority fresh source.
    lines.append("Recommendation:")
    fresh_official = [s for s in fresh_sources if s.get("authority") in ("official", "high_authority")]
    if fresh_official:
        best = min(fresh_official, key=lambda s: authority_rank(s.get("authority")))
        lines.append(
            f"Use {best.get('authority', 'authoritative')} source {best.get('source_id')} for new authoritative questions."
        )
    elif fresh_sources:
        best = min(fresh_sources, key=lambda s: authority_rank(s.get("authority")))
        lines.append(
            f"Use {best.get('authority', 'available')} source {best.get('source_id')} for new questions, but verify authority."
        )
    else:
        lines.append("No fresh usable sources found.")

    if volatility in ("volatile", "live"):
        lines.append("Do not generate product-current questions from memory.")

    # Exit code: volatile/live targets need at least one fresh usable source.
    exit_code = 0
    if volatility in ("volatile", "live") and not fresh_sources:
        exit_code = 1

    return lines, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check source freshness for StudyDD targets"
    )
    parser.add_argument("--target-id", help="Target ID to check")
    parser.add_argument("--question-id", help="Question ID whose target should be checked")
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help="Allow stale sources; switch to practice-only mode",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="ISO 8601 timestamp with timezone for deterministic checks",
    )
    args = parser.parse_args()

    now = parse_now(args.now)
    source_state = load_yaml(SOURCE_STATE_PATH)
    all_sources: list[dict[str, Any]] = source_state.get("sources") or []

    if args.allow_stale:
        print("Source freshness check")
        print("")
        print("Stale source allowed by override.")
        print("Question mode: practice-only, not authoritative-current.")
        return 0

    target_ids: list[str] = []
    if args.target_id:
        target_ids.append(args.target_id)
    elif args.question_id:
        inferred = target_id_from_question(args.question_id)
        if inferred:
            target_ids.append(inferred)
        else:
            print(f"Could not find target for question {args.question_id}")
            return 1
    else:
        # Default: check every target referenced in SOURCE_STATE.yaml.
        seen = {s.get("target_id") for s in all_sources if s.get("target_id")}
        target_ids = sorted(seen)

    if not target_ids:
        # No targets referenced; nothing to fail.
        print("Source freshness check")
        print("")
        print("No targets referenced in sources/SOURCE_STATE.yaml.")
        print("Nothing to check.")
        return 0

    overall_exit = 0
    output_blocks: list[list[str]] = []

    for target_id in target_ids:
        volatility, declared = read_target_volatility(target_id)
        target_sources = [s for s in all_sources if s.get("target_id") == target_id]
        report_lines, exit_code = build_report(
            target_id, volatility, declared, target_sources, now
        )
        output_blocks.append(report_lines)
        if exit_code != 0:
            overall_exit = exit_code

    # Print a blank line between multiple targets.
    for idx, block in enumerate(output_blocks):
        if idx > 0:
            print("")
        for line in block:
            print(line)

    return overall_exit


if __name__ == "__main__":
    sys.exit(main())
