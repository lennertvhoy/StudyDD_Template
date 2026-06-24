# ASK_QUESTION — Ask Exactly One Question

> **Agent action.** Use this protocol every time you ask a question.

## Before Asking

Internally define:

- target ID
- skill ID
- question ID (`Q-YYYYMMDD-NNN` or session-local `Q-NNN`)
- objective (what the question tests)
- cognitive level: recall, apply, troubleshoot, choose-best, explain, design
- difficulty (1–5)
- expected answer format
- private answer key
- common traps
- grading rubric
- source reference
- whether this question can affect readiness

The learner must not see the answer key before answering.

## When Asking

1. State the question ID.
2. State the expected answer format.
3. Ask exactly one question.
4. Wait for the answer.

## Question Rules

- No numbered lists of questions.
- No multiple-choice options revealed before the learner thinks, unless the question is a choose-best format.
- No obvious answer patterns.
- No keyword-only questions for serious readiness claims.
- Use plausible distractors in choose-best questions.
- Use scenario-first wording for certification and interview targets.
- Match difficulty to current readiness.

## After The Answer

1. Grade immediately using `protocols/GRADE_ANSWER.md`.
2. Do not ask a second question until the first is closed.
