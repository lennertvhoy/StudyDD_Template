# StudyDD Public Template Hardening v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the StudyDD public template so it is easy to clone, safe to personalize, hard for agents to corrupt, and impressive to demo in five minutes.

**Architecture:** Keep the existing repo-native state model. Extend `scripts/check_studydd.py` with deterministic cross-file checks, add small Python tools for instance creation and smoke testing, add protocol documents for upgrade/provenance/privacy/wrong-repo recovery, wire GitHub Actions CI, and update `AGENTS.md`/`README.md`. All learner-state simulation stays inside temporary directories.

**Tech Stack:** Python 3, PyYAML, Git, GitHub Actions.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `state/STUDYDD_TEMPLATE_VERSION.yaml` | Template version tracking (template vs. instance origin, last upgrade). |
| `scripts/create_instance.py` | Deterministic template → learner-instance creation. |
| `scripts/test_instantiate_template.py` | Existing instantiation smoke test; make portable with repo-local Git identity. |
| `scripts/test_create_instance.py` | Focused test for `create_instance.py` path. |
| `scripts/test_study_loop_smoke.py` | Full deterministic study-loop smoke test with fake learner state. |
| `scripts/agent_privacy_check.py` | Practical privacy scan before public push. |
| `scripts/check_studydd.py` | Extended validator: version file, cross-file refs, answer-key leakage, question bank schema. |
| `docs/question-bank-schema.md` | Optional `targets/<target_id>/questions/<question_id>.yaml` schema. |
| `protocols/UPGRADE_INSTANCE_FROM_TEMPLATE.md` | Safe template → instance upgrade protocol. |
| `protocols/GIT_PROVENANCE.md` | Git identity and provenance rules. |
| `protocols/PRIVACY_REVIEW.md` | Pre-push privacy review checklist. |
| `protocols/WRONG_REPO_RECOVERY.md` | Recovery steps when an agent is in the wrong repo. |
| `PROMPTS/upgrade_instance_from_template.md` | Paste-ready upgrade prompt for coding agents. |
| `.github/workflows/validate.yml` | CI running validator + smoke tests. |
| `AGENTS.md` | Add references and fix required-read list numbering. |
| `README.md` | Add create-instance, maintenance, safety, and CI sections. |

---

### Task 1: Add template version tracking

**Files:**
- Create: `state/STUDYDD_TEMPLATE_VERSION.yaml`
- Modify: `scripts/check_studydd.py`

- [ ] **Step 1: Create version file**

```yaml
template_version: "0.5.0"
template_commit: ""
instance_created_from_template_version: ""
instance_created_from_template_commit: ""
last_template_upgrade_version: ""
last_template_upgrade_commit: ""
upgrade_history: []
```

- [ ] **Step 2: Require the file in the validator**

Add `state/STUDYDD_TEMPLATE_VERSION.yaml` to `REQUIRED_STATE_FILES` and `YAML_FILES`.

- [ ] **Step 3: Warn on empty learner-instance origin fields**

In `check_mode`, when `mode == "learner_instance"`, warn if `instance_created_from_template_version` or `instance_created_from_template_commit` are empty.

---

### Task 2: Make instantiation smoke test portable

**Files:**
- Modify: `scripts/test_instantiate_template.py`

- [ ] **Step 1: Set repo-local Git identity before first commit**

Before `git commit`, run:

```python
run(["git", "config", "user.name", "StudyDD Smoke Test"], instance)
run(["git", "config", "user.email", "studydd-smoke-test@example.invalid"], instance)
```

- [ ] **Step 2: Preserve version metadata**

After switching to bootstrap mode, populate `state/STUDYDD_TEMPLATE_VERSION.yaml` from the current template HEAD.

---

### Task 3: Add deterministic create-instance tooling

**Files:**
- Create: `scripts/create_instance.py`
- Create: `scripts/test_create_instance.py`

- [ ] **Step 1: Implement `create_instance.py`**

Behavior:
- Refuse if current repo is not `mode: template`.
- Refuse to overwrite existing non-empty target directory.
- Copy template excluding `.git`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `*.pyc`, `.DS_Store`, cache directories.
- `git init`, `git checkout -b main`, repo-local identity `StudyDD Agent` / `studydd-agent@example.invalid`, add provided remote.
- Switch `state/STUDYDD_MODE.yaml` to bootstrap.
- Write origin/version metadata to `state/STUDYDD_TEMPLATE_VERSION.yaml`.
- Run `python3 scripts/check_studydd.py` in the new instance.
- Print the exact next prompt to paste.

- [ ] **Step 2: Add focused test**

`scripts/test_create_instance.py` creates a temp target dir, runs the script, asserts bootstrap mode, asserts validation passes, and cleans up. No network/push.

---

### Task 4: Add full study-loop smoke test

**Files:**
- Create: `scripts/test_study_loop_smoke.py`

- [ ] **Step 1: Build a temporary instance**

Use `scripts/create_instance.py` or direct copy to create a temp learner instance.

- [ ] **Step 2: Move through lifecycle**

Bootstrap → learner_instance, create one fake target, one fake skill, one fake question record, simulate answer/grade, add evidence, update readiness conservatively, schedule review, append session log, update `NEXT_ACTIONS.md`.

- [ ] **Step 3: Validate and assert**

Run `python3 scripts/check_studydd.py` and assert it passes. Assert no state-reference drift.

---

### Task 5: Strengthen cross-file validation

**Files:**
- Modify: `scripts/check_studydd.py`

- [ ] **Step 1: Evidence reference checks**

- Every evidence reference in `state/SKILL_MAP.yaml` must appear in `state/EVIDENCE_LOG.md`.
- Every review item `Evidence ID` must appear in `state/EVIDENCE_LOG.md`.
- Every session-log `Evidence added` reference must appear in `state/EVIDENCE_LOG.md`.

- [ ] **Step 2: Review-item skill checks**

Every review item `Skill ID` must match a skill in `state/SKILL_MAP.yaml`.

- [ ] **Step 3: Active question consistency**

If `state/STUDY_STATE.yaml` declares `active_focus.next_question` and `NEXT_ACTIONS.md` declares a question ID, they must match.

- [ ] **Step 4: Readiness evidence rules**

- Status `demonstrated` requires evidence (join `practiced`/`confirmed`).
- Readiness ≥ 70 requires evidence.
- Warn when high readiness cannot be verified as varied/repeated from the current schema.

---

### Task 6: Add answer-key leakage heuristics

**Files:**
- Modify: `scripts/check_studydd.py`

- [ ] **Step 1: Scan learner-facing target surfaces**

Scan `targets/**` Markdown/YAML files, excluding `targets/<id>/questions/` (answer-key storage), `EXAMPLES/`, `PROMPTS/`, and `protocols/`.

- [ ] **Step 2: Flag leakage patterns**

Patterns (case-insensitive): `correct answer`, `answer_key`, `[correct]`, `private answer key`, `expected answer`, `rubric`.

Report warnings (do not fail the template on protocols).

---

### Task 7: Add question bank schema documentation

**Files:**
- Create: `docs/question-bank-schema.md`
- Modify: `scripts/check_studydd.py` (optional validator support)

- [ ] **Step 1: Document schema**

Define `targets/<target_id>/questions/<question_id>.yaml` with required fields: `id`, `target_id`, `skill_id`, `cognitive_level`, `difficulty`, `source_ref`, `public_prompt`, `private_answer_key`, `rubric`, `common_traps`, `transfer_probe`, `last_used`, `cooldown_days`.

- [ ] **Step 2: Optional validator support**

If question files exist, validate required fields; do not require a question bank in every target.

---

### Task 8: Add instance upgrade protocol

**Files:**
- Create: `protocols/UPGRADE_INSTANCE_FROM_TEMPLATE.md`

- [ ] **Step 1: Document safe upgrade flow**

Rules:
- Verify `learner_instance` mode.
- Verify template source path/remote.
- Compare versions.
- Protect learner state files and target folders.
- Upgrade generic files first (protocols, prompts, scripts, docs, validator, examples only if useful).
- Run validation before and after.
- Commit upgrade separately.
- Final handoff lists copied/merged/skipped/protected files.

---

### Task 9: Add paste-ready upgrade prompt

**Files:**
- Create: `PROMPTS/upgrade_instance_from_template.md`

- [ ] **Step 1: Write agent-facing prompt**

Instruct the agent to confirm learner-instance mode, locate template source, inspect versions, protect learner state, copy/merge generic improvements only, validate before/after, commit/push only when instructed, report limitations.

---

### Task 10: Add Git provenance protocol

**Files:**
- Create: `protocols/GIT_PROVENANCE.md`

- [ ] **Step 1: Document required checks**

Agents must inspect and report:

```bash
git config --show-origin --get user.name || true
git config --show-origin --get user.email || true
git log -1 --pretty=fuller || true
```

Recommend repo-local identity `StudyDD Agent` / `studydd-agent@example.invalid`. No history rewrite unless explicitly instructed.

---

### Task 11: Add privacy review protocol and helper

**Files:**
- Create: `protocols/PRIVACY_REVIEW.md`
- Create: `scripts/agent_privacy_check.py`

- [ ] **Step 1: Document pre-push scan**

Scan for personal names, emails, health/recovery details, employer-sensitive info, proprietary exam dumps, credentials/secrets/tokens, private notes.

- [ ] **Step 2: Implement helper**

`scripts/agent_privacy_check.py` warns by default; simple regex/keyword heuristics. Do not create a full compliance framework.

---

### Task 12: Add wrong-repo recovery protocol

**Files:**
- Create: `protocols/WRONG_REPO_RECOVERY.md`

- [ ] **Step 1: Document recovery steps**

Stop, print `pwd`, repo root, remote, branch, status, `state/STUDYDD_MODE.yaml`, do not commit/push, report touched files, revert only if safe/approved, never repair learner state inside the template, never personalize the template.

---

### Task 13: Add CI

**Files:**
- Create: `.github/workflows/validate.yml`

- [ ] **Step 1: Minimal workflow**

Trigger on push to `main` and pull requests. Minimal permissions. Steps:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with: { python-version: "3.11" }
- run: pip install pyyaml
- run: python3 scripts/check_studydd.py
- run: python3 scripts/test_instantiate_template.py
- run: python3 scripts/test_study_loop_smoke.py
- run: git diff --check
```

---

### Task 14: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Add lifecycle references**

Add references to template version tracking, `create_instance.py`, upgrade protocol, provenance protocol, privacy protocol, wrong-repo recovery protocol, study-loop smoke test, and CI validation.

- [ ] **Step 2: Fix required-read list numbering**

Current list has duplicate `13`, `14`. Renumber sequentially and add new protocols.

---

### Task 15: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add concise sections**

- Create an instance with the script.
- Maintaining learner instances after template updates.
- Public/private safety.
- Validation and CI.

Keep the README brief.

---

## Self-Review

**Spec coverage:** Each numbered requirement from the user spec maps to a task above.

**Placeholder scan:** No `TBD`/`TODO` placeholders remain; file paths and behaviors are explicit.

**Type consistency:** Version field names match `state/STUDYDD_TEMPLATE_VERSION.yaml`. Mode values use the existing `template`/`bootstrap`/`learner_instance` vocabulary.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-24-studydd-public-template-hardening.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks.
2. **Inline Execution** — execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

Which approach?
