# QUESTION_QUALITY_GOVERNOR.md — Question Quality Gate

This policy defines the quality gate that every generated question must pass before it is shown to the learner.

## Rules

- Every generated question must have a small quality record.
- No authoritative volatile or live question passes the quality gate without a fresh source.
- The answer key must never appear in learner-facing text.
- Scenario questions must test reasoning, not keyword matching.
- Distractors must be plausible but not nonsense.
- The question must match the active study skill.
- The question must match the learner's current level and recent mistakes.
- If the agent is unsure of source freshness or correctness, it must either ask a simpler source-grounded question or perform a source refresh before continuing.
- Learner-facing honesty:
  - When sources are fresh and authoritative: "This question is based on a fresh official source."
  - When sources are stale or absent: "This is conceptual practice only; I have not refreshed current vendor details."

## Question Quality Record Shape

```yaml
question_quality:
  question_id: Q-...
  target_id: ...
  skill_id: ...
  study_skill: ...
  volatility: ...
  source_ids: [...]
  source_freshness_status: fresh | stale | not_required | unverified
  cognitive_level: recall | understand | apply | analyze | evaluate | create
  question_type: scenario | calculation | interpretation | troubleshooting | explanation | production
  answer_key_visibility: private_until_grading
  distractor_quality: plausible
  learner_fit: appropriate
  estimated_difficulty: easy | medium | hard
  generated_from_memory_allowed: true | false
  quality_gate: pass | warn | fail
  quality_gate_reason: ""
  notes: ""
```
