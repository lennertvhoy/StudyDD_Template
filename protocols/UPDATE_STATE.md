# UPDATE_STATE — Update State From Evidence

> **Agent action.** Apply state updates immediately after grading.

## Before Writing

1. Propose the update to the learner.
2. Wait for confirmation unless auto-updates are explicitly authorized.
3. If the learner overrides, record the override in evidence and session logs.

## Files To Update

1. `state/EVIDENCE_LOG.md` — append one evidence item per question.
2. `sessions/SESSION_LOG.md` — append one entry per session.
3. `state/SKILL_MAP.yaml` — update status, readiness, confidence, evidence list, next validation question, mistake tags.
4. `state/STUDY_STATE.yaml` — update active focus, current readiness estimate, readiness confidence, risk level, blocking confusions, session history.
5. `state/STUDY_STATUS.md` — refresh the human-readable snapshot.
6. `NEXT_ACTIONS.md` — write the single next action.
7. `reviews/REVIEW_QUEUE.md` — add or update review items.

## Compact after writing

After appending evidence and session entries, run `python3 scripts/compact_state.py` so `state/CURRENT_CONTEXT.md`, `state/EVIDENCE_INDEX.yaml`, and `sessions/SESSION_SUMMARIES.md` stay current.

## Evidence Item Format

```markdown
- **Date:**
- **Target ID:**
- **Skill ID:**
- **Question ID:**
- **Question summary:**
- **Learner answer summary:**
- **Verdict:** correct / partial / incorrect / unclear / override
- **Mistake type:** (use `protocols/MISTAKE_TAXONOMY.md`)
- **Explanation:**
- **Confidence:** high / medium / low
```

## State Update Rules

- Never inflate readiness.
- A single correct answer moves a skill to `practiced`, not `confirmed`.
- A repaired answer stays at or below `practiced`.
- An incorrect or vague answer marks the skill `weak`.
- A persistent confusion marks the skill `blocked`.
- `confirmed` requires strong or varied evidence.
- Apply the active study skill's readiness rules in addition to the general readiness policy.
- If the study skill conflicts with general StudyDD policy, the stricter anti-inflation rule wins.
- Update timestamps and `updated_by` in YAML metadata.

## After Updating

Run `python3 scripts/check_studydd.py`.
