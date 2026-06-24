# TUTOR_PROTOCOL — Ask, Grade, Repair, Update

> **Agent-maintained.** This protocol governs how coding agents and tutor agents ask questions, grade answers, and update StudyDD state.

## Active Question Tracking

Every question must have a unique active question ID.

- Format: `Q-YYYYMMDD-NNN` or a sequential ID within the session.
- The ID must be visible to the learner.
- Only one question may be active at a time.
- Before asking, define the active question ID, expected answer format, answer key, target ID, and skill ID.
- Do not reveal the answer key until after the learner answers.

## Question Lifecycle

1. **Select** the next question from `NEXT_ACTIONS.md`, weak areas, pending validation, or due reviews.
2. **Introduce** the question with its ID and expected answer format.
3. **Wait** for the learner's answer.
4. **Grade** the actual answer against the answer key.
5. **Explain** the verdict in plain language.
6. **Repair** if the answer is wrong, incomplete, or unclear.
7. **Close** the question before opening a new one.
8. **Record** evidence and propose state updates.

## Expected Answer Format

Tell the learner what kind of answer you expect:

- one sentence
- short paragraph
- bullet list
- code snippet
- architecture explanation
- comparison
- step-by-step procedure

## Answer Key

Before asking a question, define:

- required concepts that must appear
- acceptable synonyms or alternative phrasing
- common misconceptions that should be flagged
- source-trust assumptions, if relevant
- minimum completeness threshold

## Grading

Use one of these verdicts:

- **correct** — fully meets the answer key
- **partial** — partly correct but missing something important
- **incorrect** — does not meet the answer key
- **unclear** — cannot be graded because the answer is ambiguous
- **override** — learner or human reviewer overrode the grade

Grade what the learner actually wrote or said, not what you expected them to say.

## Explanation

After grading, explain:

- what was correct
- what was missing or wrong
- why it matters for the target
- one concrete takeaway

Keep this read-aloud friendly.

## Repair Question

If the answer is partial, incorrect, or unclear, ask a repair question before moving on.

Rules for repair questions:

- Keep the repair focused on the gap.
- Label it as a repair, not a new numbered question.
- Do not mix repair questions with new numbered questions.
- Once the repair is resolved, close the original question.

## State Update Proposal

After every question and at the end of every session, propose updates:

- add or update skill entries in `state/SKILL_MAP.yaml`
- append evidence to `state/EVIDENCE_LOG.md`
- append session history to `sessions/SESSION_LOG.md`
- add SkillSignal packets to `sessions/SKILLSIGNAL_PACKETS.md` when useful
- update `state/STUDY_STATE.yaml`
- update `state/STUDY_STATUS.md`
- add due review items to `reviews/REVIEW_QUEUE.md`
- update `NEXT_ACTIONS.md`

Wait for learner confirmation before writing changes, unless the learner has explicitly authorized automatic updates.

## Readiness Rules

- New skills default to `pending` with readiness `0`.
- One correct answer can move a skill to `practiced`, not `confirmed`.
- A repair-assisted answer should stay conservative.
- Confirmed status requires strong or varied evidence.
- Source coverage alone does not prove readiness.

## Tutor-State Failure Prevention

Watch for these failures and correct them immediately:

- **Grading against the wrong active question** — always check the active question ID before grading.
- **Mixing repair questions with new numbered questions** — repairs are sub-questions; new questions get new IDs.
- **Leaking internal agent messages** — keep output learner-facing.
- **Inflating readiness after easy questions** — one easy answer does not prove mastery.
- **Ignoring the learner's correction** — stop, audit, and update state.
- **Forgetting weak areas** — weak skills must stay visible until evidence proves they are resolved.
- **Saying "correct" without checking the answer key** — always compare against the key.
- **Using untrusted sources as authoritative** — record source trust and resolve conflicts.
- **Updating the public template with personal state** — only initialize a learner copy when explicitly asked.
