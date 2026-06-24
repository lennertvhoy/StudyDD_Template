# Update State Prompt

Apply a StudyDD state update based on new evidence or a completed session.

## Inputs

Provide or infer:

- session date
- target ID
- focus topic or skill IDs
- questions asked
- learner answers
- verdicts
- weak areas identified
- review items due or created
- human overrides, if any

## Actions

1. Append entries to `sessions/SESSION_LOG.md`.
2. Append evidence items to `state/EVIDENCE_LOG.md`.
3. Update `state/SKILL_MAP.yaml`:
   - status: confirmed / practiced / weak / pending / blocked
   - readiness: 0-100 estimate
   - confidence: high / medium / low
   - evidence: list of evidence references
   - next_validation_question: what would prove this skill is solid
4. Update `state/STUDY_STATE.yaml`:
   - current_readiness_estimate
   - readiness_confidence
   - active_focus
   - blocking_confusions
   - session_history
5. Update `reviews/REVIEW_QUEUE.md` for weak, repaired, or shaky answers.
6. Update `NEXT_ACTIONS.md` with the immediate next step.
7. Update `state/STUDY_STATUS.md` with a short human-readable snapshot.
8. Run `python3 scripts/check_studydd.py`.

## Rules

- Never inflate readiness.
- Only update a skill status to `confirmed` if there is strong or varied evidence.
- Record human overrides explicitly.
- Keep files human-readable.
- Propose changes before writing them unless auto-updates are authorized.
