# Grade An Answer And Update State

Use this prompt when the learner has just answered a StudyDD question and you need to grade and update state.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.

## Inputs

- active question ID
- target ID
- skill ID
- learner's actual answer
- private answer key
- expected answer format
- source reference

## Grading

1. Compare the learner's actual answer to the answer key.
2. Choose a verdict: correct / partial / incorrect / unclear / override.
3. Tag the mistake type using `protocols/MISTAKE_TAXONOMY.md` when not fully correct.
4. Explain what was correct, what was missing, and why it matters.
5. If needed, ask one focused repair question.

## State Update

1. Append an evidence item to `state/EVIDENCE_LOG.md`.
2. Update the skill in `state/SKILL_MAP.yaml`:
   - status
   - readiness (use `protocols/READINESS_POLICY.md`)
   - confidence
   - evidence list
   - next validation question
3. Update `state/STUDY_STATE.yaml` active focus and readiness estimate.
4. Refresh `state/STUDY_STATUS.md`.
5. Add a review item to `reviews/REVIEW_QUEUE.md` if the answer was partial, incorrect, repaired, or shaky.
6. Update `NEXT_ACTIONS.md` with the single next action.
7. Append to `sessions/SESSION_LOG.md` if this ends a session.
8. Propose changes before writing unless auto-updates are authorized.

## Validation

Run `python3 scripts/check_studydd.py` after writing.
