# ASK_QUESTION — Ask Exactly One Question

> **Agent action.** Use this protocol every time you ask a question.

## Before Asking

Build the context pack with `--task ask_question`. Load the active target, weak skills, due reviews, question bank metadata, and the active study skill. Do not load full raw logs unless needed.

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

Shape the question according to the active study skill (e.g., scenario for IT certification, argument reconstruction for philosophy, concrete word problem for primary maths).

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

## Multiple-Choice / Choose-Many / Matching Workflow

For any fixed-option question:

1. **Create stable internal option IDs first.** Assign IDs like `opt_1`, `opt_2`, `opt_3`, `opt_4` to option content before any visible label exists. Mark which IDs are correct in the private answer key.
2. **Keep the private answer key in the agent context only before the learner answers.** Do not write it to repo files, active question files, session logs, or evidence logs before grading.
3. **Shuffle the visible options.** Use a random order for the final question.
4. **Verify the answer key maps to the new labels.** After shuffling, confirm the correct answer label(s) in the final order.
5. **Check for obvious position patterns.** Ensure the correct answer is not always A, first, longest, or most detailed.
6. **For choose-two/choose-three, randomize cluster positions.** Avoid correct answers always appearing as A+B or C+D.
7. **Present the question.** Show only the final shuffled options to the learner.
8. **Track recent labels.** In a practice set, avoid repeating the same correct label too often.

## After The Answer

1. Grade immediately using `protocols/GRADE_ANSWER.md`.
2. After grading, the session/evidence log may record the final visible option order, correct answer label(s), learner answer, grading result, and optionally the internal option-ID mapping.
3. Do not ask a second question until the first is closed.
