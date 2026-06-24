#!/usr/bin/env python3
"""Evidence reference sanity check for StudyDD.

Checks that evidence IDs referenced in skill maps and review queues have
corresponding entries in the evidence log where the log format allows.

Limitations: Markdown free-text evidence logs cannot be strictly parsed. This
script uses simple ID matching and may miss malformed entries.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EVIDENCE_ID_RE = re.compile(r"\bE-\d{8}-\d{3,}\b")


def load_yaml(rel: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        print("PyYAML not installed. Install with: pip install pyyaml")
        return None
    try:
        return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"Could not parse {rel}: {exc}")
        return None


def extract_evidence_ids(text: str) -> set[str]:
    return set(EVIDENCE_ID_RE.findall(text))


def collect_referenced_ids() -> set[str]:
    refs: set[str] = set()

    skill_map = load_yaml("state/SKILL_MAP.yaml")
    if skill_map:
        for skill in skill_map.get("skills") or []:
            for ev in skill.get("evidence") or []:
                refs.update(extract_evidence_ids(str(ev)))

    review_path = ROOT / "reviews/REVIEW_QUEUE.md"
    if review_path.is_file():
        refs.update(extract_evidence_ids(review_path.read_text(encoding="utf-8")))

    return refs


def collect_logged_ids() -> set[str]:
    log_path = ROOT / "state/EVIDENCE_LOG.md"
    if not log_path.is_file():
        return set()
    text = log_path.read_text(encoding="utf-8")
    return extract_evidence_ids(text)


def main() -> int:
    print("StudyDD Evidence Check")
    print("======================")
    print("Limitation: Markdown evidence logs are not strictly parseable.")
    print("This check uses simple ID matching and may miss malformed entries.\n")

    referenced = collect_referenced_ids()
    logged = collect_logged_ids()

    if not referenced:
        print("No evidence IDs referenced in skill map or review queue.")
        return 0

    missing = referenced - logged
    if missing:
        print("Referenced evidence IDs missing from state/EVIDENCE_LOG.md:")
        for eid in sorted(missing):
            print(f"  - {eid}")
        print("\nEvidence check failed.")
        return 1

    print(f"All {len(referenced)} referenced evidence IDs found in state/EVIDENCE_LOG.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
