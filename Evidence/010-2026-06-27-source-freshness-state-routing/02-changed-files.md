# Changed Files Summary

Expected changed files for this slice:

```text
AGENTS.md
NEXT_ACTIONS.md
README.md
protocols/LEARNING_ACTIVITY_POLICY.md
protocols/SELECT_NEXT_ACTION.md
scripts/build_context_pack.py
scripts/check_source_freshness.py
scripts/next_activity_decision.py
scripts/plan_learning_activity.py
scripts/test_context_pack.py
scripts/test_learning_activities.py
scripts/test_next_activity_decision.py
scripts/test_source_freshness.py
Evidence/010-2026-06-27-source-freshness-state-routing/
```

Summary:

- Added deterministic source-freshness evaluation to `scripts/check_source_freshness.py` with per-target volatility windows, official/unverified source tiers, `expires_at` overrides, and a machine-readable summary object.
- Added shared routing logic in `scripts/next_activity_decision.py` so `volatile`/`moderate`/`live` targets route to a `recent_info_check` activity when no fresh usable source exists, while fresh sources allow normal retrieval questions.
- Updated `scripts/plan_learning_activity.py` to consume the source-freshness summary and emit a `recent_info_check` recommendation with `Rule:` reason and `source_freshness_*` rule IDs.
- Updated `scripts/build_context_pack.py` to surface source-freshness status in the context pack, including fresh/stale/missing source lists and the recommendation rule.
- Added focused tests in `scripts/test_source_freshness.py` covering official/unverified/stale/missing/expires-at/aggregate cases.
- Extended `scripts/test_next_activity_decision.py` with routing tests for fresh, stale, missing, malformed, unverified, and stable-target scenarios.
- Extended `scripts/test_learning_activities.py` to verify `recent_info_check` recommendations and source-freshness signaling.
- Extended `scripts/test_context_pack.py` to verify source-freshness status is surfaced in the context pack and stale sources are reported.
- Updated docs and `NEXT_ACTIONS.md` to record the slice and point to the next recommended slice.
