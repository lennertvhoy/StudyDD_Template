# Changed Files

## New files

- `docs/superpowers/specs/FAST_DRILL_MODE.md` — design spec for Fast Drill Mode.
- `scripts/fast_drill_mode.py` — checkpoint helper: `start`, `append`, `status`, `end`, `recover`.
- `scripts/test_fast_drill_mode.py` — tests for the checkpoint lifecycle and crash recovery.
- `Evidence/012-2026-06-29-fast-drill-mode/` — this evidence directory.

## Modified files

- `state/LEARNER_PROFILE.yaml` — added generic defaults:
  - `learner_preferences.fast_drill_mode: true`
  - `learner_preferences.auto_state_update_during_drills: true`
- `state/STATE_MANIFEST.yaml` — added `state/ACTIVE_DRILL_SESSION.md` as a `runtime_checkpoint` instance-boundary file.
- `state/PERFORMANCE_BUDGET.yaml` — added `fast_drill` budget and rules for `fast_drill_ask_question` / `fast_drill_grade_answer`.
- `.gitignore` — ignore `state/ACTIVE_DRILL_SESSION.md`.
- `AGENTS.md` — added Fast Drill Mode to required reads, session flow, and crash-recovery step.
- `protocols/ASK_QUESTION.md` — fast-drill note.
- `protocols/GRADE_ANSWER.md` — checkpoint-append note.
- `protocols/UPDATE_STATE.md` — deferred-update note.
- `protocols/CLOSE_SESSION.md` — reconcile-before-close note.
- `scripts/build_context_pack.py` — added `fast_drill_ask_question` and `fast_drill_grade_answer` task choices and guidance.
- `scripts/check_studydd.py` — added required script entries and allowed generic boolean preference flags in template mode.
- `.github/workflows/validate.yml` — added `scripts/test_fast_drill_mode.py` step.
