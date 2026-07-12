# Fast Drill checkpoint capability

Fast Drill is a generic checkpoint capability for dense retrieval-question
drills. It is a runtime speed layer, not a question selector, tutor loop, or
learner-state authority.

## Boundary

`scripts/fast_drill_mode.py` owns one ignored instance runtime file:

```text
state/ACTIVE_DRILL_SESSION.md
```

The file has a versioned YAML front matter block (`studydd.fast-drill-checkpoint/v2`)
and newline-delimited JSON answer records. Every record has a typed verdict and
confidence, a sequence number, a stable record/evidence ID, and a SHA-256 hash
link to the previous record. Starting creates the file exclusively; appending
opens it only in append mode. Duplicate record IDs are idempotent and conflicting
duplicates are rejected.

The checkpoint is instance-owned and must never be committed. A small ignored
`.fast_drill/` transaction directory is used only while reconciling canonical
state.

## Operations

The Python API exposes typed `StartOperation`, `AppendAnswerOperation`,
`RecoverOperation`, and `EndOperation` values through `execute`. The CLI mirrors
those operations:

```text
python3 scripts/fast_drill_mode.py start --session-id S-1 --target-id T-1
python3 scripts/fast_drill_mode.py append --question-id Q-1 --skill-id SK-1 \
  --concept "retrieval" --answer-summary "..." --verdict correct \
  --confidence medium --evidence-marker E-1
python3 scripts/fast_drill_mode.py end --apply
python3 scripts/fast_drill_mode.py recover --apply
```

`end` without `--apply` returns a proposal and writes nothing. `end --apply`
stages the evidence suffix and canonical YAML replacements, then commits them
with a restartable transaction journal. Evidence is appended only after its
expected prefix is verified; YAML files are replaced atomically. A crash before
cleanup leaves the journal and checkpoint in place. Re-running `recover --apply`
or `end --apply` verifies already-completed writes by hash, finishes pending
writes, removes the checkpoint, and is safe to repeat.

The reconciler updates only the evidence log, known skill entries, and the
active-focus portion of study state. It does not rebuild generated views,
rewrite `NEXT_ACTIONS.md`, or route based on words in a question, concept, or
answer. Run the normal session-boundary validators after reconciliation.

## Mode and settings authority

Mutating operations require `instance.yaml` to declare
`spec.mode: learner_instance`. Template and bootstrap modes are refused,
including recovery and reconciliation; `state/STUDYDD_MODE.yaml` is not used
for this decision because it is a generated compatibility view.

`state/LEARNER_PROFILE.yaml` is the instance-owned settings authority. The
module reads `learner_preferences.fast_drill_mode` and
`learner_preferences.auto_state_update_during_drills`, but never creates,
changes, or regenerates that file. Starting a drill requires
`fast_drill_mode: true`; ending with `--apply` remains an explicit operation
and does not infer permission from the setting.

No learner content, target, canonical status, or public checkpoint is seeded by
this capability. The included tests use temporary synthetic instances only.

## Recovery contract

At startup, an active checkpoint blocks a new start. `recover` reports whether a
recent checkpoint can be resumed or an older one should be reconciled. A pending
transaction takes precedence over that age recommendation. Use
`recover --apply` after an interrupted reconciliation. Corrupt checkpoints and
transaction conflicts remain on disk for operator inspection and are not
silently discarded.

The public synthetic tests cover versioning, append-only/hash-chain integrity,
typed operation rejection, template/bootstrap refusal, settings immutability,
proposal-only end, and a crash between transactional writes followed by
idempotent recovery.
