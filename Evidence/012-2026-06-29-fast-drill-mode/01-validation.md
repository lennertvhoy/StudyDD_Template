# Validation

Local validation run on 2026-06-29.

```bash
python3 scripts/check_studydd.py
python3 scripts/test_fast_drill_mode.py
python3 scripts/test_template_instance_boundary.py
python3 scripts/test_performance_policy.py
python3 scripts/test_context_pack.py
python3 scripts/test_learning_activities.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_compact_state.py
python3 scripts/test_validate_touched_state.py
python3 scripts/test_source_freshness.py
python3 scripts/test_record_source_check.py
```

All passed.

Key checks:
- `check_studydd.py` reports the repo healthy in template mode.
- `scripts/test_fast_drill_mode.py` covers start, append, dry-run/apply reconciliation, weak-skill/due-review next-action selection, crash recovery (resume/reconcile), major-transition detection, and template-mode refusal.
- The template/instance boundary test still passes with the new `state/ACTIVE_DRILL_SESSION.md` manifest entry.
