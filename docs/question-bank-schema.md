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
source_ref: "<source_id or URL>"
public_prompt: |
  The learner-facing question text.
  Do not include the answer key, rubric, or correct label here.
private_answer_key: |
  The agent-only correct answer and reasoning.
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

## Notes

- `public_prompt` must be safe to show the learner.
- `private_answer_key` and `rubric` must never appear in learner-facing surfaces.
- The validator does not require a question bank, but if one exists it checks
  that every required field is present.
- See `protocols/QUESTION_QUALITY.md` for the question-quality gate.
