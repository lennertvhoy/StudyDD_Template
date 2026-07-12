# StudyDD Transactional Hardening Program

> **Program ID:** `TH`
> **Status:** Approved for phased implementation
> **Recorded:** 2026-07-10
> **Scope:** Generic, public-safe improvements to `StudyDD_Template`
> **Immediate implementation plan:** `docs/superpowers/plans/2026-07-10-core-safety-foundation.md`

## Purpose

StudyDD has strong policy, auditability, source-freshness, and conservative-readiness foundations. Its main technical risk is that important invariants are still enforced by agent discipline across several independently mutable files.

This program turns those prose obligations into deterministic commands, schemas, transactions, projections, and gates while preserving the repo-native, plain-file design.

The target outcome is:

> A low-capability coding agent can safely run the supported command for one bounded operation, receive a precise failure when a precondition is not met, and cannot accidentally create a plausible-looking partial state.

## Audit provenance and baseline rule

The source audit was anchored to public `origin/main` commit `27e153d57226560a09c50294e97fea54cf31b71d` dated 2026-06-30. This program was recorded from local branch `feat/fast-drill-mode` at `5ae40397daed832e123eacf7d37a86cab6c58fc2`.

Those commits are provenance, not implementation assumptions. Before changing code, every implementation agent must:

1. verify the current repo root, mode, exact remote, branch, HEAD, and worktree;
2. compare the current branch with current `origin/main` without rewriting history;
3. reproduce the specific defect on the current baseline;
4. mark a finding `already-fixed`, `still-reproducible`, or `superseded` in the implementation handoff;
5. preserve unrelated and branch-specific work.

Do not copy code mechanically from this specification when the current implementation has moved. The invariant and acceptance test are authoritative.

## Safety and scope constraints

- This repository is the public template. Never add real learner state, targets, answers, evidence, identifiers, URLs, or private incident content.
- Never edit a personal learner instance or any repository outside the current StudyDD root while implementing this program.
- Real failures may contribute only privacy-safe failure classes and synthetic reproductions.
- Do not use a personal learner repository as a committed fixture or CI dependency.
- Do not install dependencies without explicit user consent. Phase 1 must use the current dependency set and standard library where possible.
- Do not push, merge, rewrite history, or open a PR unless explicitly instructed.
- One backlog slice should produce one reviewable behavior change. Do not combine later redesign work into a foundation slice.
- Update `state/STUDY_BACKLOG.md` only after proof exists. A passing test or validation command is required before an item can move to Done.

## Architectural decisions

These are program decisions, not options for future agents to reopen casually.

### Plain-file, deterministic core

Keep StudyDD repo-native. A database, daemon, service bus, or hosted control plane is not required. Shared behavior moves into a deterministic Python package; `scripts/` become thin compatibility wrappers.

Target template layout:

```text
studydd/                    deterministic engine
schemas/                    machine-checkable contracts
instance_seed/              resettable learner-instance seed
migrations/                 versioned instance migrations
protocols/                  explanatory policy, not execution truth
study_skills/               tutoring policies
EXAMPLES/                   template-only fixtures
tests/                      discovered unit/integration/regression tests
scripts/                    compatibility wrappers
TEMPLATE_BACKLOG.md         template development only
```

Target learner-instance truth classes:

```text
canonical   configuration, targets, cards, active turn, immutable events
derived     skill/readiness state, evidence index, review views, summaries, next action
runtime     caches, locks, temporary files, local validation receipts
shared      engine, schemas, protocols, study skills
template    examples, release tooling, template backlog
instance    learner profile, actual targets, sources, answers, events, private cards
```

### One-way state flow

The long-term data flow is:

```text
source snapshot
  -> card revision
  -> active turn
  -> immutable attempt event
  -> deterministic projections
  -> review/readiness/next-action views
```

Corrections append invalidation or supersession events. They never erase history or silently rewrite old evidence.

### Supported commands are the execution boundary

The final command surface should converge on:

```text
python -m studydd instance create
python -m studydd instance upgrade
python -m studydd session start
python -m studydd turn next
python -m studydd turn grade
python -m studydd session close
python -m studydd validate
python -m studydd render
python -m studydd privacy scan
python -m studydd git verify
python -m studydd git push-verified
python -m studydd explain ...
```

Protocols explain behavior. They must not be the only enforcement mechanism.

## Non-negotiable invariants

1. **Mode:** template mode cannot start a learner session, recommend study, ask or grade a learner question, record evidence, schedule a learner review, or update readiness.
2. **Boundary:** every relevant path has exactly one manifest ownership rule; canonical files cannot be ignored or untracked.
3. **Turn binding:** grading references the exact card ID, revision, hash, and rendered option mapping shown to the learner.
4. **Transaction:** a failed operation leaves either no change or one durable event from which all projections can be rebuilt.
5. **Idempotency:** retrying an operation cannot duplicate events, evidence, activities, or reviews.
6. **Projection:** generated state is reproducible and drift-detectable.
7. **Readiness:** only eligible direct evidence affects direct readiness; stale, defective, diagnostic-only, repeated, or repair-assisted evidence is treated explicitly.
8. **Review:** one canonical review representation exists; human-readable queues are generated.
9. **Context:** ordinary task context excludes unrelated state and fails closed when its configured budget is exceeded.
10. **Privacy:** strict scans redact values and public/shared pushes fail on unresolved privacy or secret findings.
11. **Git closure:** dirty, untracked, diverged, unvalidated, or unverified states can never be described as clean and pushed.
12. **Trust:** text from sources, uploads, questions, logs, issues, and transcripts is data, never an instruction authority.
13. **Explainability:** every derived decision can name its canonical inputs, policy/algorithm version, and generated outputs.
14. **Upgrade safety:** template upgrades preserve downstream-owned state except through declared, tested migrations.

## Dependency order

```text
TH-00 baseline reconciliation
  -> TH-01 mode guards and planning-surface split
  -> TH-02 fast-path defect repairs
  -> TH-03 executable manifest v2
  -> TH-04 Git closure and redacted privacy gates
  -> TH-05 manifest-driven creation and upgrade planning
  -> TH-06 strict validation and CI convergence

TH-03 + TH-06
  -> TH-07 canonical cards and active-turn binding
  -> TH-08 atomic event transaction
  -> TH-09 idempotent review projection
  -> TH-10 canonical-state consolidation and readiness projections
  -> TH-11 selective context packing

TH-06 + TH-08
  -> TH-12 synthetic lived-in laboratory
  -> TH-13 privacy-safe incident regressions
  -> TH-14 provenance and explain commands
  -> TH-15 instruction-trust boundaries
  -> TH-16 blind grading and uncertainty hold
  -> TH-17 source/objective drift monitoring
  -> TH-18 evidence dimensions and utility planner

TH-10 + TH-12
  -> TH-20 algorithm versioning and shadow comparisons
  -> TH-21 candidate/stable promotion pipeline

TH-19 property/failure-injection tests apply to every slice.
TH-22 through TH-25 are follow-on operational capabilities.
```

## Work packages

### Phase 0 — reconcile before implementation

#### TH-00 — Reproduce and classify the audit findings

- **Priority:** P0
- **Depends on:** none
- **Status:** ready
- **Purpose:** prevent an agent from implementing against a stale commit or overwriting fast-drill work.

Required proof:

- record current root, mode, remote, branch, HEAD, upstream, and full porcelain status;
- run the current validator and test baseline;
- create a finding matrix covering all ten original defects;
- for each defect, cite the current file/function/test and classify it;
- do not change production behavior in this task.

Exit condition: the next agent can identify the exact current reproduction for `TH-01` without relying on the historical audit text.

### Phase 1 — core safety foundation

#### TH-01 — Central mode guards and template/learner planning split

- **Priority:** P0 critical
- **Depends on:** TH-00
- **Status:** next
- **Implementation plan:** `docs/superpowers/plans/2026-07-10-core-safety-foundation.md`, Slice A

Required behavior:

- introduce one reusable `RepoMode`/`ModeViolation` precondition;
- validate mode and remote compatibility before learner-state loading or mutation;
- supported study commands fail with stable `INSTANCE_REQUIRED` output in template mode;
- demo behavior is allowed only when it operates on a temporary synthetic instance;
- `build_context_pack.py --task start_session` cannot produce a learner recommendation in template mode;
- move template engineering work toward `TEMPLATE_BACKLOG.md`; learner next-action state must not inherit template development work.

Acceptance:

```text
template start/plan/ask/grade/record/review operations fail before learner state loads
no template test expects retrieval_question as a template-mode action
demo replay still works only through a temporary instance
existing template validator passes
```

#### TH-02 — Repair concrete fast-path defects

- **Priority:** P0 critical
- **Depends on:** TH-00; preferably TH-01
- **Status:** implemented; Git closure pending (2026-07-12)

Required behavior:

- `validate_touched_state.py` exits non-zero when no selector is supplied;
- new evidence is validated from canonical input even when the derived index is stale;
- requested skill and evidence references match exactly;
- duplicate evidence, activity, and review IDs fail;
- `record_activity_result.py` adds the evidence reference to the affected skill;
- review-scheduling failures propagate and abort the enclosing operation;
- writes use temporary files and atomic replacement where feasible;
- `select_next_study_action.py` is read-only;
- review learning steps use explicit durations, resolving the zero-day/positive-interval contradiction.

Acceptance: focused regression tests demonstrate every defect before and after the fix.

#### TH-03 — Executable manifest v2 and explicit Git boundaries

- **Priority:** P0 critical
- **Depends on:** TH-01
- **Status:** queued
- **Implementation plan:** `docs/superpowers/plans/2026-07-10-core-safety-foundation.md`, Slice B

Manifest rules must support:

```text
boundary
role
tracked
copied_to_instance
privacy class
allowed writers
schema
generator command
glob ownership
runtime allowlist
```

Validation must fail for unmatched or multiply matched tracked files, ignored/untracked canonical files, tracked runtime files, instance data in template mode, template-only files in instances, missing schemas, or generated files without generators.

Replace broad `.studydd/` ignore behavior with explicit runtime paths. Do not hide canonical questions, active turns, crash-recovery events, or future projections under a broad ignored directory.

#### TH-04 — Redacted privacy and verified Git closure

- **Priority:** P0 critical
- **Depends on:** TH-03
- **Status:** queued
- **Implementation plan:** `docs/superpowers/plans/2026-07-10-core-safety-foundation.md`, Slice C

Required behavior:

- privacy findings print path, line, and category, never the matched value;
- strict tracked/staged/history modes are supported;
- closure checks root, exact normalized remote, branch, staged/unstaged/untracked/ignored state, upstream, ahead/behind/diverged state, and validation receipt fingerprint;
- only `STUDYDD_CLOSURE=CLEAN_VALIDATED_AND_PUSHED` represents verified closure;
- all other machine states use explicit non-success codes;
- a push wrapper verifies remote equality after push and fetch.

Do not run a real push in unit tests. Use temporary local bare remotes.

#### TH-05 — Manifest-driven instance creation, upgrades, and migrations

- **Priority:** P0 high
- **Depends on:** TH-03 and TH-04
- **Status:** queued

Creation must copy only shared and seed entries, reset seed state, reject a destination inside the template, reject the template remote as the destination remote, avoid real names, initialize bootstrap mode, record exact template provenance, run strict validation/privacy checks, and emit a closure report.

Upgrade planning must come from manifest boundaries and versioned migrations. It must never manually copy generic directories or overwrite downstream-owned state.

#### TH-06 — One strict validation command and CI discovery

- **Priority:** P0 high
- **Depends on:** TH-01 through TH-05
- **Status:** queued

Converge checks behind:

```text
python -m studydd validate --mode template --strict
python -m studydd validate --mode instance --strict
python -m studydd validate --changed
```

Split validation by schema, boundary, Git state, questions, events, projections, reviews, readiness, privacy, and template safety. CI must use test discovery, strict validation, manifest/Git checks, privacy scans, generated-state drift checks, and a fresh-instance command-path smoke test.

Do not add `pytest`, `jsonschema`, or `ruff` without explicit dependency consent. If consent is not available, first implement equivalent coverage using the existing test style and standard library, then leave the dependency migration as a separate proposal.

### Phase 1 exit gate

Phase 1 is complete only when:

```text
template mode cannot produce learner actions
fresh instances contain no template-development next action
canonical files are tracked and not ignored
fast-path validation succeeds immediately after a valid update
privacy output contains no matched values
dirty/untracked/diverged/unpushed states cannot report closure
CI discovers and executes every required test
```

### Phase 2 — transactional study engine

#### TH-07 — Canonical card registry and active-turn binding

- **Priority:** P1 critical
- **Depends on:** TH-03 and TH-06
- **Status:** blocked by Phase 1

Add deck/card schemas, strict global IDs, exact source dependencies, readiness eligibility, card lifecycle, deterministic rendering seed, stable option IDs, persisted visible-label mapping, and an active-turn record containing card revision/hash.

Generated questions must be persisted as cards before display. Grading from reconstructed memory is forbidden.

#### TH-08 — Atomic, idempotent study-turn transaction

- **Priority:** P1 critical
- **Depends on:** TH-07
- **Status:** blocked

Implement `session start`, `turn next`, `turn grade`, and `session close`. Use a transaction lock and idempotency key. The event append is the durable operation; projections build in a temporary area, validate, and replace atomically.

Failure at any injected boundary leaves no change or a recoverable durable event.

#### TH-09 — One idempotent review scheduler

- **Priority:** P1 high
- **Depends on:** TH-08
- **Status:** blocked

Use stable review keys at card/objective/concept scope, explicit learning/relearning durations, four deterministic ratings (`again`, `hard`, `good`, `easy`), upsert behavior, and immutable override events. Generate Markdown queues from structured review truth. Next-action selection remains pure.

Do not implement full FSRS until clean card-level four-rating history exists.

#### TH-10 — Remove duplicate canonical state and derive readiness

- **Priority:** P1 high
- **Depends on:** TH-08 and TH-09
- **Status:** blocked

Reduce `STUDY_STATE.yaml` to routing/session state, remove duplicate skill representations and file-local template versions, make immutable JSONL events canonical, and generate skill, evidence, review, context, summary, and next-action projections.

Readiness must distinguish direct evidence from transfer estimates and later expose objective coverage and retention confidence. Invalidations append events; they do not delete history.

#### TH-11 — Selective, fail-closed context packing

- **Priority:** P1 high
- **Depends on:** TH-10
- **Status:** blocked

Build task-specific projections instead of embedding full canonical files. Enforce file, byte, character/token, evidence-item, and review-item budgets as failures. Separate weak, blocked, unassessed, transfer-estimated, and backlog classifications.

Growth tests must prove context size is independent of repository age for ordinary grading.

### Phase 2 exit gate

```text
a complete turn uses supported commands only
the exact shown card and key mapping are recoverable
retries do not duplicate events or reviews
manual multi-file synchronization is unnecessary
a crash leaves recoverable state
all projections rebuild from canonical inputs
context remains bounded as history grows
```

### Phase 3 — learning and reliability intelligence

#### TH-12 — Synthetic lived-in laboratory

- **Priority:** P1 very high
- **Depends on:** TH-06; expand after TH-08
- **Status:** queued after Phase 1

Create a deterministic fictional instance generator with hundreds of skills, thousands of cards/attempts, years of reviews, stale/fresh sources, quarantined cards, duplicate IDs, interrupted transactions, review debt, inactive targets, drift, canonical-looking untracked files, partial commits, and old schemas.

The generator must use no personal repository or private content. Expected metrics and failure injections are committed; generated large instances are temporary.

#### TH-13 — Privacy-safe incident-to-regression export

- **Priority:** P1 very high
- **Depends on:** TH-08 and TH-12
- **Status:** blocked

Export a failure signature, generalized reproduction, expected failure, and privacy report. The output must contain the failure class and affected boundaries, not learner content. Upstream fixtures are reviewed before commit.

StudyDD implements the local format. Generic cross-project support belongs in StateDD and must be changed in the StateDD repository, never from this repo.

#### TH-14 — Provenance graph and `explain` commands

- **Priority:** P1 high
- **Depends on:** TH-08 through TH-10
- **Status:** blocked

Support explanations for next action, skill, readiness, review, and closure. Every explanation names canonical inputs, excluded evidence, policy/algorithm versions, and affected projections. Explanations are read-only and deterministic.

#### TH-15 — Instruction-trust boundaries

- **Priority:** P1 high
- **Depends on:** TH-03 and TH-06
- **Status:** queued after Phase 1

Declare trusted instructions, trusted data, and untrusted content. Imported text is data, never executable instruction. Suspicious instruction-like content is quarantined and reported without being obeyed. Agent-specific toolpacks should repeat this boundary.

#### TH-16 — Blind grading and uncertainty hold

- **Priority:** P1 high
- **Depends on:** TH-07 and TH-08
- **Status:** blocked

Free-response grading receives only the bound card/rubric, response, permitted source snapshot, and grading policy. It must not see current readiness, past score, expected ability, or motivational notes. Low-confidence, ambiguous, or conflicting grades create `needs_adjudication` and cause no readiness change.

#### TH-17 — Official objective and source-drift monitoring

- **Priority:** P1 high
- **Depends on:** TH-07 and TH-10
- **Status:** blocked

Store source and section hashes; bind cards to exact source sections. A changed section stales only dependent cards and reduces confidence only for affected current claims. Historical attempts remain historical facts.

#### TH-18 — Evidence dimensions and deterministic utility planning

- **Priority:** P1 medium-high
- **Depends on:** TH-10, TH-11, TH-17
- **Status:** blocked

Separate practice, repair, assessment, delayed review, mixed checkpoint, and timed-exam evidence. Expose direct competence, retention, transfer, and timed performance rather than one opaque score.

Rank candidate actions using explicit versioned factors such as review urgency, objective gap, uncertainty reduction, blueprint weight, prerequisite importance, freshness, interleaving, repetition penalty, time, and energy. Always support `--explain`.

#### TH-19 — Property-based and failure-injection coverage

- **Priority:** P0/P1 cross-cutting
- **Depends on:** each affected slice
- **Status:** continuous

Every new subsystem adds invariant tests. Required properties include deterministic rendering, stable correct option IDs, idempotent replay, non-increasing readiness after defect invalidation, no false varied-evidence credit, concept-specific review satisfaction, idempotent projections, crash recovery, strict closure, update idempotency, downstream ownership, and duplicate-key rejection.

If a property-testing dependency is desired, request consent separately. Failure injection itself must be available with the existing dependency set.

#### TH-20 — Version algorithms and compare in shadow mode

- **Priority:** P2 high
- **Depends on:** TH-10, TH-12, TH-19
- **Status:** blocked

Record readiness, review, and planner algorithm versions on events/projections. Candidate algorithms write only shadow projections until invariants and material-difference reports are reviewed. Promotion never silently rewrites learner truth.

#### TH-21 — Development/candidate/stable promotion pipeline

- **Priority:** P2 high
- **Depends on:** TH-06, TH-12, TH-20
- **Status:** blocked

Promote through synthetic downstream fixtures and a temporary private canary clone/worktree. Trial upgrades report preserved canonical files, migrations, projection/readiness/review differences, validation, context size, privacy, and rollback point. A personal instance is never an automatic destructive deployment target.

### Phase 4 — operational follow-ons

#### TH-22 — Typed, scoped, expiring overrides

- **Priority:** P2 medium
- **Depends on:** TH-08 and TH-09
- **Status:** blocked

Overrides name rule, scope, approver, time, expiry, reason, remaining risk, and closure effect. They cannot turn unverified truth into verified truth or permit privacy/destructive violations.

#### TH-23 — Local content-free operational telemetry

- **Priority:** P2 medium
- **Depends on:** TH-06 and stable commands
- **Status:** blocked

Record operation, duration, counts/bytes, context size, cache hit, gate level, result, retries, and recovery events. Never record prompts, answers, learner data, contents, or private URLs.

#### TH-24 — Private fleet registry contract

- **Priority:** P3 medium
- **Depends on:** TH-21
- **Status:** external/private design only

Define a metadata-only contract for template/instance version, channel, last update, CI, and migration status. Do not create or populate a private fleet repository from this public repo. Never store learner state, readiness, answers, private URLs, or absolute paths.

#### TH-25 — Separate versioned engines from templates

- **Priority:** P3 long-term
- **Depends on:** stable TH-01 through TH-21 interfaces
- **Status:** deferred

Extract `statedd-core` and `studydd-core` only after command, event, schema, manifest, and migration contracts stabilize. Preserve a vendored/self-contained option with lockfiles recording exact source commits and hashes.

## Regression catalogue

The synthetic lab and incident exporter must eventually cover these generalized failure classes:

1. logs grow until whole-file loading violates budgets;
2. duplicate current-state files drift after multi-file writes;
3. human and machine review queues diverge;
4. defective questions contaminate readiness;
5. broad ignore rules hide meaningful state;
6. a narrow commit omits related canonical/generated/untracked work;
7. a fast operator updates only the obvious file;
8. derived summaries are stale but treated as current;
9. a free-form question loses the exact shown answer key;
10. inactive historical targets pollute active context;
11. duplicate retries create repeated evidence/reviews;
12. interrupted transactions leave partial projections;
13. old schema instances fail or mutate unexpectedly during upgrade;
14. untrusted imported text attempts to override agent policy;
15. algorithm changes silently alter learner truth.

## Progress protocol for future agents

At the start of an implementation session:

1. read `AGENTS.md`, mode/version/manifest, `NEXT_ACTIONS.md`, `state/STUDY_BACKLOG.md`, this specification, and the referenced active plan;
2. run the repo/mode/Git checks and baseline validation;
3. work only on the one `NEXT_ACTIONS.md` item;
4. reproduce the defect before patching;
5. do not start a dependent item when the acceptance gate is not green.

At handoff:

1. report finding classification and exact acceptance commands;
2. list files read/written and tests run;
3. report root, branch, HEAD, push state, and full worktree state;
4. update the backlog item only when proof passes;
5. move exactly one unblocked successor into `NEXT_ACTIONS.md`;
6. never call a task complete because code was written—completion requires its acceptance proof.

## Success definition

This program is complete when a fresh synthetic learner instance can be created, upgraded, run through a bound question/grade/review transaction, interrupted and recovered at every boundary, rendered and strictly validated, explained back to canonical inputs, privacy-scanned without value leakage, and verified clean/pushed—without a coding agent manually synchronizing duplicate truth.
