# CTO handoff

Selected modules are `studydd.core`, `studydd.activities`,
`studydd.source-freshness`, and `studydd.fast-drill`.

Source-check completion is atomic, mode-confined, dry-run capable, stale/fresh
classified by one evaluator, and idempotent. Fast Drill uses versioned,
hash-linked append-only checkpoints with transactional recovery. The
question-bank work is a typed public-safe boundary foundation and remains
deferred as a runtime module.
