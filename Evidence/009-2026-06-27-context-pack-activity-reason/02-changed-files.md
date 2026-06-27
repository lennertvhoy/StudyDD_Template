# Changed Files Summary

Expected changed files for this slice:

```text
.github/workflows/validate.yml
NEXT_ACTIONS.md
README.md
protocols/LEARNING_ACTIVITY_POLICY.md
protocols/SELECT_NEXT_ACTION.md
scripts/build_context_pack.py
scripts/next_activity_decision.py
scripts/plan_learning_activity.py
scripts/test_context_pack.py
scripts/test_next_activity_decision.py
Evidence/009-2026-06-27-context-pack-activity-reason/
```

Summary:

- Added shared pure decision logic in `scripts/next_activity_decision.py`.
- Updated `scripts/plan_learning_activity.py` to consume the shared decision object while preserving planner output and learner-instance write behavior.
- Updated `scripts/build_context_pack.py` to include a non-mutating next activity recommendation section with activity type, `rule_id`, exact `Rule: ...` reason, expected evidence, and learner-control phrase.
- Added direct rule coverage in `scripts/test_next_activity_decision.py`.
- Extended `scripts/test_context_pack.py` to verify the context pack carries the recommendation reason.
- Added the focused decision test to CI.
- Updated docs and `NEXT_ACTIONS.md` to mark the slice complete and record the next recommended slice.
