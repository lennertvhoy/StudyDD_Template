# Evidence 011 — Validation

All commands were run on the feature branch and passed.

```bash
python3 scripts/check_studydd.py
python3 scripts/test_learning_activities.py
python3 scripts/test_next_activity_decision.py
python3 scripts/test_source_freshness.py
python3 scripts/test_record_source_check.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_compact_state.py
python3 scripts/test_context_pack.py
python3 scripts/test_question_quality.py
python3 scripts/plan_learning_activity.py --demo
python3 scripts/record_source_check.py --demo
python3 scripts/run_demo_replay.py
python3 scripts/test_demo_replay.py
git diff --check
python3 scripts/agent_privacy_check.py
```

Results:
- `scripts/check_studydd.py` — healthy
- `scripts/test_record_source_check.py` — 13/13 tests passed
- `scripts/test_source_freshness.py` — all tests passed
- `scripts/test_next_activity_decision.py` — all tests passed
- `scripts/test_learning_activities.py` — all tests passed
- `scripts/test_context_pack.py` — all tests passed
- `scripts/test_question_quality.py` — all tests passed
- `scripts/test_instantiate_template.py` — passed
- `scripts/test_study_loop_smoke.py` — passed
- `scripts/test_compact_state.py` — passed
- `scripts/test_demo_replay.py` — passed
- `scripts/run_demo_replay.py` — completed successfully
- `scripts/plan_learning_activity.py --demo` — exit 0
- `scripts/record_source_check.py --demo` — exit 0, demo output printed
- `git diff --check` — no whitespace errors
- `scripts/agent_privacy_check.py` — completed in soft mode with only expected keyword warnings in existing scanner scripts
