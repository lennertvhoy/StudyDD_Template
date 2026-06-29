# Evidence 011 — Changed Files

## Created
- `scripts/record_source_check.py` — canonical writer for completed source-check metadata into `sources/SOURCE_STATE.yaml`; refactored to expose a reusable `record_source_check(...)` function.
- `scripts/test_record_source_check.py` — deterministic tests for the new script and the end-to-end freshness loop.
- `protocols/RECORD_SOURCE_CHECK.md` — usage, privacy, and learner-override guidance.

## Modified
- `sources/SOURCE_STATE.yaml` — documented the new `last_check` schema extension in a comment block.
- `scripts/check_studydd.py` — added new required files, added `last_check` schema validation, and imported `classify_source` from `check_source_freshness.py` to avoid duplicate freshness-window constants.
- `scripts/lint_questions.py` — removed duplicate `VOLATILITY_MAX_AGE_DAYS` and `classify_source`; now imports the canonical versions from `check_source_freshness.py`.
- `scripts/test_question_quality.py` — updated stale comment (`90 days` → `30 days`) and copied `check_source_freshness.py` into temp test trees so the linter import works.
- `protocols/SOURCE_FRESHNESS_POLICY.md` — aligned volatility-window defaults with `check_source_freshness.py` and added a canonical-source reference comment.
- `protocols/LEARNING_ACTIVITY_POLICY.md` — noted that `recent_info_check` completion should write back to `sources/SOURCE_STATE.yaml`.
- `protocols/SELECT_NEXT_ACTION.md` — clarified fresh source state is the primary suppressor of repeated `recent_info_check` recommendations.
- `AGENTS.md` — added `record_source_check.py` to the core architecture list and updated source-freshness agent rules/session flow.
- `README.md` — mentioned the source-check completion workflow and new test command.
- `NEXT_ACTIONS.md` — marked the source-check completion flow complete and points to the next slice.
- `scripts/record_activity_result.py` — added optional `--source-*` flags and automatic handoff to `record_source_check(...)` when a `recent_info_check` activity is completed.
- `scripts/test_learning_activities.py` — added `test_record_recent_info_check_updates_source_state()` covering the automatic handoff.
- `.github/workflows/validate.yml` — added `test_record_source_check.py` and the `--demo` smoke check.
- `docs/superpowers/plans/2026-06-24-source-grounded-question-quality-plan.md` — updated stale `VOLATILITY_MAX_AGE_DAYS` literal to match canonical values.
