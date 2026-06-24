# STATE_LOADING_POLICY — Intelligent State Loading

> **Agent rule.** StudyDD should remember everything, but only load what matters.

## Doctrine

```text
Fast path by default.
Deep audit only when needed.
```

Do not confuse thoroughness with loading everything.

## Four layers

1. **Canonical compact state** — small machine-readable truth files loaded first.
2. **Append-only audit logs** — historical narrative records, never default context.
3. **Derived summaries and indexes** — compact views that make long history usable.
4. **Task-specific context packs** — the actual runtime context an agent loads.

## Three execution modes

### Fast path

Used during ordinary tutoring turns: asking, grading, scheduling one review.

- Load `.studydd/context_pack.md` for the current task.
- Load only the active question/rubric.
- Load only relevant skill entries.
- Load only relevant review items.
- Load only evidence excerpts referenced by the context pack.
- Do not scan raw logs.

### Session boundary path

Used at session start and close.

- Refresh compact state if stale.
- Rebuild the context pack.
- Run full `scripts/check_studydd.py`.

### Deep audit path

Used only for CI, explicit audit, validation failure, state repair, learner challenge, upgrade instance, privacy review, wrong-repo recovery.

- Scan raw logs.
- Compare indexes against audit logs.
- Rebuild summaries.
- Run full validation.
- Produce a repair plan.

## Default loading order

At session start, the agent must:

1. Verify repo path, remote, and mode.
2. Run `python3 scripts/check_studydd.py`.
3. Run or perform the equivalent of:
   ```bash
   python3 scripts/compact_state.py --check-stale
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
- `state/PERFORMANCE_BUDGET.yaml`
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
- This is a session-boundary operation.

### ask_question

- Use `--task ask_question --skill-id <skill_id>` when possible.
- Include active target, weak skills, due reviews, question bank metadata, and study skill.
- Do not load unrelated target history or full evidence log.
- This is a fast-path operation.

### grade_answer

- Use `--task grade_answer --skill-id <skill_id> --active-question <question_id>` when possible.
- Include active question, rubric, learner answer, relevant skill evidence, and study skill.
- Skip unrelated skill history.
- If the exact previous answer is needed, open the relevant excerpt from `state/EVIDENCE_LOG.md`.
- This is a fast-path operation.

### schedule_review

- Use `--task schedule_review --review-id <review_id>` when possible.
- Include review state, confidence, grade, previous interval, and lapses for the relevant skill.
- Use `scripts/schedule_review.py`.
- This is a fast-path operation.

### close_session

- Append evidence and session entries first.
- Run `python3 scripts/compact_state.py` to update summaries.
- Build a final context pack if needed.
- Run `python3 scripts/check_studydd.py`.
- This is a session-boundary operation.

### upgrade_instance

- Load version/protocol files and generic template structure.
- Do not load learner logs.
- This is a deep-audit operation.

### audit

- Scan indexes and references.
- Open raw logs when needed.
- Compare compact state against append-only audit trail.
- Report conflicts instead of guessing.
- This is a deep-audit operation.

## Human override

The learner may ask the agent to load a file not in the default pack. The agent should:

- Load it if the request is reasonable.
- Record the override in `sessions/SESSION_LOG.md` if it bypasses a strong recommendation.
- Not treat the override as a reason to skip validation.

## Validation

`scripts/check_studydd.py` validates that:

- `state/STATE_MANIFEST.yaml` and `state/PERFORMANCE_BUDGET.yaml` exist and are well-formed.
- canonical/protected files exist.
- generated files exist or can be regenerated.
- `.studydd/context_pack.md` and `.studydd/state_cache.json` are ignored by Git.
- evidence IDs in `state/EVIDENCE_INDEX.yaml` match evidence IDs in `state/EVIDENCE_LOG.md` where parseable.
- session summaries are not empty when the session log has real sessions.
- `state/CURRENT_CONTEXT.md` contains active target, due review, and weak skill sections.
