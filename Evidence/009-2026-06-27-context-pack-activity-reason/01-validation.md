# Validation

All commands were run from `/home/ff/Documents/Projects/StudyDD` on branch `feat/context-pack-activity-reason`.

## Required commands

```text
python3 scripts/check_studydd.py                         PASS
python3 scripts/test_learning_activities.py              PASS
python3 scripts/test_next_activity_decision.py            PASS
python3 scripts/test_instantiate_template.py              PASS
python3 scripts/test_study_loop_smoke.py                  PASS
python3 scripts/test_compact_state.py                     PASS
python3 scripts/test_context_pack.py                      PASS
python3 scripts/run_demo_replay.py                        PASS
git diff --check                                          PASS
```

## Additional commands

```text
python3 scripts/test_demo_replay.py                       PASS
python3 scripts/plan_learning_activity.py --demo          PASS
```

Validator summary:

```text
All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.
```
