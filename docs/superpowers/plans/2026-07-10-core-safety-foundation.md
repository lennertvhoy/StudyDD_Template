# StudyDD Core Safety Foundation — Implementation Plan

> **Program:** `TH` (`docs/superpowers/specs/2026-07-10-transactional-hardening-program.md`)
> **Status:** Slice A complete; Slice B ready; Slice C blocked by its predecessor
> **Scope:** Central mode guards, executable manifest boundaries, redacted privacy, and verified Git closure
> **Current next action:** Review and close the implemented TH-02 change set;
> then implement Slice B only

## Goal

Make it technically impossible for supported StudyDD commands to perform learner operations in the public template, then establish the boundary and closure machinery that later transactions can trust.

This plan is intentionally split into three independently reviewable slices:

| Slice | Backlog ID | Outcome | Starts when |
|---|---|---|---|
| A | `TH-01` | Central mode guard and template/learner planning split | Complete |
| B | `TH-03` | Manifest v2 and Git ownership enforcement | Ready after the current TH-02 worktree receives Git closure |
| C | `TH-04` | Redacted privacy and verified Git closure | Slice B acceptance is green |

Do not implement Slices B or C in the same coding session as Slice A unless the user explicitly expands the scope after reviewing Slice A.

## Execution rules

- Work only inside the current StudyDD repository.
- Keep all fixtures generic and fictional.
- Do not use or inspect a personal learner instance.
- Do not install `pytest`, `jsonschema`, `ruff`, or any other dependency without explicit user consent.
- Use the current test style unless dependency installation is authorized.
- Do not merge, rebase, reset, push, or open a PR without explicit instruction.
- Preserve fast-drill and all unrelated work.
- Reproduce each defect before patching it.
- A slice is not complete until all acceptance commands pass and the worktree is truthfully reported.

## Slice A — TH-01 central mode guard

### A0. Reconcile the current baseline without changing production files

Run:

```bash
pwd
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git rev-parse HEAD
git status --porcelain=v2 --untracked-files=all
git log -1 --format=fuller
python3 scripts/check_studydd.py
```

If network access is available, refresh remote metadata with a non-destructive fetch and then inspect divergence:

```bash
git fetch --prune origin
git rev-list --left-right --count origin/main...HEAD
```

Stop and report rather than rebasing or switching branches when:

- the root or remote is not the expected template;
- the worktree has unrelated changes that overlap this slice;
- the mode is not `template`;
- current branch history makes the intended base ambiguous.

This roadmap was recorded on `feat/fast-drill-mode`. Unless the user explicitly names that feature branch as the hardening base, do not add Slice A code to it while its merge status is unresolved. Complete the read-only classification and hand off the branch blocker.

Create a short finding table in the handoff, not a new state file:

| Historical finding | Current classification | Reproduction/test |
|---|---|---|
| Template planning returns learner recommendation | `still-reproducible`, `already-fixed`, or `superseded` | exact command/test |
| Mode checks are duplicated | classification | exact references |
| Template backlog is copied/ambiguous | classification | exact references |

### A1. Add failing mode-contract tests first

Create `scripts/test_mode_guards.py` using temporary repository copies and the current dependency set.

Required test cases:

1. `template`, `bootstrap`, and `learner_instance` parse as known modes.
2. An unknown or missing mode fails closed.
3. Template mode plus the exact template remote is valid for template-maintenance operations.
4. Template mode plus a non-template remote fails with `MODE_REMOTE_MISMATCH`.
5. Learner-instance mode plus the template remote fails with `MODE_REMOTE_MISMATCH`.
6. Learner-instance mode plus a non-template remote is valid for learner operations.
7. Remote normalization handles HTTPS/SSH spelling deliberately, but never uses substring matching.
8. `plan_learning_activity.py` in template mode exits non-zero with `INSTANCE_REQUIRED` and does not print a retrieval recommendation.
9. `build_context_pack.py --task start_session` in template mode exits non-zero with `INSTANCE_REQUIRED` before writing a learner context pack.
10. Mutating learner commands fail before changing any file in template mode.
11. Demo commands remain allowed only when their implementation creates/uses a temporary synthetic learner instance.
12. Existing temporary learner-instance smoke tests continue to work.

For no-write assertions, fingerprint relevant files before and after the refused command. At minimum cover:

```text
state/STUDY_STATE.yaml
state/SKILL_MAP.yaml
state/EVIDENCE_LOG.md
state/ACTIVITY_STATE.yaml
activities/ACTIVITY_LOG.md
reviews/REVIEW_STATE.yaml
reviews/REVIEW_QUEUE.md
sources/SOURCE_STATE.yaml
NEXT_ACTIONS.md
```

Run the new test and record the expected failures before implementing the guard:

```bash
python3 scripts/test_mode_guards.py
```

Do not weaken an existing test to make the old template retrieval recommendation pass. Replace that expectation with the hard template failure.

### A2. Create the reusable mode module

Create:

```text
studydd/__init__.py
studydd/mode.py
```

Required public contract:

```python
class RepoMode(StrEnum):
    TEMPLATE = "template"
    BOOTSTRAP = "bootstrap"
    LEARNER_INSTANCE = "learner_instance"


class ModeViolation(RuntimeError):
    code: str


def load_repo_mode(repo_root: Path) -> RepoMode:
    ...


def normalized_remote(value: str) -> str:
    ...


def validate_mode_remote(repo_root: Path, mode: RepoMode) -> None:
    ...


def require_mode(
    repo_root: Path,
    *allowed: RepoMode,
    operation: str,
) -> RepoMode:
    ...
```

Stable failure codes for this slice:

```text
MODE_FILE_MISSING
MODE_INVALID
REMOTE_MISSING
MODE_REMOTE_MISMATCH
INSTANCE_REQUIRED
```

Behavioral decisions:

- `require_mode` loads and validates both mode and remote compatibility.
- The template remote comparison is exact after deliberate normalization; never use `"StudyDD_Template" in remotes`.
- Support the repository's declared HTTPS template remote and its exact SSH equivalent if tests define both.
- Normalize only transport/trailing `.git`/trailing slash differences. Do not make unrelated owner/repository names equivalent.
- A violation writes a short user-safe message to stderr and returns a non-zero process status through the wrapper.
- The error message points to `protocols/INSTANTIATE_TEMPLATE.md` for `INSTANCE_REQUIRED`.
- The module does not import learner state or application-specific planners.
- Keep this module dependency-light so every command can import it early.

### A3. Inventory and guard supported learner operations

Before editing wrappers, produce the inventory with:

```bash
rg -n "STUDYDD_MODE|learner_instance|def main|ArgumentParser" scripts -g '*.py'
```

Classify each command:

```text
template maintenance
learner read
learner write
demo in temporary instance
generic pure helper
```

Guard learner operations at the earliest command boundary, before learner files are loaded or written.

Minimum commands/paths to inspect and cover:

```text
scripts/build_context_pack.py --task start_session
scripts/plan_learning_activity.py
scripts/select_next_study_action.py
scripts/plan_state_update.py
scripts/record_activity_result.py
scripts/record_source_check.py
scripts/schedule_review.py
scripts/fast_drill_mode.py start|append|end
scripts/setup_studydd.py
scripts/suggest_study_adjustment.py
scripts/analyze_voice_note.py non-demo recording path
scripts/analyze_presentation_rehearsal.py non-demo recording path
```

Do not guard pure validators, environment inspection, template creation, schema linting, or read-only generic demo helpers as learner writes. `create_instance.py` must require template mode, not learner-instance mode.

For this slice, choose one deterministic template behavior:

```text
start_session in template mode -> non-zero INSTANCE_REQUIRED
plan_learning_activity in template mode -> non-zero INSTANCE_REQUIRED
learner writers in template mode -> non-zero INSTANCE_REQUIRED
template validation/creation/temporary demo -> allowed
```

Do not emit a template-mode fallback study recommendation.

### A4. Split template engineering planning from learner study planning

The current planning files are transitional and ambiguous. Make the separation explicit without redesigning the full manifest yet.

Required result:

```text
TEMPLATE_BACKLOG.md       template engineering only
state/STUDY_BACKLOG.md   generic learner-instance seed only
NEXT_ACTIONS.md          generic learner/bootstrap next action until generated projections arrive
```

Implementation steps:

1. Move the `TH` engineering program index from `state/STUDY_BACKLOG.md` to root `TEMPLATE_BACKLOG.md` while preserving stable IDs and history.
2. Reset `state/STUDY_BACKLOG.md` to generic learner backlog placeholders; no real learner data.
3. Reset template `NEXT_ACTIONS.md` so a newly created instance does not inherit an engineering branch/PR task.
4. Teach template-oriented preflight/docs to read `TEMPLATE_BACKLOG.md` when `mode: template`.
5. Ensure learner-instance preflight continues to read `state/STUDY_BACKLOG.md` and `NEXT_ACTIONS.md`.
6. Ensure `create_instance.py` does not copy `TEMPLATE_BACKLOG.md`, or explicitly removes it from the destination until Slice B makes this manifest-driven.
7. Add focused creation/preflight tests.

Do not add learner engineering work to `CURRENT_CONTEXT.md`, `STUDY_STATUS.md`, evidence, session, review, or readiness files.

### A5. Update compatibility documentation only where required

Update the smallest set of references needed so agents follow the executable behavior:

- `AGENTS.md`: template-maintenance sessions read `TEMPLATE_BACKLOG.md`; learner study sessions read learner next-action state.
- `protocols/TEMPLATE_INSTANCE_BOUNDARY.md`: mode precondition is executable and template study commands fail.
- `protocols/INSTANTIATE_TEMPLATE.md`: refused template learner operation points here.
- `README.md`: one short note about the template-mode refusal and correct creation command.

Do not rewrite all protocols in Slice A. Later command consolidation owns that cleanup.

### A6. Slice A acceptance

Run:

```bash
python3 scripts/test_mode_guards.py
python3 scripts/test_template_instance_boundary.py
python3 scripts/test_create_instance.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_demo_replay.py
python3 scripts/test_fast_drill_mode.py
python3 scripts/check_studydd.py
git diff --check
git status --short --untracked-files=all
```

Manual assertions:

```bash
python3 scripts/plan_learning_activity.py
python3 scripts/build_context_pack.py --task start_session
```

Both commands must fail safely with `INSTANCE_REQUIRED`, must not recommend learner study, and must not change learner-state files.

Slice A exit checklist:

- [ ] The historical defect is reproduced or shown already fixed on the current baseline.
- [ ] One reusable mode/remote module owns the precondition.
- [ ] All inventoried learner write paths use it before loading/writing learner state.
- [ ] Template start/planning paths fail with stable codes.
- [ ] Temporary-instance demos pass.
- [ ] Template engineering backlog is not copied into a learner instance.
- [ ] No learner, evidence, readiness, target, review, or session state was added to the template.
- [ ] Full validation and whitespace checks pass.
- [ ] Backlog and next action are updated with evidence only after the checks pass.

Stop after Slice A and hand off. Do not begin Slice B automatically.

## Slice B — TH-03 executable manifest v2

Start only after Slice A is accepted.

### B1. Add manifest-contract tests first

Create `scripts/test_manifest_git_boundaries.py` using temporary Git repositories.

Required failing cases:

```text
tracked file has no manifest/glob owner
tracked file matches two rules
canonical file is ignored
canonical file is untracked
runtime file is tracked
instance-only data appears in template mode
template-only file appears in a created instance
generated file has no generator
manifest references a missing schema
writer is not authorized
Gitignore broadly hides a future canonical path
```

Required passing cases:

```text
every tracked file has one owner
explicit runtime allowlist is ignored and untracked
shared/seed/template/generated/runtime boundaries copy correctly
```

### B2. Add the manifest schema and loader

Create:

```text
schemas/manifest.schema.json
studydd/manifest.py
```

Manifest v2 must represent:

```yaml
manifest_version: "2.0"
paths: {}
globs: {}
runtime_allowlist: []
```

Each owned path/glob supports, where applicable:

```text
boundary: template_only | template_shared | instance_seed | instance | generated | runtime
role
tracked
copied_to_instance
privacy
writers
schema
generated_by
```

Use a deterministic precedence rule only for explicitly documented exact-path overrides. Otherwise overlapping rules fail.

If `jsonschema` is not already installed and the user has not approved it, implement the required subset validator locally and leave dependency adoption for a separate task.

### B3. Migrate the current manifest deliberately

Use `git ls-files` as the inventory. Do not mechanically mark everything `template_shared`.

Pay special attention to:

```text
AGENTS.md and protocols                 template_shared
TEMPLATE_BACKLOG.md                     template_only
EXAMPLES/** and release docs            template_only
state/LEARNER_PROFILE.yaml              instance_seed
actual targets/cards/events             instance
derived views                           generated
.studydd cache/lock/receipts/tmp         runtime
```

Resolve `NEXT_ACTIONS.md`, learner backlog, question banks, active turns, and checkpoints explicitly. No tracked path may remain ambiguous.

### B4. Replace broad ignore rules

Remove the broad `.studydd/` rule. Ignore only declared runtime paths, including:

```text
.studydd/context_pack.md
.studydd/state_cache.json
.studydd/validation_receipt.json
.studydd/transaction.lock
.studydd/tmp/
```

Add common secret patterns without hiding example files:

```text
.env
.env.*
!.env.example
*.pem
*.key
token_*.json
client_secret*.json
```

The manifest, not ad hoc Git command exclusions, owns runtime allowances.

### B5. Integrate manifest checks

Expose a compatibility command through the existing script surface, then have `scripts/check_studydd.py` call the shared module.

The long-term command is:

```bash
python -m studydd manifest check --git
```

Slice B may add the package CLI entry point if it remains small. Otherwise expose a thin `scripts/check_manifest.py` wrapper and record the CLI consolidation as `TH-06`.

### B6. Slice B acceptance

Run:

```bash
python3 scripts/test_manifest_git_boundaries.py
python3 scripts/test_template_instance_boundary.py
python3 scripts/test_create_instance.py
python3 scripts/check_studydd.py
git check-ignore -v .studydd/context_pack.md
git ls-files
git diff --check
git status --short --untracked-files=all
```

Acceptance:

- [ ] Every tracked file has exactly one boundary owner.
- [ ] Canonical/shared/seed files cannot be ignored or untracked.
- [ ] Runtime files cannot be tracked.
- [ ] A created instance contains no template-only planning fixture.
- [ ] Every generated path names a generator.
- [ ] Existing public fixtures remain schema/boundary valid.

Stop after Slice B and hand off.

## Slice C — TH-04 redacted privacy and verified Git closure

Start only after Slice B is accepted.

### C1. Add redaction and closure tests first

Create:

```text
scripts/test_privacy_redaction.py
scripts/test_git_closure.py
```

Use temporary working repos and local bare remotes. Never call a real network remote.

Privacy cases:

```text
matched email/phone/secret value never appears in stdout/stderr
finding reports path, line, and category
tracked, staged, and history scopes behave distinctly
strict mode exits non-zero on a finding
generic public placeholders remain allowlisted deliberately
```

Closure cases:

```text
staged change -> fail
unstaged change -> fail
meaningful untracked file -> fail
ignored canonical-like file outside runtime allowlist -> fail
missing upstream -> fail
ahead -> fail
behind -> fail
diverged -> fail
remote HEAD mismatch after fetch -> fail
stale/missing validation receipt -> fail
wrong root/remote/branch -> fail
clean validated local branch equal to local bare upstream -> exact success token
```

### C2. Redact the privacy scanner

Refactor `scripts/agent_privacy_check.py` behind a reusable module such as `studydd/privacy.py`.

Supported scopes:

```text
--tracked
--staged
--history
--redact
--fail
```

Redaction is the default for machine/CI output. Do not provide an option that prints secret values in CI.

### C3. Implement closure verification

Create `studydd/git_closure.py` and a thin compatibility wrapper.

Required checks:

```text
rev-parse --show-toplevel
remote get-url
branch --show-current
status --porcelain=v2 --untracked-files=all
ls-files --others --ignored --exclude-standard
fetch --prune
HEAD and upstream revisions
left/right divergence
manifest runtime allowlist
validation receipt fingerprint
```

Machine states:

```text
DIRTY
VALIDATION_FAILED
PRIVACY_FAILED
UNTRACKED_MEANINGFUL_FILES
NO_UPSTREAM
AHEAD
BEHIND
DIVERGED
PUSH_NOT_VERIFIED
```

The only success token is:

```text
STUDYDD_CLOSURE=CLEAN_VALIDATED_AND_PUSHED
```

### C4. Add validation receipts and verified push wrapper

A validation receipt is runtime-only and contains the validation version, timestamp, mode, HEAD, and a deterministic worktree/manifest fingerprint. Closure fails when the receipt does not describe the current state.

`push-verified` performs:

```text
strict validation
strict redacted privacy scan
pre-push cleanliness check
git push
fetch
local/remote equality check
post-push worktree check
closure receipt
```

The command must require an explicit remote and branch. It must never infer permission to push; an agent may invoke it only after the user explicitly instructs a push.

### C5. Slice C acceptance

Run:

```bash
python3 scripts/test_privacy_redaction.py
python3 scripts/test_git_closure.py
python3 scripts/agent_privacy_check.py --tracked --redact --fail
python3 scripts/test_manifest_git_boundaries.py
python3 scripts/check_studydd.py
git diff --check
git status --short --untracked-files=all
```

Do not require the current feature branch to equal its upstream during development. The closure tests prove that mismatch cannot produce success; the final handoff reports the actual branch state truthfully.

Slice C exit checklist:

- [ ] Scan output never contains matched private values.
- [ ] Every dirty/divergent/unvalidated state has a stable non-success code.
- [ ] Only a clean, validated, fetched, upstream-equal temporary repo emits the success token.
- [ ] Runtime allowlisting comes from manifest v2.
- [ ] No real push occurred during tests.

## Foundation completion gate

The foundation epic is complete only after Slices A, B, and C have each been reviewed independently and their tests pass together:

```bash
python3 scripts/test_mode_guards.py
python3 scripts/test_manifest_git_boundaries.py
python3 scripts/test_privacy_redaction.py
python3 scripts/test_git_closure.py
python3 scripts/test_create_instance.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_template_instance_boundary.py
python3 scripts/test_demo_replay.py
python3 scripts/check_studydd.py
git diff --check
```

Then update `state/STUDY_BACKLOG.md`/`TEMPLATE_BACKLOG.md` according to the planning split, record exact proof, and promote only `TH-02` or the next dependency-valid item—not the atomic transaction redesign prematurely.
