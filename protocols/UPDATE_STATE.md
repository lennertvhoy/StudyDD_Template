# UPDATE_STATE — Update State From Evidence

> **Agent action.** Apply state updates immediately after grading.

This is a **fast-path** operation. Write minimal state and validate only the touched IDs.

## Before Writing

1. Propose the update to the learner.
2. Wait for confirmation unless auto-updates are explicitly authorized.
3. If the learner overrides, record the override in evidence and session logs.

Identify touched files before writing:

```bash
python3 scripts/plan_state_update.py --operation grade_answer
```

## Files To Update

1. `state/EVIDENCE_LOG.md` — append one evidence item per question.
2. `state/SKILL_MAP.yaml` — update status, readiness, confidence, evidence list, next validation question, mistake tags.
3. `state/STUDY_STATE.yaml` — update active focus, current readiness estimate, readiness confidence, risk level, blocking confusions, session history.
4. `NEXT_ACTIONS.md` — write the single next action.
5. `reviews/REVIEW_QUEUE.md` — add or update review items.

Leave these for session close unless the learner explicitly requests otherwise:

- `sessions/SESSION_LOG.md`
- derived summaries (`state/CURRENT_CONTEXT.md`, `state/EVIDENCE_INDEX.yaml`, `sessions/SESSION_SUMMARIES.md`)

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

1. Run targeted validation on the touched IDs:
   ```bash
   python3 scripts/validate_touched_state.py --skill-id <skill_id> --evidence-id <evidence_id>
   ```
2. If targeted validation passes, continue.
3. If targeted validation fails, escalate to a session-boundary or deep-audit pass:
   ```bash
   python3 scripts/check_studydd.py
   ```
