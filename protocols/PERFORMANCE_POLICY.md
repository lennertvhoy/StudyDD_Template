# PERFORMANCE_POLICY — StudyDD Fast Path State Policy v1

> **Agent rule.** StudyDD should remember everything, but every tutoring turn should touch as little as possible.

## Doctrine

```text
Fast path by default.
Deep audit only when needed.
Write minimal state.
Append audit trail once.
Validate touched references first.
Full validation at session boundaries, CI, audit, and repair.
```

Do not confuse thoroughness with loading everything.

## Three execution modes

### 1. Fast path

Used during ordinary tutoring turns: asking a question, grading an answer, scheduling one review, or updating one skill.

Allowed:

- load `.studydd/context_pack.md`
- load only the active question/rubric
- load only relevant skill entries
- load only relevant review items
- load only evidence excerpts referenced by the context pack
- write only touched canonical state
- append exactly one evidence/session/review entry when needed
- run targeted validation on touched IDs

Not allowed:

- scanning the entire repo
- reading full raw audit logs (`state/EVIDENCE_LOG.md`, `sessions/SESSION_LOG.md`, `reviews/REVIEW_OVERRIDES.md`)
- rebuilding derived summaries
- running full `scripts/check_studydd.py`

### 2. Session boundary path

Used at session start and close, and when the agent explicitly starts or finishes a block of work.

Allowed:

- refresh compact state if stale
- rebuild the context pack
- update `state/CURRENT_CONTEXT.md`
- update `state/EVIDENCE_INDEX.yaml` if evidence changed
- update `sessions/SESSION_SUMMARIES.md` if sessions changed
- run full `scripts/check_studydd.py`

### 3. Deep audit path

Used only for:

- CI
- explicit audit request
- validation failure
- state repair
- learner challenge
- upgrade instance
- privacy review
- wrong-repo recovery

Allowed:

- scan raw logs
- compare indexes against audit logs
- rebuild all summaries
- run full validation
- produce a repair plan

## State cache

`.studydd/state_cache.json` tracks source-file fingerprints so compaction can skip unchanged files. It is generated and must not be committed. Treat it as a safe-to-delete cache.

If the cache is missing or corrupt, scripts must fall back to full, correct behavior.

## Override

The learner or operator may request a deep audit at any time. Honor it, but name the cost:

> "Running a full audit. This will load raw logs and rebuild all summaries."

Record the override in `sessions/SESSION_LOG.md` or `reviews/REVIEW_OVERRIDES.md` if it bypasses a strong recommendation.

## Validation discipline

- After a fast-path update, run `scripts/validate_touched_state.py` on the touched IDs.
- If targeted validation fails, escalate to the session-boundary or deep-audit path.
- Run `scripts/check_studydd.py` at session close, CI, audit, and repair.

## Budget

See `state/PERFORMANCE_BUDGET.yaml` for numeric limits per mode.
