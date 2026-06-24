# Refresh Source Map

Use this prompt when the learner wants to update sources or when source freshness is in doubt.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.

## Review Existing Sources

1. Read `sources/SOURCE_INDEX.md`.
2. Read `state/STUDY_STATE.yaml` to find the active target.
3. Read `targets/<active>/TARGET.yaml` to see trusted source references.

## Update Sources

1. Add new official or trusted sources.
2. Update `last_checked` for existing sources.
3. Mark outdated or conflicting sources.
4. For certification targets, verify the current official credential name and exam outline.

## Reconcile

1. If a source changes the skill map, propose conservative updates to `state/SKILL_MAP.yaml`.
2. If a source is stale, lower readiness confidence where appropriate.
3. Append a source-refresh note to `sessions/SESSION_LOG.md`.
4. Run `python3 scripts/check_studydd.py`.

## Do Not

- Treat generated summaries or old notes as authoritative without verification.
- Inflate readiness just because sources are fresh.
