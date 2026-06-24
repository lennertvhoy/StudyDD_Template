# CLOSE_SESSION — End The Session Cleanly

> **Agent action.** Run this protocol at the end of every StudyDD session.

## Must Do

1. **Summarize what was covered.**
   - Target ID and skills touched.
   - Questions asked.
   - Verdicts.

2. **List evidence added.**
   - Evidence IDs from `state/EVIDENCE_LOG.md`.

3. **Identify weak areas.**
   - Skills still `weak` or `blocked`.
   - Skills that were repaired or partial.

4. **Propose state updates.**
   - `state/SKILL_MAP.yaml`
   - `state/STUDY_STATE.yaml`
   - `state/STUDY_STATUS.md`
   - `sessions/SESSION_LOG.md`
   - `reviews/REVIEW_QUEUE.md`
   - `NEXT_ACTIONS.md`

5. **Confirm or apply authorized updates.**
   - Wait for learner confirmation unless auto-updates are authorized.

6. **Run validator.**
   - `python3 scripts/check_studydd.py`

7. **Write the next action.**
   - One clear next action in `NEXT_ACTIONS.md`.

8. **Leave a truthful handoff.**
   - repo path
   - branch
   - HEAD commit
   - pushed status
   - validation result
   - worktree status
   - changed files
   - summary of didactic and operational upgrades (template work only)
   - weak areas still open
   - next best action

## Do Not

- Hide mistakes.
- Inflate readiness in the summary.
- Leave the worktree dirty with unreported changes.
- Push without explicit instruction.
