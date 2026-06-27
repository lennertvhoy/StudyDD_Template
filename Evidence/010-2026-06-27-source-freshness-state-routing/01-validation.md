# Validation

All commands were run from `/home/ff/Documents/Projects/StudyDD` on branch `feat/source-freshness-state-routing`.

## Required commands

```text
python3 scripts/check_studydd.py                         PASS
python3 scripts/test_learning_activities.py              PASS
python3 scripts/test_next_activity_decision.py           PASS
python3 scripts/test_source_freshness.py                 PASS
python3 scripts/test_instantiate_template.py             PASS
python3 scripts/test_study_loop_smoke.py                 PASS
python3 scripts/test_compact_state.py                    PASS
python3 scripts/test_context_pack.py                     PASS
python3 scripts/run_demo_replay.py                       PASS
python3 scripts/test_demo_replay.py                      PASS
python3 scripts/plan_learning_activity.py --demo         PASS
git diff --check                                         PASS
```

## Additional commands

```text
python3 scripts/check_source_freshness.py --demo         N/A (no --demo flag)
```

`scripts/check_source_freshness.py` supports `--target-id`, `--question-id`, `--allow-stale`, and `--now`. No `--demo` argument is implemented; the demo path instead invokes the source-freshness check via `scripts/run_demo_replay.py` and `scripts/test_demo_replay.py`.

## Command output highlights

### `python3 scripts/check_studydd.py`

```text
StudyDD validation
==================

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.
```

### `python3 scripts/test_source_freshness.py`

```text
Running test_volatile_fresh_official_passes...            PASSED
Running test_volatile_stale_source_fails...               PASSED
Running test_stable_target_no_refresh_required...         PASSED
Running test_no_web_search...                             PASSED
Running test_allow_stale_practice_only...                 PASSED
Running test_now_deterministic...                         PASSED
Running test_target_freshness_summary_missing_state...    PASSED
Running test_target_freshness_summary_fresh_inside_window... PASSED
Running test_target_freshness_summary_stale_outside_window... PASSED
Running test_target_freshness_summary_malformed_timestamp... PASSED
Running test_target_freshness_summary_stable_no_sources... PASSED
Running test_target_freshness_summary_stable_with_valid_source... PASSED
Running test_live_target_window_one_day...                PASSED
Running test_volatile_target_window_seven_days...         PASSED
Running test_moderate_target_window_thirty_days...        PASSED
Running test_freshness_window_days_override...            PASSED
Running test_target_freshness_summary_multiple_sources_aggregate... PASSED
Running test_usable_for_questions_false_counts_unverified... PASSED
Running test_expires_at_overrides_window...               PASSED

All source freshness tests passed.
```

### `python3 scripts/test_next_activity_decision.py`

```text
Running test_due_review_beats_everything
Running test_due_review_beats_source_freshness
Running test_volatile_target_routes_to_recent_info_check
Running test_recent_info_check_prevents_immediate_repeat
Running test_fresh_source_allows_retrieval_question_for_volatile_target
Running test_stale_source_triggers_recent_info_check
Running test_missing_source_state_triggers_recent_info_check_when_no_recent_check
Running test_missing_source_state_obeys_recent_activity_fallback
Running test_malformed_timestamp_triggers_recent_info_check
Running test_unverified_source_triggers_recent_info_check
Running test_moderate_target_missing_source_triggers_recent_info_check
Running test_live_target_stale_source_triggers_recent_info_check
Running test_stable_target_ignores_missing_source_state
Running test_stable_explicit_requirement_triggers_recent_info_check
Running test_stable_with_requires_recent_info_and_stale_source_triggers_recent_info_check
Running test_empty_source_state_recent_activity_fallback
Running test_freshness_window_days_override_shortens_window
Running test_source_freshness_signals_populated
Running test_reason_starts_with_rule
Running test_template_mode_no_target_skips_source_freshness
Running test_practical_skill_routes_to_practical_lab
Running test_conceptual_skill_routes_to_diagram
Running test_certification_practiced_routes_to_retrieval_question
Running test_weak_skill_fallback_routes_to_paper_exercise
Running test_blocked_skill_fallback_routes_to_explain_back
Running test_low_energy_fallback_routes_to_explain_back
Next activity decision tests passed.
```

### `python3 scripts/test_learning_activities.py`

```text
Running test_required_files_exist...                      passed
Running test_activity_state_is_generic_in_template_mode... passed
Running test_activity_templates_parse...                  passed
Running test_recent_info_check_activity_type_exists...    passed
Running test_plan_recommends_recent_info_check_for_volatile_target... passed
Running test_plan_recommends_recent_info_check_for_stale_source... passed
Running test_plan_recommends_lab_for_practical_skill...   passed
Running test_plan_recommends_diagram_for_conceptual_skill... passed
Running test_plan_recommends_exam_question_for_certification_target... passed
Running test_plan_includes_source_freshness_for_fresh_volatile_target... passed
Running test_plan_learning_activity_demo...               passed
Running test_voice_note_analyzer...                       passed
Running test_presentation_analyzer...                     passed
Running test_context_pack_includes_active_activity...     passed
Running test_demo_replay_mentions_non_question_activity... passed
Running test_record_activity_result_on_temp_instance...   passed
Running test_full_validator_passes...                     passed

All learning activity tests passed.
```

### `python3 scripts/test_context_pack.py`

```text
Test: start_session includes canonical state and active study skill          passed
Test: start_session skips raw logs by default                                passed
Test: start_session includes due review                                      passed
Test: start_session includes next activity recommendation reason             passed
Test: start_session includes source freshness status                         passed
Test: context pack surfaces stale source freshness                           passed
Test: audit includes raw log references                                      passed
Test: grade context includes relevant skill, not every skill                 passed
Test: context pack is gitignored                                             passed

Context pack test passed.
```

### `python3 scripts/run_demo_replay.py` and `python3 scripts/test_demo_replay.py`

Both completed the full demo replay, including the source-freshness gate, context-pack build, question/grade/update cycle, non-question activity planning, review scheduling, override recording, and final validation.

```text
StudyDD demo replay
===================

1. Created learner instance from template.
...
21. Validation passed.
```

### `python3 scripts/plan_learning_activity.py --demo`

```text
StudyDD recommendation: paper exercise.

Reason:
The learner has missed this skill twice and answered too quickly. A short written exercise is more useful than another chat question.

Task:
Solve 5 problems on paper and upload a photo or type your answers.

Expected evidence:
photo or typed answers

Learner control:
You can accept, modify, or override this.
```

### `git diff --check`

No whitespace errors reported.

## Validator summary

```text
All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.
```
