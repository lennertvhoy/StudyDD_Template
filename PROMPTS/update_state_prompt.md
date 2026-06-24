:memo: Update State Prompt

Apply a state update based on new evidence or a completed session.

## Inputs

Provide or infer:

- session date
- focus topic or skill IDs
- questions asked
- learner answers
- verdicts
- weak areas identified
- human overrides, if any

## Actions

1. Append entries to `state/SESSION_LOG.md`.
2. Append evidence items to `state/EVIDENCE_LOG.md`.
3. Update `state/SKILL_MAP.yaml`:
   - status: confirmed / practiced / weak / pending / blocked
   - readiness: 0–100 estimate
   - confidence: high / medium / low
   - evidence: list of evidence references
   - next_validation_question: what would prove this skill is solid
4. Update `state/STUDY_STATE.yaml`:
   - current_readiness_estimate
   - readiness_confidence
   - active_focus
   - blocking_confusions
   - session_history
5. Update `state/NEXT_STUDY_ACTIONS.md` with the immediate next step.
6. Update `state/STUDY_STATUS.md` with a short human-readable snapshot.

## Rules

- Never inflate readiness.
- Only update a skill status to `confirmed` if there is strong, varied evidence.
- Record human overrides explicitly.
- Keep the files human-readable.
- Propose changes before writing them unless auto-updates are authorized.
