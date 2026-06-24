# Reflection Prompt

Run a StudyDD reflection session.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.

## Purpose

Help the learner think about what they learned, what confused them, and what to focus on next. Reflection is evidence too, but usually lower-confidence evidence unless it includes a concrete demonstration.

## Questions

Ask one at a time:

1. What was the most important thing you learned today?
2. What still feels unclear or shaky?
3. What did you answer correctly but feel lucky about?
4. What did you answer incorrectly? Why?
5. What should the next study session focus on?

## Rules

- Do not answer for the learner.
- Capture the learner's own words.
- Link reflections back to target IDs and skill IDs when possible.
- Record reflection as low or medium confidence unless it includes a concrete demonstration.
- Do not inflate readiness from reflection alone.

## Output

Propose updates to:

- `state/EVIDENCE_LOG.md`
- `sessions/SESSION_LOG.md`
- `state/SKILL_MAP.yaml`
- `reviews/REVIEW_QUEUE.md`
- `NEXT_ACTIONS.md`

Run `python3 scripts/check_studydd.py` after writing.
