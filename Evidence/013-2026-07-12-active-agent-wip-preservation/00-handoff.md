# Active-agent WIP preservation handoff

**Outcome:** lossless WIP preservation; not implementation-complete and not
closure-grade.

## Recovered objective

The dirty checkout was implementing the approved transactional-hardening
program in two dependency-ordered but independently reviewable slices:

- `TH-01`: central mode/remote guards and separation of template-engineering
  planning from learner-instance planning;
- `TH-02`: concrete fast-path integrity repairs, including canonical evidence
  validation, duplicate detection, review idempotency/failure propagation,
  atomic touched-state writes, read-only selection, and positive review steps.

The work also carries generic question-quality and fast-drill invariants learned
from lived-instance operation: explicit target scope, ambiguity/readiness
isolation, evidence weighting, and option-length-bias warnings. No learner data
or private fixture was imported.

## Why this is WIP preservation

The work spans more than one backlog slice and was developed directly on the
committed head of the open `feat/fast-drill-mode` branch. That branch is behind
and ahead of `origin/main`, and PR #5 is currently reported as conflicting.
The implementation plan itself says the hardening work should not be added to
that unresolved feature branch without an explicit base decision.

The code and focused tests are useful, but the change set has not been split,
reviewed against current `main`, or proven by remote cross-platform CI. It must
therefore remain WIP.

## Provenance

- Original branch: `feat/fast-drill-mode`
- Original committed HEAD: `5ae40397daed832e123eacf7d37a86cab6c58fc2`
- Remote-main observation: `27e153d57226560a09c50294e97fea54cf31b71d`
- Preservation branch: `wip/studydd-active-agent-handoff-2026-07-12`
- Prior owner: an active Codex session rooted in the shared StudyDD checkout
- Ownership mechanism: no repository lease, lock, or agent-state release
  mechanism was found; process ownership must be released operationally

## Completed pieces preserved

- A dependency-light `studydd.mode` contract and compatibility guard.
- Template-mode refusal for supported learner planning, context, recording,
  scheduling, selection, and fast-drill paths.
- Template-engineering backlog separation and instance-copy exclusion.
- Atomic text replacement helper used by touched state writers.
- Canonical evidence-log parsing for targeted validation.
- Duplicate evidence, activity, review, and drill-marker checks.
- Review scheduling idempotency, failure propagation, and explicit positive
  learning steps.
- Read-only next-action selection.
- Target-scoped drills and ambiguity/readiness isolation.
- Question option-length-bias warning and generic fixture adjustment.
- Focused regression coverage and CI discovery for fast-path integrity.

## Incomplete or unresolved work

- Separate `TH-01` and `TH-02` into independently reviewable changes based on a
  current, explicitly selected integration base.
- Reconcile overlapping files with current `origin/main` and with PR #5.
- Decide whether the question-scope/ambiguity work belongs inside `TH-02` or a
  later question-card slice.
- Review the temporary compatibility layer split between
  `scripts/mode_guard.py` and `studydd/mode.py`.
- Run remote Linux/macOS/Windows CI on the eventual integration branches.
- Reconcile the v1 runtime manifest's new closure-policy prose with the later
  executable manifest work.
- Implement none of `TH-03`, `TH-04`, or `TH-05` here. In particular, there is
  no Lifecycle Manifest v2, strict privacy gate, Git-closure implementation, or
  manifest-driven migration support in this preservation branch.

## Pull-request relationships

- PR #4 (`feat/source-check-completion-flow`) remains independent and was not
  merged or modified. This WIP touches source-check files only for mode guards,
  atomic writes, and time-hermetic regression behavior; a future extraction
  must reconcile those overlaps deliberately.
- PR #5 (`feat/fast-drill-mode`) remains independent and its remote branch was
  not updated. This preservation branch starts at PR #5's recorded head and is
  suitable only as a stacked WIP review until PR #5's conflict is resolved or
  the generic hardening changes are cleanly extracted.

## Next integration action

Do not start later transactional-hardening slices from this branch. First choose
a current canonical base, then extract and review `TH-01` and `TH-02`
independently while preserving the tests and public-safety constraints recorded
here.
