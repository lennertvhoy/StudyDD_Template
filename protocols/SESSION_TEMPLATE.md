# SESSION_TEMPLATE — Standard Study Session Structure

> **Agent-maintained.** Use this structure for every StudyDD session.

## Before The Session

1. Read the required files listed in `AGENTS.md`.
2. Verify repo path and remote.
3. Run `python3 scripts/check_studydd.py`.
4. Confirm whether the repo is still a public template or has been initialized for a learner.
5. If no learner or target exists, initialize only after learner confirmation.
6. Choose session mode: deep, normal, low-energy, or recovery.
7. Identify the active target, active focus, weakest skill, pending validation, or due review.
8. Select the next best single question using `protocols/SELECT_NEXT_ACTION.md`.

## During The Session

For each question:

1. State the active question ID and expected answer format.
2. Ask exactly one question.
3. Wait for the learner's answer.
4. Grade against the answer key.
5. Explain the verdict.
6. If needed, ask one repair question.
7. Close the question before asking the next.

End the session after the planned question count or when the learner asks to stop.

Default normal mode: 3–5 exam-style questions per session.
Low-energy mode: 1–2 questions or one due review.
Recovery mode: one concept explanation, optionally one gentle check question.

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
13. Leave a truthful handoff.

See `protocols/CLOSE_SESSION.md` for the handoff format.
