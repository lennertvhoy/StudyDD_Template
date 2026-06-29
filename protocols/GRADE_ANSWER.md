# GRADE_ANSWER — Grade The Actual Answer

> **Agent action.** Grade the learner's answer against the private answer key, guided by the active study skill.

This is a **fast-path** operation. Load only the active question, rubric, learner answer, and relevant skill evidence.

In **fast drill mode**, append one compact checkpoint line with `scripts/fast_drill_mode.py append` instead of rewriting canonical state after every answer. Reconcile immediately if a major state transition occurs (e.g., a weak skill answers correctly, readiness crosses a certification threshold, or a source is promoted/demoted).

## Verdicts

- **correct** — fully meets the answer key.
- **partial** — partly correct but missing something important.
- **incorrect** — does not meet the answer key.
- **unclear** — cannot be graded because the answer is ambiguous.
- **override** — learner or human reviewer overrode the grade.

## Context loading

Build a minimal context pack:

```bash
python3 scripts/build_context_pack.py --task grade_answer --skill-id <skill_id> --active-question <question_id>
```

Include the active question, rubric, learner answer, relevant skill evidence from `state/EVIDENCE_INDEX.yaml`, and the active study skill. Open the exact previous answer in `state/EVIDENCE_LOG.md` only when needed.

## Grading Steps

1. Re-read the actual answer.
2. Compare each required element from the answer key.
3. Note what is correct.
4. Note what is missing, wrong, or vague.
5. Choose a verdict.
6. Apply the active study skill's grading emphasis (e.g., strict distractor analysis for IT certification, charity and precision for philosophy, process over final answer for practical lab).
7. Tag the mistake type using `protocols/MISTAKE_TAXONOMY.md` when the answer is not fully correct.
8. Decide whether a repair question is needed.

## Explanation

After grading, explain in plain language:

- what was correct
- what was missing or wrong
- why it matters for the target
- one concrete takeaway

Keep it read-aloud friendly.

## Repair Question

If the answer is partial, incorrect, or unclear, ask one focused repair question before moving on.

- Label it as a repair.
- Target only the gap.
- Do not mix repair questions with new numbered questions.
- After the repair, close the original question.

## Readiness Impact

- A correct answer without repair can move a `pending` skill to `practiced`.
- A partial or repaired answer stays conservative.
- An incorrect answer marks the skill `weak` or `blocked`.
- A single answer does not move any skill to `confirmed`.

## Fast-path validation

After updating state, run targeted validation:

```bash
python3 scripts/validate_touched_state.py --skill-id <skill_id> --evidence-id <evidence_id>
```
