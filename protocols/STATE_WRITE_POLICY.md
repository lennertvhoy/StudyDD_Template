# STATE_WRITE_POLICY — Minimal State Writes

> **Agent rule.** Write as little as possible while keeping the audit trail complete.

## Principle

Every tutoring turn should produce exactly one canonical update and exactly one audit append. Do not rewrite large files unless you are closing a session or repairing state.

## Before updating state

1. Identify the touched files for this operation.
2. Prefer:
   - one canonical state update (e.g., `state/SKILL_MAP.yaml`)
   - one audit append (e.g., `state/EVIDENCE_LOG.md`)
3. Avoid:
   - rewriting `state/EVIDENCE_LOG.md` or `sessions/SESSION_LOG.md` from scratch
   - updating unrelated skills
   - updating all target maps
   - rewriting derived summaries (`state/CURRENT_CONTEXT.md`, `state/EVIDENCE_INDEX.yaml`, `sessions/SESSION_SUMMARIES.md`) during ordinary turns

## After updating state

1. Run targeted validation on the touched IDs:
   ```bash
   python3 scripts/validate_touched_state.py --skill-id <skill_id>
   python3 scripts/validate_touched_state.py --evidence-id <evidence_id>
   python3 scripts/validate_touched_state.py --review-id <review_id>
   ```
2. If targeted validation passes, continue.
3. If targeted validation fails, stop and escalate to a session-boundary or deep-audit pass:
   ```bash
   python3 scripts/check_studydd.py
   ```

## Session boundaries

At session start:

- build the context pack
- compact state only if it is stale

At session close:

- append any remaining evidence/session entries
- run `scripts/compact_state.py` to refresh derived summaries
- run `scripts/check_studydd.py`

## Handoff

Every handoff must list:

- files read
- files written
- validation command run
- whether the fast path, session boundary, or deep audit path was used
