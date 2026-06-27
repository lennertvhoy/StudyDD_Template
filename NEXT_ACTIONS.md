# NEXT_ACTIONS — Active Queue

> **Agent-maintained.** This is the single canonical next-action file for the repo.

## Current next action

1. Build the activity-completion state flow (`feat/activity-completion-state-flow`): wire `scripts/record_activity_result.py` and `scripts/record_source_check.py` more tightly into session close so completed activities always update summaries, context, and the next action deterministically.

## Pending actions

- Run `python3 scripts/check_studydd.py` after initialization or any state change.
- Add weak or uncertain skills to `reviews/REVIEW_QUEUE.md` after evidence exists.

## Recently completed

- 2026-06-27: Built the source-check completion flow (`feat/source-check-completion-flow`): added `scripts/record_source_check.py` and `protocols/RECORD_SOURCE_CHECK.md` so completed `recent_info_check` metadata is recorded deterministically in `sources/SOURCE_STATE.yaml` and suppresses repeated source-check recommendations.
- 2026-06-27: Integrated source freshness state into next-activity decisions so `recent_info_check` keys off verified source freshness in `sources/SOURCE_STATE.yaml`, not only recent activity type.
- 2026-06-27: Wired the shared next-activity recommendation and auditable `Rule: ...` reason into `scripts/build_context_pack.py`; added focused decision-rule tests.
- 2026-06-27: Improved next-activity selection to recommend among exam-style question, spaced-repetition review, lab/practical exercise, diagram/visual explanation, and recent-info check.
