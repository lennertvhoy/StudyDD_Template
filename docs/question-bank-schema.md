# Question Bank Schema

StudyDD supports an optional per-target question bank under:

```text
targets/<target_id>/questions/<question_id>.yaml
```

A question bank is **not required** in every target. The validator checks any
files that exist, but the template remains valid with an empty `targets/`
folder.

## Required fields

```yaml
id: "<question_id>"
target_id: "<target_id>"
skill_id: "<skill_id>"
cognitive_level: "recall | apply | troubleshoot | choose-best | explain | design"
difficulty: 1-5
# At least one source reference is required.
# Use source_ids (preferred) tied to sources/SOURCE_STATE.yaml, or source_ref (legacy).
source_ref: "<source_id or URL>"   # legacy, still accepted
source_ids:
  - "<source_id>"
public_prompt: |
  The learner-facing question text.
  Do not include the answer key, rubric, or correct label here.
private_answer_key: |
  The agent-only correct answer and reasoning.
  # This field may be a plain string (legacy/simple) or a structured object with
  # correct_answer, rationale, and source_support. The structured form is
  # recommended for volatile/current topics.
rubric:
  - "Required point 1"
  - "Required point 2"
common_traps:
  - "Common distractor 1"
  - "Common distractor 2"
transfer_probe: |
  Optional follow-up scenario that tests transfer.
last_used: "YYYY-MM-DD"
cooldown_days: 7
```

## Optional quality and freshness fields

```yaml
# Legacy single-source reference is still accepted.
source_ref: "<source_id or URL>"

# Preferred for moderate, volatile, and live topics: list source IDs from
# sources/SOURCE_STATE.yaml.
source_ids:
  - mslearn_ai_search_overview

# Volatility class for this specific question. Defaults to the target's declared
# volatility if omitted.
volatility: stable | slow_changing | moderate | volatile | live

# Cached freshness status. The linter/validator recomputes this from
# sources/SOURCE_STATE.yaml; do not trust it blindly.
source_freshness_status: "fresh | stale | not_required | unverified"

# What kind of factual claim this question makes.
question_mode: authoritative_current | conceptual_practice | stale_practice | exam_sim | remediation

# For volatile/current questions, the private answer key should include source
# grounding so it is not just model memory.
private_answer_key:
  correct_answer: "..."
  rationale: "..."
  source_support:
    - source_id: mslearn_ai_search_overview
      checked_at: "2026-06-24T12:00:00+00:00"
      section: "Overview"

# Internal quality gate record. The linter validates these values.
# The top-level question file contains identifiers (id, target_id, skill_id, etc.);
# the question_quality block records quality-specific metadata. The governor
# describes a derived/flattened audit record.
question_quality:
  cognitive_level: "recall | understand | apply | analyze | evaluate | create"
  question_type: "scenario | calculation | interpretation | troubleshooting | explanation | procedural"
  answer_key_visibility: "private_until_grading"
  distractor_quality: "plausible"
  learner_fit: "appropriate"
  estimated_difficulty: "easy | medium | hard"
  generated_from_memory_allowed: "true | false"   # derived/validated, not trusted
  quality_gate: "pass | warn | fail"
  quality_gate_reason: ""
  notes: ""
```

## Notes

- `public_prompt` must be safe to show the learner.
- `private_answer_key` and `rubric` must never appear in learner-facing surfaces.
- The validator does not require a question bank, but if one exists it checks
  that every required field is present.
- See `protocols/QUESTION_QUALITY.md` for the question-quality gate.

## Backward compatibility

- Existing question banks with only `source_ref` continue to validate.
- For moderate, volatile, or live topics, `lint_questions.py` warns when only `source_ref` is used.
- `source_freshness_status` and `generated_from_memory_allowed` are cached hints; the linter
  recomputes the canonical values from `sources/SOURCE_STATE.yaml`.
