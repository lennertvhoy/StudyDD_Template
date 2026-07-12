# RECORD_SOURCE_CHECK — Completed Source Checks

Use `scripts/record_source_check.py` after a `recent_info_check` has actually
been completed. The command records source metadata and check provenance in
`sources/SOURCE_STATE.yaml`; it does not fetch sources and it does not update
learner evidence, readiness, session history, or other study status.

## Write boundary

Writes are permitted only when `state/STUDYDD_MODE.yaml` says
`mode: learner_instance`. `template` and `bootstrap` modes refuse writes.
Use `--dry-run` or `--demo` to inspect a proposed record without changing a
file. Input validation happens before any write.

```bash
python3 scripts/record_source_check.py source-id \
  --target-id target-id \
  --outcome fresh \
  --checked-at 2026-07-01T12:00:00+00:00 \
  --summary "Official source checked; relevant current facts confirmed." \
  --evidence-id ev_source_001 \
  --activity-id act_source_001
```

For a source that is already registered, `--target-id` is optional. A new
source requires it. Source IDs and target IDs are generic safe identifiers;
do not put URLs, learner names, secrets, or private source content in this
registry.

## Freshness semantics

`check_source_freshness.py` is the single freshness classifier. This writer
does not duplicate its age windows or make a separate fresh/stale decision.
Only `outcome: fresh` advances `last_checked_at` (and replaces an old explicit
expiry when no new expiry is supplied). `stale`, `missing`, `unverified`, and
`unknown` preserve the prior freshness timestamp and remain visible through
the classifier's recorded check outcome.

Repeated identical commands update the source by ID rather than appending a
duplicate. Once the serialized state is identical, the writer skips the
replacement and reports that the record is already present. Real writes use a
same-directory temporary file, flush and fsync the file, atomically replace
the destination, and fsync the directory when supported.
