# Close A Session Cleanly

Use this prompt at the end of any StudyDD session.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git status --short` and report any unexpected changes.

## Summarize

1. What was covered.
2. Questions asked and verdicts.
3. Evidence IDs added.
4. Weak areas still open.
5. Reviews scheduled.

## State Updates

1. Append to `sessions/SESSION_LOG.md`.
2. Append to `state/EVIDENCE_LOG.md` if not already done.
3. Update `state/SKILL_MAP.yaml`.
4. Update `state/STUDY_STATE.yaml`.
5. Refresh `state/STUDY_STATUS.md`.
6. Update `reviews/REVIEW_QUEUE.md`.
7. Write one clear next action to `NEXT_ACTIONS.md`.

## Validation

1. Run `python3 scripts/check_studydd.py`.
2. Run `python3 scripts/agent_consistency_check.py`.
3. Run `python3 scripts/agent_evidence_check.py`.

## Handoff

Leave a concise handoff that includes:

- repo path
- branch
- HEAD commit
- pushed status
- validation result
- worktree status
- changed files
- summary of the session
- weak areas still open
- next best action

## Do Not

- Push without explicit instruction.
- Leave uncommitted or unreported changes.
- Inflate readiness in the summary.
