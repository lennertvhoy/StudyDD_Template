# Source-Grounded Question Quality v1 — Summary

## What changed

Added a source freshness gate, question-quality governor, and learner-adaptation layer to StudyDD_Template.

### New files
- `protocols/SOURCE_FRESHNESS_POLICY.md`
- `protocols/SOURCE_REFRESH_POLICY.md`
- `protocols/QUESTION_QUALITY_GOVERNOR.md`
- `protocols/LEARNER_ADAPTATION_POLICY.md`
- `protocols/LEARNER_FEEDBACK_POLICY.md`
- `sources/SOURCE_STATE.yaml`
- `state/LEARNER_PROFILE.yaml`
- `scripts/check_source_freshness.py`
- `scripts/lint_questions.py`
- `scripts/suggest_study_adjustment.py`
- `scripts/test_source_freshness.py`
- `scripts/test_question_quality.py`
- `scripts/test_learner_adaptation.py`
- `docs/future-model-efficiency.md`

### Modified files
- `docs/question-bank-schema.md`
- `scripts/check_studydd.py`
- `scripts/build_context_pack.py`
- `scripts/run_demo_replay.py`
- `scripts/test_demo_replay.py`
- `AGENTS.md`
- `PROMPTS/coding_agent_start_prompt.md`
- `README.md`
- `.github/workflows/validate.yml`
- `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml`
- `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/questions/Q-DEMO-001.yaml`
- `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml`
- `study_skills/*/SKILL.md`
- `state/STATE_MANIFEST.yaml`

## How the guardrails work

- **Source freshness**: `scripts/check_source_freshness.py` reads `sources/SOURCE_STATE.yaml` and determines whether sources are fresh, stale, expired, missing timestamps, or unverified. Volatile/live targets require fresh official/high-authority sources for authoritative questions.
- **Question quality**: `scripts/lint_questions.py` validates question files, recomputes freshness from `SOURCE_STATE.yaml`, blocks volatile/live `authoritative_current` questions with stale/missing sources, detects answer-key leakage, and enforces `quality_gate`/`quality_gate_reason`.
- **Learner adaptation**: `scripts/suggest_study_adjustment.py` inspects recent evidence and review state and outputs at most one evidence-based recommendation. The learner can accept, modify, or override it.

## Validation

All required tests pass:
- `scripts/test_source_freshness.py`
- `scripts/test_question_quality.py`
- `scripts/test_learner_adaptation.py`
- `scripts/check_studydd.py`
- existing instantiation, create-instance, study-loop-smoke, demo-replay, compact-state, context-pack, study-skills, performance-policy, and validate-touched-state tests.

## Backlog note

Cross-platform dependency setup and consent is tracked as the next platform-hardening concern; it was not implemented in this slice to keep scope focused.
