# StudyDD_Template

**Repo-native study brain for coding agents.**

StudyDD is not a human-facing app. It is a study brain operated by coding agents such as Codex, Kimi Code, Claude Code, or ChatGPT agents. The human says "Start a StudyDD session" and the agent runs the learning loop inside the repo.

Give the repo to a coding agent, tell it who you are and what you want to learn, and it maintains your study library, tutor memory, readiness tracker, spaced-repetition queue, source registry, and next-action engine in plain files.

Your progress is never hidden inside an app database or chat history.

### Source-grounded question quality

StudyDD does not treat AI memory as current truth. Stable topics can use local state, but volatile topics such as cloud services, vendor certifications, pricing, preview features, and product names require fresh source metadata before authoritative questions. Source freshness is tracked in `sources/SOURCE_STATE.yaml`. When freshness is missing, stale, or unknown for a `moderate`, `volatile`, or `live` target, the next-activity router chooses a `recent_info_check` instead of an authoritative question; fresh source state suppresses repeated source-check recommendations. Due reviews still take priority.

### Learning activities and evidence intake

StudyDD is not only a question generator. It can recommend the best next learning activity: a question, review, paper exercise, external resource, lab, interview rehearsal, presentation rehearsal, voice note, diagram, or upload-and-review task. The learner stays in control, and readiness only changes when submitted evidence demonstrates competence.

### Learner adaptation with learner control

StudyDD adapts question style, review strategy, and study recommendations from evidence and learner feedback. It may suggest better approaches, but the learner can accept, modify, or override them. Overrides are recorded so the study state remains honest.

## The Promise

> Give this repo to a coding agent, tell it who you are and what you want to learn, and it turns the directory into your personal study library, tutor memory, readiness tracker, spaced-repetition queue, and next-action engine.

## Why This Exists

AI tutors and coding agents are useful study companions, but they often:

- forget what you already know
- inflate readiness after one easy answer
- lose track of weak areas
- grade against the answer they expected instead of what you actually said
- drift into generic encouragement instead of exam-style challenge
- make mistakes and never update the learning state

StudyDD fixes this by making learning state explicit, evidence-based, and auditable.

## The Happy Path

1. Initialize learner profile.
2. Add first target.
3. Build skill map from trusted sources.
4. Set conservative readiness.
5. Start one-question-at-a-time active tutoring.
6. Log answer and feedback.
7. Update readiness only with evidence.
8. Add weak items to spaced repetition.
9. Choose the next best study action.
10. Validate repo health.

There is no architecture menu in the core template. The default path is intentionally boring and powerful.

## Folder Model

- `state/` — current learner truth
- `targets/` — one folder per study, certification, interview, or skill target
- `reviews/` — spaced repetition queues
- `sessions/` — tutor session logs and update history
- `sources/` — trusted source tracking
- `activities/` — learning activity templates and append-only activity log
- `scripts/check_studydd.py` — repo sanity and educational-drift gate
- `scripts/agent_preflight.py` — quick agent orientation
- `scripts/agent_consistency_check.py` — cross-file state consistency
- `scripts/agent_evidence_check.py` — evidence reference sanity
- `NEXT_ACTIONS.md` — the single next best study action
- `AGENTS.md` — agent-operated learning loop contract
- `protocols/` — actionable operating rules for agents
- `PROMPTS/` — paste-ready prompts for coding agents
- `EXAMPLES/` — reference states only, not defaults

## Three Modes

StudyDD has three modes:

1. **Template mode** — maintain the reusable educational operating system in `StudyDD_Template`. Must stay generic and public-safe.
2. **Bootstrap mode** — the repo has left the template remote and Git history has been reset, but the learner profile and first target are not initialized yet.
3. **Learner instance mode** — the repo is a personal study brain with learner profile, targets, evidence, sessions, reviews, and next action.

Do not personalize the template repo. Personalization happens only after reinitializing a learner instance and moving it through bootstrap mode.

## How To Create A New StudyDD Learner Instance

Run these commands to cast the mold into a new learner repo:

```bash
# Clone and detach from the template history
git clone https://github.com/lennertvhoy/StudyDD_Template.git Study_Lenny
cd Study_Lenny
rm -rf .git
git init
git branch -M main
git remote add origin https://github.com/lennertvhoy/Study_Lenny.git

# Switch to bootstrap mode before running learner-instance validation
# Edit state/STUDYDD_MODE.yaml:
#   mode: bootstrap
#   template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
#   personalized: false
#   public_safe: false_or_review_required
python3 scripts/check_studydd.py

# Now initialize the learner profile and first target inside Study_Lenny.
# Only then switch state/STUDYDD_MODE.yaml to mode: learner_instance.

python3 scripts/check_studydd.py
git add .
git commit -m "chore: initialize StudyDD learner instance"
git push -u origin main
```

Replace `Study_Lenny` and the remote URL with your own learner/project name.

**Warning:** Do not personalize the template repo. The commands above remove the template Git history and reinitialize Git so the new directory becomes a separate learner instance.

**Warning:** Do not run learner-instance validation until the learner profile and first target are initialized. Switch `state/STUDYDD_MODE.yaml` to `mode: learner_instance` only after that initialization is complete.

## After Creating An Instance

1. Open the new learner folder in your coding agent.
2. Paste `PROMPTS/coding_agent_start_prompt.md` into the agent chat.
3. Tell the agent what you want to learn.

Example:

> Initialize this StudyDD instance for me. I want to prepare for a certification exam. Ask me only the essential setup questions first.

The agent will read `AGENTS.md`, inspect the current state, initialize the learner profile and first target, build a conservative skill map from trusted sources, and set the first next action.

## Template Maintenance

If you are editing `StudyDD_Template` itself, you are maintaining the mold. Keep the repo generic and public-safe. Do not seed learner state, active targets, or private data.

## What The Agent Maintains

- `state/STUDY_STATUS.md` — short human-readable snapshot
- `state/STUDY_STATE.yaml` — structured current truth
- `state/SKILL_MAP.yaml` — skills with readiness and confidence
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/STUDY_BACKLOG.md` — strategic backlog
- `targets/` — target-specific files
- `reviews/REVIEW_QUEUE.md` — spaced repetition queue
- `sessions/SESSION_LOG.md` — session history
- `sources/SOURCE_INDEX.md` — trusted source registry
- `state/ACTIVITY_STATE.yaml` — active and recent learning activities
- `activities/ACTIVITY_LOG.md` — append-only activity audit trail
- `NEXT_ACTIONS.md` — immediate next step

You can inspect or override any of these files. They are plain Markdown and YAML.

## Quick setup

StudyDD runs on Linux, macOS, and Windows PowerShell with Python 3.10+. It does
not install dependencies without your explicit consent.

```bash
# 1. Check your environment
python scripts/check_environment.py

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Review what would be installed, then install with consent
python scripts/setup_studydd.py --check
python scripts/setup_studydd.py --install

# 4. Run validation and the demo replay
python scripts/check_studydd.py
python scripts/run_demo_replay.py
```

See [`docs/setup.md`](docs/setup.md) for the full setup guide and troubleshooting.

## Validation

Run the sanity gate after setup or state changes:

```bash
python3 scripts/check_studydd.py
```

The validator checks required files, parses YAML when PyYAML is available, and verifies the happy-path folder structure.

## Source And Readiness Discipline

Readiness is earned through demonstrated answers, not through source coverage or encouragement.

- A new skill starts as `pending`.
- One good answer can make a skill `practiced`, not `confirmed`.
- Weak and repaired answers go into `reviews/REVIEW_QUEUE.md`.
- Confirmed status requires strong or varied evidence.
- Official and authoritative sources come first. Old spreadsheets, exports, notes, blogs, and generated summaries are secondary until verified.

## Examples

- `EXAMPLES/ai-103-example/` — reference certification study state.
- `EXAMPLES/product-engineer-interview-example/` — reference interview prep state.

Examples show how maintained state can look after sessions. They are not the root template's default learner or target.

## Create A Learner Instance With The Script

From the template repo:

```bash
python3 scripts/create_instance.py \
  --target ../Study_MyTarget \
  --remote https://github.com/example/Study_MyTarget.git
```

Then open the new instance in your coding agent and paste the contents of
`PROMPTS/coding_agent_start_prompt.md`.

The script leaves the instance in `bootstrap` mode, detaches it from the
`StudyDD_Template` Git history, records the template origin in
`state/STUDYDD_TEMPLATE_VERSION.yaml`, and runs the validator before handing
off.

## Maintaining Learner Instances After Template Updates

When the public template improves, apply generic upgrades safely:

1. Read `protocols/UPGRADE_INSTANCE_FROM_TEMPLATE.md`.
2. Paste `PROMPTS/upgrade_instance_from_template.md` into the agent.
3. Never overwrite learner state files automatically.

## Public/Private Safety

- The `StudyDD_Template` repo itself must stay generic and public-safe.
- Learner instances may contain private data; run `scripts/agent_privacy_check.py`
  before pushing a learner instance to a public or shared remote.
- Never push a learner instance publicly without the learner's explicit consent.

## Validation And CI

Local checks:

```bash
python3 scripts/check_studydd.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_create_instance.py
python3 scripts/test_compact_state.py
python3 scripts/test_context_pack.py
python3 scripts/test_study_skills.py
python3 scripts/test_performance_policy.py
python3 scripts/test_validate_touched_state.py
python3 scripts/test_learning_activities.py
python3 scripts/test_next_activity_decision.py
python3 scripts/test_source_freshness.py
```

GitHub Actions runs the validator, instantiation smoke test, study-loop smoke
test, and `git diff --check` on every push and pull request. See
`.github/workflows/validate.yml`.

### Intelligent state loading

StudyDD keeps long audit logs, but agents do not load everything by default. Before a session, the repo builds a compact context pack from canonical state, indexes, summaries, due reviews, relevant evidence, and the next activity recommendation with its auditable `Rule: ...` reason. Raw logs stay available for audit and repair.

See `protocols/STATE_LOADING_POLICY.md`, `scripts/compact_state.py`, and `scripts/build_context_pack.py`.

### Fast path state updates

StudyDD keeps a full audit trail, but ordinary tutoring turns use a fast path. The agent loads the current context pack, touches only the relevant skill/evidence/review records, and runs targeted validation. Full compaction and full validation happen at session boundaries, CI, audit, or repair.

See `protocols/PERFORMANCE_POLICY.md`, `protocols/STATE_WRITE_POLICY.md`, `scripts/validate_touched_state.py`, and `scripts/plan_state_update.py`.

### Study skills

StudyDD uses `study_skills/<id>/SKILL.md` files to adapt tutoring to the target. IT certifications, philosophy, primary maths, language learning, interview prep, and practical labs need different question styles, grading rules, evidence standards, and review strategies.

A target declares its study skill in `TARGET.yaml`:

```yaml
study_skill: it_certification
```

See `study_skills/README.md`.

### Spaced repetition by default

StudyDD treats due review as learning debt. At the start of a session, the agent
checks the current time and recommends due or overdue review before new
material. The learner can override, but the override is recorded so the study
state remains honest.

See `protocols/SPACED_REPETITION_POLICY.md`, `scripts/schedule_review.py`, and
`scripts/select_next_study_action.py`.

### How the agent chooses the next activity

StudyDD recommends one activity at a time using protocol-driven rules:

1. **Due reviews first** — spaced retrieval is the highest-retention move.
2. **Recent-info check** — for `moderate`, `volatile`, or `live` topics whose `sources/SOURCE_STATE.yaml` freshness is missing, stale, or unknown.
3. **Lab or diagram** — when the study skill is hands-on (`practical_lab`, `cloud`, `sysadmin`, `networking`) or conceptual (`philosophy`, `conceptual_understanding`).
4. **Exam-style question** — when the target is a certification or exam and the skill is practiced.
5. **Fallback question** — a focused retrieval question, paper exercise, or explain-back.

The same shared decision logic powers `scripts/plan_learning_activity.py` and the context pack, so the tutor sees the same activity type, expected evidence, and `Rule: ...` reason. The learner can accept, modify, or override it.

## Five-minute demo

Run the public demo replay to see the full StudyDD learning loop in under a
minute:

```bash
python3 scripts/run_demo_replay.py
```

The replay creates a temporary learner instance, asks one fake question, grades
the answer honestly, writes evidence, schedules a review, demonstrates
review-first selection, records an override, and validates the result.

For a walkthrough meant for students, teachers, and LinkedIn viewers, see
`docs/demo-walkthrough.md`. The final demo state is also available as a static
fixture in `EXAMPLES/demo_ai_search_exam/`.

## Future Add-Ons

These are intentionally backlog items, not part of the core slice:

- `addon-telegram-study-bot` — daily review prompt, answer capture, reminders, low-energy study mode.
- `addon-containerized-studydd` — Docker, Podman, devcontainer, or compose setup for portable local execution.

## License

This project is licensed under the MIT License. See `LICENSE.md` for the full text.

## Status

v0.10.0 — cross-platform setup and dependency consent (`requirements.txt`, `docs/setup.md`, `scripts/check_environment.py`, `scripts/setup_studydd.py`, `scripts/test_cross_platform_paths.py`, `.github/workflows/validate.yml` matrix) layered on top of the learning activity orchestrator.
