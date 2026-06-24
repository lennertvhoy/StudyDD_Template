#!/usr/bin/env python3
"""Print the expected touched files for a StudyDD state update operation.

Use this before writing state to stay on the fast path. The script does not
modify any files.
"""

from __future__ import annotations

import argparse
import sys

PLANS = {
    "ask_question": {
        "mode": "fast_path",
        "touched": [
            "state/STUDY_STATE.yaml (active_focus only)",
            ".studydd/state_cache.json (if context pack is rebuilt)",
        ],
        "do_not_touch": [
            "state/EVIDENCE_LOG.md",
            "sessions/SESSION_LOG.md",
            "state/SKILL_MAP.yaml readiness",
            "full raw logs",
        ],
        "validation": [
            "scripts/validate_touched_state.py --active-question <question_id>",
        ],
    },
    "grade_answer": {
        "mode": "fast_path",
        "touched": [
            "state/SKILL_MAP.yaml",
            "state/EVIDENCE_LOG.md",
            ".studydd/state_cache.json",
        ],
        "do_not_touch": [
            "sessions/SESSION_LOG.md until close_session",
            "unrelated target folders",
            "full raw logs",
        ],
        "validation": [
            "scripts/validate_touched_state.py --skill-id <skill_id> --evidence-id <evidence_id>",
        ],
    },
    "schedule_review": {
        "mode": "fast_path",
        "touched": [
            "reviews/REVIEW_STATE.yaml",
            "reviews/REVIEW_QUEUE.md",
            ".studydd/state_cache.json",
        ],
        "do_not_touch": [
            "state/EVIDENCE_LOG.md",
            "sessions/SESSION_LOG.md",
            "unrelated skill maps",
        ],
        "validation": [
            "scripts/validate_touched_state.py --review-id <review_id> --skill-id <skill_id>",
        ],
    },
    "close_session": {
        "mode": "session_boundary",
        "touched": [
            "state/EVIDENCE_LOG.md",
            "sessions/SESSION_LOG.md",
            "state/SKILL_MAP.yaml",
            "state/STUDY_STATE.yaml",
            "state/STUDY_STATUS.md",
            "reviews/REVIEW_QUEUE.md",
            "reviews/REVIEW_STATE.yaml",
            "NEXT_ACTIONS.md",
            "state/CURRENT_CONTEXT.md (via compact_state.py)",
            "state/EVIDENCE_INDEX.yaml (via compact_state.py)",
            "sessions/SESSION_SUMMARIES.md (via compact_state.py)",
            ".studydd/state_cache.json",
        ],
        "do_not_touch": [
            "unrelated target folders",
        ],
        "validation": [
            "scripts/check_studydd.py",
        ],
    },
    "start_session": {
        "mode": "session_boundary",
        "touched": [
            ".studydd/context_pack.md",
            ".studydd/state_cache.json (if compaction runs)",
        ],
        "do_not_touch": [
            "state/EVIDENCE_LOG.md",
            "sessions/SESSION_LOG.md",
            "state/SKILL_MAP.yaml",
        ],
        "validation": [
            "scripts/check_studydd.py",
        ],
    },
    "audit": {
        "mode": "deep_audit",
        "touched": [
            "state/EVIDENCE_LOG.md",
            "sessions/SESSION_LOG.md",
            "reviews/REVIEW_OVERRIDES.md",
            "state/CURRENT_CONTEXT.md",
            "state/EVIDENCE_INDEX.yaml",
            "sessions/SESSION_SUMMARIES.md",
            ".studydd/state_cache.json",
        ],
        "do_not_touch": [
            "nothing without explicit repair plan",
        ],
        "validation": [
            "scripts/check_studydd.py",
        ],
    },
}


def print_plan(operation: str) -> int:
    plan = PLANS.get(operation)
    if not plan:
        print(f"Unknown operation: {operation}")
        print(f"Known operations: {', '.join(sorted(PLANS))}")
        return 1

    print(f"Operation: {operation}")
    print(f"Mode: {plan['mode']}")
    print("")
    print("Expected touched files:")
    for item in plan["touched"]:
        print(f"- {item}")
    print("")
    print("Do not touch:")
    for item in plan["do_not_touch"]:
        print(f"- {item}")
    print("")
    print("Validation:")
    for item in plan["validation"]:
        print(f"- {item}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a StudyDD state update")
    parser.add_argument(
        "--operation",
        required=True,
        choices=sorted(PLANS),
        help="StudyDD operation to plan",
    )
    args = parser.parse_args()
    return print_plan(args.operation)


if __name__ == "__main__":
    sys.exit(main())
