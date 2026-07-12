# Evidence 014 — Lifecycle Adoption Golden-Path Privacy and Conflict Review

**Review scope:** read-only adversarial review for `GOLDEN-PATH-MEGA-001`, performed from the designated StudyDD worktree on 2026-07-12. No code, lifecycle manifest, project-state file, or script was changed.

## Refs reviewed

| Repository/ref | Observed revision | Disposition |
|---|---|---|
| StudyDD `origin/main` | `27e153d57226560a09c50294e97fea54cf31b71d` | Baseline |
| StudyDD `origin/feat/source-check-completion-flow` (PR #4) | `afacc307c208a4c83eefa9ee3d65d17aa68ce7b4` | Open-PR ref; not treated as accepted source |
| StudyDD `origin/feat/fast-drill-mode` (PR #5) | `5ae40397daed832e123eacf7d37a86cab6c58fc2` | Open/conflicting ref; not treated as accepted source |
| StudyDD `origin/wip/studydd-active-agent-handoff-2026-07-12` | `49abc8bef6d58a262dc5d0d73fd4d07d6a007e96` | WIP candidate scanned; no local ref identifies it as PR #6 |
| StatePort `HEAD` | clean local `main` checkout | Cross-repository authority and fixture review |

No `refs/pull/*` or explicitly named PR #6 ref exists in the available local StudyDD refs. The WIP ref above is therefore a limitation, not a confirmed PR #6 mapping.

## Findings

### F-01 — Tracked machine-local and private-canary identifiers remain in public-facing records (medium)

StudyDD tracked docs and test/provenance records contain `/home/ff` and explicit `Study_Lenny` examples, including `protocols/INSTANTIATE_TEMPLATE.md:18,26-40` and `PROMPTS/create_new_instance_from_template.md:15,27-41`. StatePort contains metadata-only `Study_Lenny` references in `PROJECT_STATE.yaml:228-232`, plus a tracked local `/home/ff/CTO_Lenny` path in `docs/superpowers/specs/2026-07-05-sp-001a-design.md:5` and many absolute StatePort checkout paths in evidence/coordination records.

No learner file contents were read from the private canary, and no evidence shows learner content was copied. The issue is portability/privacy exposure of local paths, private repository identity, and operator directory names in tracked public material. Replace with placeholders or repository-relative paths in a separately scoped cleanup.

### F-02 — No private learner content, credential signature, or tracked symlink found

The StudyDD example state added by PR #5 declares `Sam` and `Pat` fictional/public-safe examples. StatePort’s `instances/demo-classdd` uses synthetic labels (`Student A/B/C`) and generic lesson content. Searches across the reviewed refs found no private key headers, GitHub/OpenAI/AWS token signatures, or tracked symlinks. This is a clean result, not evidence that future instance materialisation is safe without the lifecycle gates below.

### F-03 — StudyDD’s manifest is a runtime-loading manifest, not a complete lifecycle ownership manifest (high adoption risk)

`state/STATE_MANIFEST.yaml:14-89` is manually generated and declares 18 runtime state/context entries. A tracked-domain comparison found nine tracked paths outside it, including `state/PERFORMANCE_BUDGET.yaml`, `state/STUDY_BACKLOG.md`, `state/STUDY_STATUS.md`, `targets/README.md`, and the `README.md` files under `reviews/`, `sessions/`, and `sources/`. The three root `EXAMPLES/*` learner-like trees also have no local `STUDYDD_MODE.yaml` or `STATE_MANIFEST.yaml`.

This does not prove those files are unsafe by themselves; it proves ownership/provision/generation is not declared for the complete tracked surface. StatePort’s own `PROJECT_STATE.yaml:862` correctly records that StudyDD has no platform lifecycle manifest. During adoption, StatePort must not promote `state/STATE_MANIFEST.yaml`, `STUDYDD_MODE.yaml`, or template-version metadata into lifecycle authority. They must remain StudyDD domain/runtime contracts until a separate machine-readable lifecycle manifest, instance overlay, lock, and provenance boundary are accepted.

### F-04 — StatePort retains duplicate contract/metadata truth without consistency enforcement (medium)

Each reviewed StatePort source-like directory (`templates/classdd`, `templates/projectdd`, and both synthetic fixture directories) contains `template.yaml` plus `.statedd/manifest.yaml`; the two files carry overlapping identity/required-file declarations. The ClassDD and ProjectDD trees also contain `.statedd/contract.md`. StatePort records this limitation explicitly in `PROJECT_STATE.yaml:863-865`: `template.yaml` and `.statedd/contract.md` duplicate contract truth without consistency validation.

The lifecycle v2 manifest has the right direction—machine-readable owner, policy, sensitivity, and collision checks (`docs/LIFECYCLE_MANIFEST_V2.md:20-32`)—but the duplicate legacy documents remain an authority-conflict surface. Do not treat repository placement or prose contract text as canonical during StudyDD adoption; require one declared authority and a compatibility/read-only view for legacy consumers.

### F-05 — Open-PR-only paths and unresolved WIP must not become lifecycle input

PR #4 adds source-check and template/instance-boundary paths such as `scripts/record_source_check.py` and `state/STATE_MANIFEST.yaml`. PR #5 adds fast-drill code and two instance-like example trees under `EXAMPLES/`, and its evidence says CI was pending at its recorded head. The WIP ref adds a broad hardening set and explicitly records itself as incomplete/unreviewed. These refs overlap in shared scripts, state files, protocols, and evidence paths.

The StatePort snapshot records PR #4/#5 as open and says neither is an implicit lifecycle source (`PROJECT_STATE.yaml:209-222`, `862`). No direct StatePort code path was found that installs an open-PR-only StudyDD path. The safe disposition is to resolve one immutable accepted source, classify each path once, and reject mixed-branch adoption or evidence-only claims.

## Scans and validation

- `git status --short --branch` on both repositories: clean before this report; no unrelated changes were touched.
- Tracked symlink scan over StudyDD `origin/main`, PR #4, PR #5, WIP candidate, and StatePort refs: none found.
- Tracked path/manifest comparison: StudyDD runtime manifest covers 18 entries; 9 tracked domain/support paths are not declared; ignored generated context is intentionally absent.
- Redacted searches for `Study_Lenny`, `CTO_Lenny`, absolute paths, learner/private markers, and common credential signatures: local/canary references found as listed; no credential signatures or learner-content import found.
- `python3 scripts/check_studydd.py`: passed.
- `python3 scripts/agent_privacy_check.py`: soft pass with warnings limited to scanner keyword lists, validator pattern text, and a generic design keyword; no matched secret/value finding.
- `python3 scripts/validate_repo.py` in StatePort: passed.
- StatePort `scripts/gitleaks_scan.sh`: passed, no leaks found.
- StudyDD focused tests: instantiation, cross-platform path, and context-pack tests passed. `test_learning_activities.py` had one pre-existing time-sensitive failure: a fixture dated 2026-06-27 is classified stale on 2026-07-12, so the “fresh volatile source” assertion fails. No test or code was changed.
- StatePort focused `test_lifecycle.py`, `test_statedd_core.py`, `test_template_validator.py`, and `test_contribution_bundle.py`: all passed.
- `git diff --check` in both repositories: passed.

## Limitations and handoff

This review used local tracked content, local refs, manifests, history metadata, and read-only validators. It did not fetch or query GitHub, inspect `/home/ff/Study_Lenny` contents, run remote CI, install scanners, or prove redistribution/licensing status. The report intentionally records paths and categories without copying private values or learner content. No code or lifecycle authority was changed; follow-up should first remove local identifiers, then define and validate the missing StudyDD lifecycle ownership/provenance contract before any upgrade or materialisation claim.
