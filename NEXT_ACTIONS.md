# NEXT_ACTIONS — Active Queue

> **Agent-maintained.** This is the single canonical next-action file for the repo.

## Current next action

1. Open a pull request for `feat/fast-drill-mode` after confirming with the user, then merge it into `main` and continue with the agent-driven study loop slice.

## Pending actions

- Run `python3 scripts/check_studydd.py` after initialization or any state change.
- Add weak or uncertain skills to `reviews/REVIEW_QUEUE.md` after evidence exists.
- Build the agent-driven study loop (`feat/agent-session-study-loop`): implement a single-entry wrapper that runs the full StudyDD session lifecycle (verify, read context, choose activity, ask/grade/update, validate, hand off) so agents can start a session with one command.

## Recently completed

- 2026-06-29: Implemented Fast Drill Mode (`feat/fast-drill-mode`): added `docs/superpowers/specs/FAST_DRILL_MODE.md`, `scripts/fast_drill_mode.py`, and tests; wired the speed-layer checkpoint into AGENTS.md and the ask/grade/update/close protocols; added `fast_drill_mode` and `auto_state_update_during_drills` preferences; updated the state manifest, performance budget, context pack, and validator.
- 2026-06-29: Closed the source-check completion flow (`feat/source-check-completion-flow`): refactored `scripts/record_source_check.py` into a reusable `record_source_check(...)` function and wired `scripts/record_activity_result.py` to call it automatically for completed `recent_info_check` activities when `--source-id` is supplied.
- 2026-06-27: Built the source-check completion flow (`feat/source-check-completion-flow`): added `scripts/record_source_check.py` and `protocols/RECORD_SOURCE_CHECK.md` so completed `recent_info_check` metadata is recorded deterministically in `sources/SOURCE_STATE.yaml` and suppresses repeated source-check recommendations.
- 2026-06-27: Integrated source freshness state into next-activity decisions so `recent_info_check` keys off verified source freshness in `sources/SOURCE_STATE.yaml`, not only recent activity type.
- 2026-06-27: Wired the shared next-activity recommendation and auditable `Rule: ...` reason into `scripts/build_context_pack.py`; added focused decision-rule tests.
- 2026-06-27: Improved next-activity selection to recommend among exam-style question, spaced-repetition review, lab/practical exercise, diagram/visual explanation, and recent-info check.
