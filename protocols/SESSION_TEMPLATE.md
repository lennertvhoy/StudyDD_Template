# SESSION_TEMPLATE — Standard Study Session Structure

> **Agent-maintained.** Use this structure for every StudyDD session.

## Before The Session

1. Read the required files listed in `AGENTS.md`.
2. Confirm whether the repo is still a public template or has been initialized for a learner.
3. If no learner or target exists, initialize only after learner confirmation.
4. Identify the active target, active focus, weakest skill, pending validation, or due review.
5. Select the next best single question.

## During The Session

For each question:

1. State the active question ID.
2. State the expected answer format.
3. Ask exactly one question.
4. Wait for the learner's answer.
5. Grade against the answer key.
6. Explain the verdict.
7. If needed, ask one repair question.
8. Close the question before asking the next.

End the session after the planned question count or when the learner asks to stop.

## After The Session

1. Summarize what was covered.
2. List new evidence items.
3. Identify weak areas.
4. Propose updates to `state/SKILL_MAP.yaml`.
5. Propose updates to `state/STUDY_STATE.yaml`.
6. Propose updates to `state/STUDY_STATUS.md`.
7. Append entries to `sessions/SESSION_LOG.md` and `state/EVIDENCE_LOG.md`.
8. Add or update review items in `reviews/REVIEW_QUEUE.md`.
9. Propose updates to `NEXT_ACTIONS.md`.
10. Run or request `python3 scripts/check_studydd.py`.
11. Wait for learner confirmation or apply authorized updates.
12. End with one clear next action.

## Session Length

Default: 3-5 exam-style questions per session.

Adjust based on learner preference, available time, and topic difficulty. Even in a multi-question session, ask and grade one question at a time.
