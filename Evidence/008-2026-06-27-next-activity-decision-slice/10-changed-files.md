# Changed Files Summary

`git diff --name-status main..HEAD`:

```
M	NEXT_ACTIONS.md
M	README.md
M	activities/ACTIVITY_TEMPLATES.yaml
A	docs/superpowers/plans/2026-06-27-next-activity-decision-slice.md
A	docs/superpowers/specs/2026-06-27-next-activity-decision-slice-design.md
M	protocols/LEARNING_ACTIVITY_POLICY.md
M	protocols/SELECT_NEXT_ACTION.md
M	scripts/plan_learning_activity.py
M	scripts/test_learning_activities.py
```

**Summary of changes:**

- Added `recent_info_check` activity type and `source_freshness_check` template.
- Extended `scripts/plan_learning_activity.py` to load the active target, check volatility, inspect recent activity types, map study skills to templates, and route to one of five canonical activity categories with explicit `Rule: ...` reasons.
- Added tests covering `recent_info_check`, volatile target routing, practical lab routing, diagram routing, and certification/exam routing.
- Updated protocols (`SELECT_NEXT_ACTION.md`, `LEARNING_ACTIVITY_POLICY.md`), `README.md`, and `NEXT_ACTIONS.md`.
- Added design spec and implementation plan under `docs/superpowers/`.
