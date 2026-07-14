# TEMPLATE_BACKLOG — Template Engineering Roadmap

> This file belongs to the public StudyState mold. It is copied neither to learner
> instances nor into learner next-action state. The approved program and plan
> remain the authoritative design references below.

## Authoritative program

- **Specification:** `docs/superpowers/specs/2026-07-10-transactional-hardening-program.md`
- **Implementation plan:** `docs/superpowers/plans/2026-07-10-core-safety-foundation.md`
- **Audit anchor:** public `origin/main` commit `27e153d` (2026-06-30)
- **Recorded integration branch:** `feat/fast-drill-mode` at `5ae4039`

The specification owns scope, architecture, invariants, dependencies, and exit
gates. This file owns only template-engineering ordering and status.

## Lived-instance audit disposition — 2026-07-12

Reusable behavior was evaluated by invariant and dependency group, not copied
directory-for-directory.

- **Integrated now:** fast-path validation, canonical evidence parsing,
  duplicate detection, review selector purity and scheduling idempotency,
  atomic touched-state writes, time-hermetic freshness tests, target-scoped
  drills, ambiguity/readiness isolation, and option-length-bias linting.
- **Deferred to the existing program:** canonical card routing and presentation
  (`TH-07`/`TH-08`), review and readiness projections (`TH-09`/`TH-10`), and
  Git closure plus unified validation (`TH-03`/`TH-04`/`TH-06`). Their instance
  implementations are useful design evidence but depend on learner-specific
  schemas or precede the template's planned boundaries.
- **Excluded from the template core:** automatic distractor padding, direct
  readiness-bump commands, auto-repair that deletes unknown fields, and
  operator-specific messaging, browser, classroom, or sync integrations.
  These either change question meaning, bypass evidence gates, or belong in
  optional add-ons rather than the public mold.

## Git closure policy — binding handoff rule

- A worktree with modified, deleted, or untracked files is **not clean**.
- A coding slice is not complete until validation passes, the reviewed change
  set is committed, and the requested push is verified against its upstream.
- Never describe an uncommitted worktree as “intentionally dirty” or as a
  clean handoff. If Git writes are blocked by the environment, stop and report
  `GIT_WRITE_BLOCKED` with the exact command/error and one bounded next action.
- The next coding agent must begin by checking this policy, the full porcelain
  status, branch/upstream divergence, validation state, and pushed status.
- Do not stash, reset, discard, rewrite history, or silently omit existing
  user changes. Commit the complete reviewed set only after explicit approval.

## Phase 0 and Phase 1 — core safety foundation

| ID | Status | Depends on | Bounded deliverable |
|---|---|---|---|
| `TH-00` | Required preflight inside `TH-01` | None | Reconcile root/mode/remote/branch/HEAD; run baseline validation; classify current reproductions. |
| `TH-01` | **DONE** | `TH-00` | Central mode/remote guard; template learner operations fail with `INSTANCE_REQUIRED`; split template and learner planning. Slice A complete. |
| `TH-02` | IMPLEMENTED — CLOSURE PENDING | `TH-01` | Repair targeted validation, evidence references, review failure propagation/idempotency, atomic writes, selector purity, and intervals. |
| `TH-03` | QUEUED | `TH-01` | Executable manifest v2 with boundary, tracking, privacy, writer, schema, and generator rules. |
| `TH-04` | BLOCKED | `TH-03` | Redacted privacy and verified Git closure gates. |
| `TH-05` | BLOCKED | `TH-03`, `TH-04` | Manifest-driven instance creation, upgrades, and migrations. |
| `TH-06` | BLOCKED | `TH-01`–`TH-05` | Strict validation, generated-drift checks, and command-path smoke tests. |

## Phase 2 — transactional study engine

| ID | Status | Depends on | Bounded deliverable |
|---|---|---|---|
| `TH-07` | BLOCKED | `TH-03`, `TH-06` | Canonical cards and active-turn binding. |
| `TH-08` | BLOCKED | `TH-07` | Atomic, idempotent session and turn transactions. |
| `TH-09` | BLOCKED | `TH-08` | Idempotent canonical review projection. |
| `TH-10` | BLOCKED | `TH-08`, `TH-09` | Canonical-state consolidation and readiness projections. |
| `TH-11` | BLOCKED | `TH-10` | Selective, bounded context packing. |

## Phase 3 — regression learning and explainability

| ID | Status | Depends on | Bounded deliverable |
|---|---|---|---|
| `TH-12` | BLOCKED | `TH-06`; expand after `TH-08` | Fictional lived-in regression laboratory. |
| `TH-13` | BLOCKED | `TH-08`, `TH-12` | Privacy-safe incident regressions. |
| `TH-14` | BLOCKED | `TH-08`–`TH-10` | Read-only provenance and explain commands. |
| `TH-15` | BLOCKED | `TH-03`, `TH-06` | Trusted-instruction and untrusted-content boundaries. |
| `TH-16` | BLOCKED | `TH-07`, `TH-08` | Blind grading and uncertainty holds. |
| `TH-17` | BLOCKED | `TH-07`, `TH-10` | Objective and source-drift monitoring. |
| `TH-18` | BLOCKED | `TH-10`, `TH-11`, `TH-17` | Evidence dimensions and deterministic utility planning. |
| `TH-19` | CONTINUOUS | Each affected slice | Property and failure-injection coverage. |
| `TH-20` | BLOCKED | `TH-10`, `TH-12`, `TH-19` | Algorithm versioning and shadow comparisons. |
| `TH-21` | BLOCKED | `TH-06`, `TH-12`, `TH-20` | Candidate/stable promotion pipeline. |

## Phase 4 — operational follow-ons

| ID | Status | Depends on | Bounded deliverable |
|---|---|---|---|
| `TH-22` | BLOCKED | `TH-08`, `TH-09` | Typed, narrow, expiring human overrides. |
| `TH-23` | BLOCKED | `TH-06`, stable commands | Content-free local performance telemetry. |
| `TH-24` | EXTERNAL | `TH-21` | Metadata-only private fleet contract. |
| `TH-25` | DEFERRED | Stable `TH-01`–`TH-21` interfaces | Separate versioned core from template and instance state. |

## Implemented pending Git closure

- 2026-07-12 — **TH-02 fast-path integrity:** Ported public-safe lessons from
  lived-in instance operation. Targeted validation now reads canonical
  evidence before compaction, rejects missing selectors and duplicate IDs,
  and checks exact cross-references. Review selection is read-only, scheduling
  is idempotent with explicit positive learning steps, scheduling failures
  abort activity preflight, and touched state writers use atomic replacement.
  Added generic drill-scope, ambiguity, evidence-weight, option-length-bias,
  and time-hermetic regression coverage. All discovered tests passed. The
  slice remains open under the binding closure policy because no commit or push
  was authorized.

## Done

- 2026-07-14 — **public naming compatibility:** Adopted StudyState, StateSpec,
  and State-Centric Engineering in current public and operator surfaces while
  preserving repository names, paths, schemas, environment variables, history,
  and other machine identifiers as compatibility contracts. Added an explicit
  migration boundary; no learner instance or private learner data was touched.
- 2026-07-10 — **TH-01 Slice A:** Added the shared mode/remote guard,
  template learner-operation refusal, temporary-instance demo path coverage,
  and the template/learner planning split. Required Slice A acceptance checks
  passed; no commit or push was performed.
- 2026-07-10 — **planning-integration:** Integrated the technical audit into
  the approved specification, dependency-ordered backlog, and bounded
  foundation plan. No product implementation, learner-state update, commit,
  or push was performed.
- 2026-06-29 — **fast-drill-mode:** Implemented the generic fast-drill
  checkpoint speed layer on `feat/fast-drill-mode`.
- 2026-06-27 — **source-check-completion-flow:** Added deterministic source
  checking and freshness-aware activity routing.
