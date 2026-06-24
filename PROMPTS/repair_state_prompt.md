# Repair State Consistency

Use this prompt when state files seem missing, contradictory, or out of sync.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.
4. Run `python3 scripts/agent_consistency_check.py`.
5. Run `python3 scripts/agent_evidence_check.py`.

## Diagnosis

1. Read `state/STUDY_STATE.yaml`, `state/SKILL_MAP.yaml`, `state/EVIDENCE_LOG.md`, `sessions/SESSION_LOG.md`, and `reviews/REVIEW_QUEUE.md`.
2. Compare root `state/SKILL_MAP.yaml` to any `targets/<id>/state/SKILL_MAP.yaml` files.
3. Compare readiness values to evidence references.
4. Check for missing required files or YAML keys.

## Repair

1. Fix contradictions using the most recent evidence as the source of truth.
2. Add missing evidence references or remove stale ones.
3. Restore required sections in Markdown files if they are missing.
4. Re-run all validation scripts.
5. Record the repair in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md` as a state-correction event.

## Do Not

- Delete learner data without explicit permission.
- Inflate readiness to make the validator pass.
- Hide the cause of the inconsistency.
