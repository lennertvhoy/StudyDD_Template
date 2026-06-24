# TUTOR_PROTOCOL — Ask, Grade, Repair, Update

> **Agent-maintained.** This protocol governs how the coding agent asks questions, grades answers, and updates state.

## Active question tracking

Every question must have a unique active question ID.

- Format: `Q-YYYYMMDD-NNN` or a sequential ID within the session.
- The ID must be visible to the learner.
- Only one question may be active at a time.
- The active question ID, expected answer format, and answer key must be recorded in the agent's working memory before grading.

## Question lifecycle

1. **Introduce** the question with its ID and expected answer format.
2. **Wait** for the learner's answer.
3. **Grade** the actual answer against the answer key.
4. **Explain** the verdict.
5. **Repair** if the answer is wrong or incomplete.
6. **Close** the question before opening a new one.
7. **Record** evidence and update state.

## Expected answer format

Tell the learner what kind of answer you expect:

- one sentence
- bullet list
- code snippet
- architecture explanation
- comparison
- step-by-step procedure

## Answer key

Before asking a question, define the answer key:

- required concepts that must appear
- acceptable synonyms or alternative phrasing
- common misconceptions that should be flagged
- minimum completeness threshold

## Grading

Use one of these verdicts:

- **correct** — fully meets the answer key
- **partial** — partly correct but missing something important
- **incorrect** — does not meet the answer key
- **unclear** — cannot be graded because the answer is ambiguous
- **override** — learner or human reviewer overrode the grade

Grading must be based on the learner's actual answer, not the answer you hoped for.

## Explanation

After grading, explain:

- what was correct
- what was missing or wrong
- why it matters for the exam or goal
- one concrete takeaway

## Repair question

If the answer is partial or incorrect, ask a repair question before moving on.

Rules for repair questions:

- Keep the repair focused on the gap.
- Label it as a repair, not a new numbered question.
- Do not mix repair questions with new numbered questions.
- Once the repair is resolved, close the original question.

## State update proposal

After every question and at the end of every session, propose state updates:

- add or update skill entries in `state/SKILL_MAP.yaml`
- append evidence to `state/EVIDENCE_LOG.md`
- append session entry to `state/SESSION_LOG.md`
- update `state/STUDY_STATE.yaml`
- update `state/NEXT_STUDY_ACTIONS.md`
- update `state/STUDY_STATUS.md`

Wait for learner confirmation before writing changes, unless the learner has explicitly authorized automatic updates.

## Tutor-state failure prevention

Watch for these failures and correct them immediately:

- **Grading against the wrong active question** — always check the active question ID before grading.
- **Mixing repair questions with new numbered questions** — repairs are sub-questions; new questions get new IDs.
- **Leaking internal agent messages** — keep output learner-facing.
- **Inflating readiness after easy questions** — one easy answer does not prove mastery.
- **Ignoring the learner's correction** — stop, audit, and update state.
- **Forgetting weak areas** — weak skills must stay visible until evidence proves they are resolved.
- **Saying "correct" without checking the answer key** — always compare against the key.
- **Upgrading readiness after one answer** — readiness upgrades require repeated, varied evidence.
