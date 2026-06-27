# NEXT_ACTIONS — Active Queue

> **Agent-maintained.** This is the single canonical next-action file for the repo.

## Current next action

1. Wire the active activity recommendation reason into `scripts/build_context_pack.py` and add a focused `scripts/test_next_activity_decision.py` for the decision rules.

## Pending actions

- Run `python3 scripts/check_studydd.py` after initialization or any state change.
- Add weak or uncertain skills to `reviews/REVIEW_QUEUE.md` after evidence exists.

## Recently completed

- 2026-06-27: Improved next-activity selection to recommend among exam-style question, spaced-repetition review, lab/practical exercise, diagram/visual explanation, and recent-info check.
