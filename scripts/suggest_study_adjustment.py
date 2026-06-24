#!/usr/bin/env python3
"""Suggest at most one StudyDD adaptation based on recent evidence and reviews.

Usage:
    python3 scripts/suggest_study_adjustment.py
    python3 scripts/suggest_study_adjustment.py --demo
    python3 scripts/suggest_study_adjustment.py --now "2026-06-24T12:00:00+02:00"

Exit code is always 0 in normal cases.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_LOG_PATH = ROOT / "state" / "EVIDENCE_LOG.md"
REVIEW_STATE_PATH = ROOT / "reviews" / "REVIEW_STATE.yaml"

WEAK_VERDICTS = {"partial", "incorrect", "unclear", "wrong"}
RECENT_DAYS = 30

DEMO_OUTPUT = """StudyDD suggestion:

You missed a scenario tradeoff. Next time, use a short comparison drill.

Why:
The last weak evidence item involved choosing between similar services.

Learner control:
You can accept, modify, or override this.
"""


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        return {}

    if not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _make_field_pattern() -> re.Pattern[str]:
    # Evidence log fields use bold labels with the colon inside the bold:
    # "- **Date:** value". Capture the field name before the colon and the
    # value until the next field or end of chunk.
    return re.compile(r"- \*\*([^*]+?):\*\*[ \t]+(.*?)(?=\n- \*\*|\Z)", re.DOTALL)


def parse_evidence_items(text: str) -> list[dict[str, str]]:
    """Parse bullet-style evidence items from EVIDENCE_LOG.md."""
    if not text:
        return []

    # Split on "- **Date:**" so each chunk is one item.
    parts = re.split(r"\n- \*\*Date:\*\*", text)
    if len(parts) < 2:
        return []

    field_re = _make_field_pattern()
    items: list[dict[str, str]] = []
    for raw in parts[1:]:
        # Re-add the delimiter so the first field is captured like the rest.
        chunk = "- **Date:**" + raw
        fields: dict[str, str] = {}
        for match in field_re.finditer(chunk):
            key = match.group(1).strip()
            value = match.group(2).strip()
            fields[key] = value
        if fields:
            items.append(fields)
    return items


def item_date(fields: dict[str, str]) -> datetime | None:
    raw = fields.get("Date", "").strip()
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def item_mistake_tags(fields: dict[str, str]) -> list[str]:
    raw = fields.get("Mistake type", "").strip()
    if not raw:
        return []
    # Tags are hyphenated; split on commas or whitespace.
    tags = [t.strip().lower() for t in re.split(r"[\s,]+", raw) if t.strip()]
    return tags


def is_weak_evidence(fields: dict[str, str]) -> bool:
    verdict = fields.get("Verdict", "").strip().lower()
    return any(weak in verdict for weak in WEAK_VERDICTS)


def count_recent_mistakes(
    items: list[dict[str, str]], now: datetime
) -> dict[str, int]:
    cutoff = now - timedelta(days=RECENT_DAYS)
    counts: dict[str, int] = {}
    for fields in items:
        if not is_weak_evidence(fields):
            continue
        dt = item_date(fields)
        if dt is not None and dt < cutoff:
            continue
        for tag in item_mistake_tags(fields):
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def topic_for_tag(tag: str) -> str:
    """Convert a canonical mistake tag into a learner-facing topic phrase."""
    if tag.endswith("-confusion"):
        tag = tag[: -len("-confusion")]
    return tag


def why_for_tag(tag: str, count: int) -> str:
    topic = topic_for_tag(tag)
    item_label = "item" if count == 1 else "items"
    if tag == "service-boundary-confusion":
        return (
            f"The last {count} weak evidence {item_label} involve choosing between similar services."
        )
    if tag == "missed-constraint":
        return f"The last {count} weak evidence {item_label} miss stated constraints."
    if tag == "stale-source-assumption":
        return f"The last {count} weak evidence {item_label} rely on stale source assumptions."
    if tag == "overconfident-guess":
        return f"The last {count} weak evidence {item_label} look like confident guesses."
    if tag == "vague-answer":
        return f"The last {count} weak evidence {item_label} are too vague to count as mastery."
    return f"The last {count} weak evidence {item_label} relate to {topic}."


def build_evidence_recommendation(tag: str, count: int) -> str:
    topic = topic_for_tag(tag)
    strength = "strong" if count >= 3 else "moderate"
    adjustment = (
        "Do two short comparison drills before adding new material."
        if tag == "service-boundary-confusion"
        else "Do a focused review drill before adding new material."
    )
    why = why_for_tag(tag, count)

    return (
        f"StudyDD suggestion:\n\n"
        f"You keep missing {topic} questions. Recommended adjustment:\n"
        f"{adjustment}\n\n"
        f"Why:\n"
        f"{why}\n\n"
        f"Recommendation strength: {strength}\n\n"
        f"Learner control:\n"
        f"You can accept, modify, or override this."
    )


def count_overdue_reviews(review_state: dict[str, Any], now: datetime) -> int:
    items = review_state.get("review_items") or []
    overdue = 0
    for item in items:
        due_at_str = item.get("due_at")
        status = item.get("status")
        if status in ("completed", "suspended"):
            continue
        if not due_at_str:
            continue
        try:
            due_at = datetime.fromisoformat(due_at_str)
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=timezone.utc)
            if due_at <= now:
                overdue += 1
        except Exception:
            continue
    return overdue


def build_review_recommendation(overdue_count: int) -> str:
    return (
        f"StudyDD suggestion:\n\n"
        f"You have overdue reviews. Recommended adjustment:\n"
        f"Do your due reviews before adding new material.\n\n"
        f"Why:\n"
        f"There are {overdue_count} review item(s) past their due date.\n\n"
        f"Recommendation strength: moderate\n\n"
        f"Learner control:\n"
        f"You can accept, modify, or override this."
    )


def no_recommendation() -> str:
    return "StudyDD suggestion:\nNo recommendation: insufficient evidence."


def load_evidence_text() -> str:
    if not EVIDENCE_LOG_PATH.is_file():
        return ""
    try:
        return EVIDENCE_LOG_PATH.read_text(encoding="utf-8")
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Suggest at most one StudyDD adaptation"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Print deterministic demo output"
    )
    parser.add_argument(
        "--now", default=None, help="ISO 8601 timestamp with timezone for deterministic checks"
    )
    args = parser.parse_args()

    if args.demo:
        print(DEMO_OUTPUT, end="")
        return 0

    now = parse_now(args.now)

    evidence_text = load_evidence_text()
    items = parse_evidence_items(evidence_text)
    mistake_counts = count_recent_mistakes(items, now)

    strong_tag: str | None = None
    moderate_tag: str | None = None
    for tag, count in mistake_counts.items():
        if count >= 3:
            strong_tag = tag
            break
        if count == 2 and moderate_tag is None:
            moderate_tag = tag

    if strong_tag is not None:
        print(build_evidence_recommendation(strong_tag, mistake_counts[strong_tag]))
        return 0

    review_state = load_yaml(REVIEW_STATE_PATH)
    overdue_count = count_overdue_reviews(review_state, now)
    if overdue_count > 0:
        print(build_review_recommendation(overdue_count))
        return 0

    if moderate_tag is not None:
        print(build_evidence_recommendation(moderate_tag, mistake_counts[moderate_tag]))
        return 0

    print(no_recommendation())
    return 0


if __name__ == "__main__":
    sys.exit(main())
