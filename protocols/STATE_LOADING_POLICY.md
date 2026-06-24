# STATE_LOADING_POLICY — Intelligent State Loading

> **Agent rule.** StudyDD should remember everything, but only load what matters.

## Four layers

1. **Canonical compact state** — small machine-readable truth files loaded first.
2. **Append-only audit logs** — historical narrative records, never default context.
3. **Derived summaries and indexes** — compact views that make long history usable.
4. **Task-specific context packs** — the actual runtime context an agent loads.

## Default loading order

At session start, the agent must:

1. Verify repo path, remote, and mode.
2. Run `python3 scripts/check_studydd.py`.
3. Run or perform the equivalent of:
   ```bash
   python3 scripts/compact_state.py
   python3 scripts/build_context_pack.py --task start_session
   ```
4. Read `.studydd/context_pack.md`.
5. Load the active target's `study_skills/<id>/SKILL.md` or fall back to `study_skills/generic/SKILL.md`.
6. Open raw logs only if the context pack or validator says it is necessary.

## What agents load by default

- `state/STUDY_STATE.yaml`
- `state/SKILL_MAP.yaml`
- `reviews/REVIEW_STATE.yaml`
- `state/STUDYDD_MODE.yaml`
- `state/STUDYDD_TEMPLATE_VERSION.yaml`
- `state/STATE_MANIFEST.yaml`
- `state/CURRENT_CONTEXT.md`
- `state/EVIDENCE_INDEX.yaml`
- `sessions/SESSION_SUMMARIES.md`
- `NEXT_ACTIONS.md`
- active target `TARGET.yaml`
- active study skill `study_skills/<id>/SKILL.md`
- relevant question bank files for the active target

## What agents do not load by default

- `state/EVIDENCE_LOG.md` full raw log
- `sessions/SESSION_LOG.md` full raw log
- `reviews/REVIEW_OVERRIDES.md` full raw log
- older target notes and historical artifacts unless referenced

## When raw logs are opened

Open raw audit logs only when:

- the context pack explicitly references them (e.g., `--task audit`),
- validation fails and the conflict must be traced,
- grading requires the exact previous answer for the same skill,
- the learner challenges a prior grade,
- an audit or repair is requested,
- a referenced evidence ID cannot be resolved through the index.

## Conflict resolution

If compact state conflicts with append-only logs:

1. Stop and do not guess.
2. Run `python3 scripts/check_studydd.py`.
3. If validation cannot resolve the conflict, run `--task audit` and compare evidence.
4. Repair the compact state or the log as appropriate.
5. Record any human override in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md`.

## Task-specific loading rules

### start_session

- Build the context pack with `--task start_session`.
- Include active target, due/overdue reviews, weak skills, last session summary, and current next action.
- Do not open full raw logs unless the validator reports a conflict.

### ask_question

- Include active target, weak skills, due reviews, question bank metadata, and study skill.
- Do not load unrelated target history or full evidence log.

### grade_answer

- Include active question, rubric, learner answer, relevant skill evidence, and study skill.
- Skip unrelated skill history.
- If the exact previous answer is needed, open the relevant excerpt from `state/EVIDENCE_LOG.md`.

### schedule_review

- Include review state, confidence, grade, previous interval, and lapses for the relevant skill.
- Use `scripts/schedule_review.py`.

### close_session

- Append evidence and session entries first.
- Run `python3 scripts/compact_state.py` to update summaries.
- Build a final context pack if needed.

### upgrade_instance

- Load version/protocol files and generic template structure.
- Do not load learner logs.

### audit

- Scan indexes and references.
- Open raw logs when needed.
- Compare compact state against append-only audit trail.
- Report conflicts instead of guessing.

## Human override

The learner may ask the agent to load a file not in the default pack. The agent should:

- Load it if the request is reasonable.
- Record the override in `sessions/SESSION_LOG.md` if it bypasses a strong recommendation.
- Not treat the override as a reason to skip validation.

## Validation

`scripts/check_studydd.py` validates that:

- `state/STATE_MANIFEST.yaml` exists and is well-formed.
- canonical/protected files exist.
- generated files exist or can be regenerated.
- `.studydd/context_pack.md` is ignored by Git.
- evidence IDs in `state/EVIDENCE_INDEX.yaml` match evidence IDs in `state/EVIDENCE_LOG.md` where parseable.
- session summaries are not empty when the session log has real sessions.
- `state/CURRENT_CONTEXT.md` contains active target, due review, and weak skill sections.
