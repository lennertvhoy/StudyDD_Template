# Validation

The complete immutable upgrade proof passed locally. These final commands
passed once: `python3 scripts/check_studydd.py`,
`python3 scripts/validate_manifest.py --origin-ref HEAD`,
`python3 scripts/test_instantiate_template.py`,
`python3 scripts/test_study_loop_smoke.py`, `python3 scripts/test_compact_state.py`,
`python3 scripts/test_context_pack.py`, `python3 scripts/test_learning_activities.py`,
`python3 scripts/test_next_activity_decision.py`,
`python3 scripts/test_source_freshness.py`,
`python3 scripts/test_cross_platform_paths.py`, Fast Drill checkpoint and
settings migration tests, source-check completion, compatibility-view,
instance-layout, question-quality, privacy, and `git diff --check`.
The only privacy output was the existing soft warning set for scanner keywords
and synthetic invalid-email fixtures. Remote CI was not run.
