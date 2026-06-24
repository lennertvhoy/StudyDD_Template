# StudyDD Source-Grounded Question Quality v1 — Design Spec

**Date:** 2026-06-24  
**Repo:** `/home/ff/Documents/Projects/StudyDD` (StudyDD_Template)  
**Status:** Approved, ready for implementation planning  
**Related prompt:** "Add a source freshness, question-quality, and learner-adaptation layer."

## Core doctrine

> Stable knowledge can be taught from local state. Volatile knowledge must be source-grounded. Expensive lookup should be deliberate, cached, and justified.
>
> The agent may be clever, but it must not pretend stale memory is current truth.

## Goals

1. Prevent authoritative questions on volatile topics (Azure services, cloud security, certification objectives, pricing, preview features, portal locations, product names) from being generated from AI memory.
2. Make source freshness explicit, machine-readable, and validated.
3. Keep question quality high by tying volatility, source IDs, question mode, and answer-key grounding to the question record.
4. Adapt study style to the learner from evidence and feedback, while leaving the learner in control.
5. Stay file-native, repo-native, and coding-agent-friendly. No UI, no web app, no database, no MCP, no Telegram.
6. Keep the template generic and public-safe. Do not seed real learner data.

## Non-goals

- Do not perform automatic web search for every question.
- Do not build a model-routing gateway or API abstraction.
- Do not add runtime AI model efficiency routing in this slice (document future direction only).
- Do not personalize learner state in the template.

## Approved approach

**Approach 1 — Extend the existing question bank and ship one coherent layer.**

- Extend `docs/question-bank-schema.md` with volatility, source IDs, question mode, source-grounded answer key, and a validated quality gate.
- Add five new policy files, two new state files, and three new scripts.
- Wire the new files into `check_studydd.py`, `build_context_pack.py`, `run_demo_replay.py`, the demo tests, the agent start prompt, `AGENTS.md`, the demo fixture, and CI.

## Architecture overview

```text
┌─────────────────────────────────────────────────────────────┐
│  Policy layer                                                │
│  SOURCE_FRESHNESS_POLICY.md                                  │
│  SOURCE_REFRESH_POLICY.md                                    │
│  QUESTION_QUALITY_GOVERNOR.md                                │
│  LEARNER_ADAPTATION_POLICY.md                                │
│  LEARNER_FEEDBACK_POLICY.md                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  State layer                                                 │
│  sources/SOURCE_STATE.yaml      (canonical freshness truth)  │
│  state/LEARNER_PROFILE.yaml     (generic template placeholder)│
│  docs/question-bank-schema.md  (extended with quality fields)│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Tool layer                                                  │
│  scripts/check_source_freshness.py                           │
│  scripts/lint_questions.py                                   │
│  scripts/suggest_study_adjustment.py                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Integration layer                                           │
│  scripts/check_studydd.py                                    │
│  scripts/build_context_pack.py                               │
│  scripts/run_demo_replay.py + test_demo_replay.py            │
│  AGENTS.md                                                   │
│  PROMPTS/coding_agent_start_prompt.md                        │
│  README.md                                                   │
│  .github/workflows/validate.yml                              │
└─────────────────────────────────────────────────────────────┘
```

## 1. Source freshness layer

### 1.1 Volatility classes

Defined in `protocols/SOURCE_FRESHNESS_POLICY.md`:

```yaml
volatility_classes:
  stable:
    examples:
      - basic arithmetic
      - classical logic forms
      - long-established historical facts
      - basic grammar patterns
    default_max_age_days: 3650
    source_required_for_new_questions: false

  slow_changing:
    examples:
      - general networking fundamentals
      - basic programming concepts
      - established philosophical arguments
      - standard mathematical techniques
    default_max_age_days: 730
    source_required_for_new_questions: false

  moderate:
    examples:
      - certification objectives
      - school curriculum standards
      - cloud architecture best practices
      - software library behavior
    default_max_age_days: 90
    source_required_for_new_questions: true

  volatile:
    examples:
      - Microsoft Azure services
      - cloud security products
      - vendor certification exam objectives
      - pricing
      - preview features
      - portal UI locations
      - product names
      - compliance features
    default_max_age_days: 30
    source_required_for_new_questions: true

  live:
    examples:
      - current outages
      - current prices
      - current exam retirement dates
      - current product availability
      - breaking changes
    default_max_age_days: 1
    source_required_for_new_questions: true
```

### 1.2 Target volatility declaration

Targets declare volatility in `TARGET.yaml`. Example update to `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml`:

```yaml
volatility: volatile
```

If a target does not declare volatility, the freshness gate defaults to `moderate` and emits a warning.

### 1.3 `sources/SOURCE_STATE.yaml`

Machine-readable canonical source registry. Example demo fixture:

```yaml
sources:
  - id: mslearn_ai_search_overview
    title: "Azure AI Search overview"
    url: "https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search"
    authority: official
    target_ids:
      - demo-ai-search-exam
    volatility: volatile
    last_checked_at: "2026-06-24T12:00:00+00:00"
    expires_at: "2026-07-24T12:00:00+00:00"
    checked_by: "demo_replay"
    notes: "Demo fixture. Timestamp is deterministic test metadata, not a live source refresh."
    usable_for_questions: true
```

Authority values: `official`, `high_authority`, `instructor`, `textbook`, `learner_notes`, `unverified`.

Freshness statuses (computed, not trusted from question files): `fresh`, `stale`, `expired`, `missing_timestamp`, `unverified`.

### 1.4 `scripts/check_source_freshness.py`

CLI:

```bash
python3 scripts/check_source_freshness.py
python3 scripts/check_source_freshness.py --target-id <target_id>
python3 scripts/check_source_freshness.py --question-id <question_id>
python3 scripts/check_source_freshness.py --allow-stale
python3 scripts/check_source_freshness.py --now "2026-06-24T12:00:00+00:00"
```

Behavior:

- Reads `sources/SOURCE_STATE.yaml`.
- Reads target volatility from `targets/<id>/TARGET.yaml` or accepts a default.
- Computes freshness:
  - If `expires_at` exists, compare `now <= expires_at`.
  - Else if `last_checked_at` exists, compute expiry from volatility class.
  - Else mark `missing_timestamp` / `unverified`.
- `usable_for_questions: false` makes a source unusable regardless of timestamp.
- Prints fresh/stale/missing/unverified sources per target.
- Recommends refresh or stable-review fallback.
- Exits non-zero if a volatile/live target lacks fresh usable sources, unless `--allow-stale`.
- With `--allow-stale`, prints:
  ```text
  Stale source allowed by override.
  Question mode: practice-only, not authoritative-current.
  ```
- Does **not** perform web search.

### 1.5 `protocols/SOURCE_REFRESH_POLICY.md`

Rules:

- Refresh only when the freshness gate says it is needed.
- Prefer official/high-authority sources.
- Refresh the smallest source set needed for the current question/task.
- Cache metadata back to `sources/SOURCE_STATE.yaml`.
- Record checked source, timestamp, authority, volatility class, usability, and reason.
- Do not refresh stable topics unnecessarily.
- Learner may say:
  - "refresh sources now"
  - "use stale source for practice only"
  - "avoid web search"
  - "official sources only"

## 2. Question quality layer

### 2.1 Extended question-bank schema

`docs/question-bank-schema.md` keeps backward compatibility and adds optional recommended fields:

```yaml
id: "<question_id>"
target_id: "<target_id>"
skill_id: "<skill_id>"
cognitive_level: "recall | apply | troubleshoot | choose-best | explain | design"
difficulty: 1-5
source_ref: "<source_id or URL>"          # legacy, still accepted
source_ids:                                 # preferred for moderate+
  - mslearn_ai_search_overview
volatility: stable | slow_changing | moderate | volatile | live
source_freshness_status: fresh | stale | not_required | unverified   # cached hint; linter recomputes from SOURCE_STATE.yaml
question_mode: authoritative_current | conceptual_practice | stale_practice | exam_sim | remediation
public_prompt: |
  The learner-facing question text.
private_answer_key:
  correct_answer: "..."
  rationale: "..."
  source_support:
    - source_id: mslearn_ai_search_overview
      checked_at: "2026-06-24T12:00:00+00:00"
      section: "Overview"
rubric:
  - "Required point 1"
common_traps:
  - "Common distractor 1"
transfer_probe: |
  Optional follow-up scenario.
last_used: "YYYY-MM-DD"
cooldown_days: 7
question_quality:
  cognitive_level: recall | understand | apply | analyze | evaluate | create
  question_type: scenario | calculation | interpretation | troubleshooting | explanation | production
  answer_key_visibility: private_until_grading
  distractor_quality: plausible
  learner_fit: appropriate
  estimated_difficulty: easy | medium | hard
  generated_from_memory_allowed: true | false   # derived/validated, not trusted
  quality_gate: pass | warn | fail
  quality_gate_reason: ""
  notes: ""
```

### 2.2 Question modes

- `authoritative_current`: requires fresh usable sources for moderate/volatile/live topics.
- `conceptual_practice`: can use stable local knowledge if not product-current.
- `stale_practice`: allowed only with explicit override and must be labelled.
- `exam_sim`: must follow source/objective freshness rules.
- `remediation`: can focus on previous mistakes, but current volatile claims still need freshness.

### 2.3 `protocols/QUESTION_QUALITY_GOVERNOR.md`

Rules:

- No authoritative volatile/live question passes quality gate without a fresh source.
- Answer key never appears in learner-facing text.
- Scenario questions test reasoning, not keyword matching.
- Distractors plausible but not nonsense.
- Question must match active study skill and learner level.
- If uncertain, the agent asks a simpler source-grounded question or triggers source refresh.
- Learner-facing honesty:
  - "This question is based on a fresh official source."
  - "This is conceptual practice only; I have not refreshed current vendor details."

### 2.4 `scripts/lint_questions.py`

Validates question files and active/pending question records. Checks:

- Missing skill ID or target ID.
- Missing `source_ids` for moderate/volatile/live topics.
- Stale source used for volatile/live authoritative question (recomputed from `SOURCE_STATE.yaml`).
- Answer-key leakage patterns in `public_prompt`.
- Correct answer always in same visible option position (heuristic).
- Implausible distractors marker missing.
- Too many recall-only questions for a skill that needs application.
- No transfer probe before readiness upgrade.
- `generated_from_memory_allowed` derived from volatility, sources, freshness, mode, authority.
- `quality_gate: fail` for volatile/live `authoritative_current` with stale/missing sources.
- `quality_gate_reason` required when gate is `warn` or `fail`.
- Legacy `source_ref` triggers a warning for moderate+/volatile topics:
  ```text
  Question Q-... uses legacy source_ref only. Volatile/current questions should use source_ids tied to SOURCE_STATE.yaml.
  ```

Template mode: validate demo/example question banks and schema, but do not fail because there is no real learner question bank.

### 2.5 Source truth discipline

- `sources/SOURCE_STATE.yaml` is the canonical freshness registry.
- Question files may cache `source_freshness_status`, but the linter/validator recomputes it.
- The freshness script computes `fresh | stale | expired | missing_timestamp | unverified` from source metadata. The question record's cached status uses `fresh | stale | not_required | unverified`, where `expired` and `missing_timestamp` map to `stale` or `unverified`.
- Question files may declare `generated_from_memory_allowed`, but the validator derives the real permission.

## 3. Learner adaptation layer

### 3.1 Doctrine

> StudyDD should adapt to the learner, but not manipulate the learner.
>
> Preference informs the route. Evidence determines readiness. Target requirements constrain both.

### 3.2 `state/LEARNER_PROFILE.yaml`

Template mode keeps this generic/empty:

```yaml
learner_preferences:
  explanation_style: ""
  question_style_preference: ""
  desired_difficulty: ""
  feedback_style: ""
  session_length_preference_minutes: null
  low_energy_mode_preference: ""
  source_refresh_preference: "ask_when_needed"

adaptation_state:
  methods_tried: []
  methods_that_helped: []
  methods_that_failed: []
  recurring_friction: []
  last_feedback_prompt_at: ""
  feedback_prompt_cooldown_days: 7

control:
  learner_overrides: []
  agent_recommendations_declined: []
```

### 3.3 `protocols/LEARNER_ADAPTATION_POLICY.md`

- Agent occasionally asks for feedback, not every turn.
- Feedback should be short and useful.
- Track preferences separately from evidence of mastery.
- Distinguish learner preference, demonstrated effectiveness, temporary energy state, and target requirements.
- Agent may recommend a different approach if evidence shows the current one is weak.
- Never flatter readiness to match preference.
- Learner can override study method; record the override.
- Recommendation strength: `weak | moderate | strong`.
- Every study adjustment ends with: "You can accept, modify, or override this."

### 3.4 `protocols/LEARNER_FEEDBACK_POLICY.md`

Ask feedback after:

- several sessions
- repeated misses
- repeated overrides
- low engagement
- target milestones

Not during every ordinary question. Example prompts provided in the policy.

### 3.5 `scripts/suggest_study_adjustment.py`

Inspects:

- recent mistakes
- review misses
- overrides
- confidence calibration
- learner preferences
- target deadline
- study skill

Outputs at most one recommendation. If evidence is insufficient, prints:

```text
StudyDD suggestion:
No recommendation: insufficient evidence.
```

Supports `--demo` for deterministic demo output.

Example strong recommendation:

```text
StudyDD suggestion:

You keep missing service-boundary questions. Recommended adjustment:
Do two short comparison drills before adding new material.

Why:
The last three weak evidence items involve choosing between similar services.

Learner control:
You can accept, modify, or override this.
```

### 3.6 Study skill integration

Update each `study_skills/<id>/SKILL.md` to optionally declare:

- `preferred_question_types`
- `freshness_requirements`
- `adaptation_signals`
- `feedback_style`
- `source_requirements`

The generic skill includes a short note pointing to freshness/adaptation policies.

## 4. Integration points

### 4.1 `scripts/check_studydd.py`

- Validate `sources/SOURCE_STATE.yaml` exists and is structurally correct.
- Validate `state/LEARNER_PROFILE.yaml` exists and is generic in template mode.
- Ensure required protocols exist.
- In learner-instance mode, ensure volatile/live targets have at least one fresh usable official/high-authority source before authoritative question generation.
- Validate question quality records against `SOURCE_STATE.yaml` (recompute freshness, check source IDs exist, block `authoritative_current` volatile/live questions with stale/missing sources).
- Check learner overrides are recorded when bypassing strong recommendations.

### 4.2 `scripts/build_context_pack.py`

Include in the context pack:

- source freshness status for active target
- active target volatility class
- learner source-refresh preference
- learner adaptation summary (one current recommendation if present)
- question quality requirements for active task

Stay performance-aware: no full source logs, no full learner history.

### 4.3 Demo replay

Update `scripts/run_demo_replay.py` and the demo fixture `EXAMPLES/demo_ai_search_exam/`:

- Create `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml` with a fresh demo official source for `demo-ai-search-exam`.
- Show cached source freshness message:
  ```text
  StudyDD checks source freshness before generating product-current questions.
  The demo uses a demo official source marked fresh.
  The agent does not search the web because the cached source is fresh enough.
  If the source were stale, StudyDD would ask to refresh or choose a stable review instead.
  ```
- Show learner-adaptation moment:
  ```text
  StudyDD suggestion:
  You missed a scenario tradeoff. Next time, use a short comparison drill.
  Learner control:
  You can accept, modify, or override this.
  ```
- Update `scripts/test_demo_replay.py` to assert these messages appear.

### 4.4 `AGENTS.md`

- Add to Core Rules: "Do not generate authoritative questions on volatile topics from memory. Run the freshness gate or use cached fresh source metadata."
- Add the five new protocols to Required First Actions.
- Add freshness check to session flow before generating volatile questions.

### 4.5 `PROMPTS/coding_agent_start_prompt.md`

Add under "During Study Sessions":

```text
- Before generating or grading authoritative questions on moderate, volatile, or live topics, run `scripts/check_source_freshness.py` for the active target. Do not invent current product, pricing, portal, or exam details from memory.
```

### 4.6 `README.md`

Add two concise sections as specified in the prompt.

### 4.7 `docs/future-model-efficiency.md`

Future-facing note only. No runtime routing. States:

> StudyDD should become cheaper over time by making easy tasks explicit, deterministic, and tool-like. The strongest model should only be needed at the moments where teaching judgment actually matters.

Include the `task_complexity` taxonomy from the approved refinement as a future architecture direction.

## 5. File map

### New files

- `protocols/SOURCE_FRESHNESS_POLICY.md`
- `protocols/SOURCE_REFRESH_POLICY.md`
- `protocols/QUESTION_QUALITY_GOVERNOR.md`
- `protocols/LEARNER_ADAPTATION_POLICY.md`
- `protocols/LEARNER_FEEDBACK_POLICY.md`
- `sources/SOURCE_STATE.yaml`
- `state/LEARNER_PROFILE.yaml`
- `scripts/check_source_freshness.py`
- `scripts/lint_questions.py`
- `scripts/suggest_study_adjustment.py`
- `scripts/test_source_freshness.py`
- `scripts/test_question_quality.py`
- `scripts/test_learner_adaptation.py`
- `docs/future-model-efficiency.md`
- `Evidence/005-2026-06-24-studydd-source-grounded-question-quality/`

### Modified files

- `docs/question-bank-schema.md`
- `scripts/check_studydd.py`
- `scripts/build_context_pack.py`
- `scripts/run_demo_replay.py`
- `scripts/test_demo_replay.py`
- `AGENTS.md`
- `PROMPTS/coding_agent_start_prompt.md`
- `README.md`
- `.github/workflows/validate.yml`
- `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml`
- `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml` (new in fixture)
- `study_skills/generic/SKILL.md` and other skill files (optional declarations)

## 6. Testing plan

### New tests

- `scripts/test_source_freshness.py`:
  - volatile target with fresh official source passes
  - volatile target with stale source fails/warns as designed
  - stable target does not require source refresh
  - `check_source_freshness.py` does not perform web search
  - `--allow-stale` switches to practice-only mode
  - `--now` produces deterministic output

- `scripts/test_question_quality.py`:
  - question quality record fails when volatile topic has no source
  - answer-key leakage is caught
  - legacy `source_ref` triggers warning for volatile topic
  - `authoritative_current` with stale source fails quality gate
  - `quality_gate_reason` required for warn/fail

- `scripts/test_learner_adaptation.py`:
  - learner profile remains generic in template mode
  - adaptation suggestion is evidence-based and non-spammy
  - `--demo` produces deterministic output
  - insufficient evidence yields "No recommendation"

### Existing tests

Run all existing tests. None should break. If an earlier-slice test does not exist, report that clearly.

### Validation commands

```bash
pwd
git rev-parse --show-toplevel
git remote -v
cat state/STUDYDD_MODE.yaml
cat state/STUDYDD_TEMPLATE_VERSION.yaml
python3 scripts/check_studydd.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_create_instance.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_demo_replay.py
python3 scripts/test_compact_state.py || true
python3 scripts/test_context_pack.py || true
python3 scripts/test_performance_policy.py || true
python3 scripts/test_validate_touched_state.py || true
python3 scripts/test_source_freshness.py
python3 scripts/test_question_quality.py
python3 scripts/test_learner_adaptation.py
python3 scripts/check_source_freshness.py --target-id demo-ai-search-exam --now "2026-06-24T12:00:00+00:00"
python3 scripts/lint_questions.py
python3 scripts/suggest_study_adjustment.py --demo
python3 scripts/run_demo_replay.py
git diff --check
git status --short
```

## 7. CI plan

Update `.github/workflows/validate.yml` to add:

```yaml
- run: python3 scripts/test_source_freshness.py
- run: python3 scripts/test_question_quality.py
- run: python3 scripts/test_learner_adaptation.py
- run: python3 scripts/check_source_freshness.py --target-id demo-ai-search-exam --now "2026-06-24T12:00:00+00:00"
- run: python3 scripts/lint_questions.py
- run: python3 scripts/suggest_study_adjustment.py --demo
```

Use fixed `--now` so CI does not fail when demo timestamps age.

## 8. Evidence plan

Create `Evidence/005-2026-06-24-studydd-source-grounded-question-quality/` with up to 12 files:

1. `01-repo-check.md` — repo path, remote, mode, version
2. `02-validator-pass.txt` — `python3 scripts/check_studydd.py` output
3. `03-source-freshness-fresh.txt` — fresh check for demo target
4. `04-source-freshness-stale.txt` — negative proof: stale volatile source blocked
5. `05-question-quality-lint.txt` — `lint_questions.py` output
6. `06-question-quality-negative.txt` — negative proof: volatile authoritative question with missing source fails
7. `07-learner-adaptation.txt` — `suggest_study_adjustment.py --demo` output
8. `08-demo-replay.txt` — demo replay showing cached freshness and learner control
9. `09-ci-workflow.md` — `.github/workflows/validate.yml` update
10. `10-final-git-status.txt` — `git status --short` and `git log --oneline -1`
11. `11-pushed-commit.md` — pushed status and commit hash
12. `12-summary.md` — what changed and how the guardrails work

## 9. Future work

- Model efficiency routing (`docs/future-model-efficiency.md`) is documented but not implemented.
- Study skills may declare more granular source/freshness requirements over time.
- The source refresh protocol may later integrate a deliberate web-search tool call, but only when the freshness gate explicitly requests it.
- Learning Activity + Evidence Intake Orchestrator (see Section 11) is the next major product direction.
- Cross-platform setup and dependency consent: track as a platform-hardening concern. Add `requirements.txt`, `scripts/setup_studydd.py`, `docs/setup.md`, and CI coverage for Ubuntu/Windows/macOS. Never install dependencies without explicit consent.

## 10. Open questions / none

All design questions resolved during brainstorming. No open questions remain.

## 11. Next product direction: Learning Activity + Evidence Intake Orchestrator v1

> Questions are one teaching move, not the whole system.
>
> StudyDD should recommend the best next learning activity, explain why, let the learner override, and record evidence from the result.

### 11.1 Core doctrine

StudyDD should not become only an AI question generator. Good teaching is flexible. Depending on the learner, target, energy level, evidence, and deadline, the best next move might be a question, a worked example, a paper exercise, a video, a reading task, a lab, an external platform exercise, a whiteboard drawing, or an upload-and-review task.

The tutor should not ask, "What question do I generate?" It should ask, "What learning activity gives this student the best chance of improving now, and what evidence will prove it worked?"

### 11.2 Activity types

```yaml
activity_types:
  retrieval_question:
    description: "One direct question or exam-style scenario."

  spaced_review:
    description: "Due or overdue review based on time-aware spaced repetition."

  worked_example:
    description: "The learner is missing a process or mental model."

  paper_exercise:
    description: "Learner solves work on paper, then uploads a photo or types the result."

  external_platform_exercise:
    description: "Learner completes exercises on another platform and uploads score/screenshot/notes."

  video_or_reading_task:
    description: "Learner watches, reads, or studies a selected resource, then submits a short summary or answers a check question."

  practical_lab:
    description: "Learner performs a technical task, command, configuration, troubleshooting step, or build."

  explain_back:
    description: "Learner explains the idea back in their own words."

  diagram_or_whiteboard:
    description: "Learner draws a model, flow, topology, argument map, architecture, or solution."

  interview_prep:
    description: "Learner answers realistic interview questions, STAR stories, technical explanations, follow-ups, or role-fit prompts."

  presentation_prep:
    description: "Learner rehearses a presentation, pitch, class explanation, demo talk, or oral exam answer."

  voice_note_review:
    description: "Learner uploads or records a voice note; StudyDD reviews structure, clarity, correctness, confidence, pacing, filler words, and target fit."

  writing_or_essay_review:
    description: "Learner submits a written answer, essay, cover letter, reflection, or explanation for feedback."

  upload_and_review:
    description: "Generic evidence intake for screenshots, PDFs, photos, notes, logs, transcripts, or external work."
```

### 11.3 New files to create later

```text
protocols/LEARNING_ACTIVITY_POLICY.md
protocols/EVIDENCE_INTAKE_POLICY.md
protocols/VOICE_NOTE_REVIEW_POLICY.md
protocols/INTERVIEW_PREP_POLICY.md
protocols/PRESENTATION_PREP_POLICY.md
protocols/EXTERNAL_RESOURCE_POLICY.md
state/ACTIVITY_STATE.yaml
activities/ACTIVITY_LOG.md
activities/ACTIVITY_TEMPLATES.yaml
scripts/plan_learning_activity.py
scripts/record_activity_result.py
scripts/analyze_voice_note.py
scripts/analyze_presentation_rehearsal.py
scripts/test_learning_activities.py
```

### 11.4 Key policies

**`protocols/LEARNING_ACTIVITY_POLICY.md`**

- Choose the next activity based on due reviews, weak skills, learner energy, preference, target requirements, study skill, source freshness, recent mistakes, and deadline pressure.
- A question is not always the best next action.
- Explain why the activity is recommended.
- Learner can accept, modify, or override.
- Every activity must produce evidence.
- No readiness upgrade without evidence.
- External resources must respect source freshness and quality rules.

**`protocols/EVIDENCE_INTAKE_POLICY.md`**

- Accept typed answers, voice notes, transcripts, screenshots, photos, PDFs, external scores, command output, lab logs, presentation outlines.
- Grade evidence according to the active study skill.
- Distinguish completed activity, correct understanding, effort, and mastery evidence.
- Effort can be acknowledged; readiness only changes from demonstrated competence.
- If evidence is unclear, ask one focused clarification or mark as insufficient evidence.

**`protocols/EXTERNAL_RESOURCE_POLICY.md`**

- Recommend external resources only when they are better than an AI-generated explanation or exercise.
- Prefer official/high-authority sources for volatile domains.
- State why a resource is recommended (better visualization, worked examples, official explanation, practice density, different teaching style).
- Recommend one good resource, not a dump of links.
- Run freshness policy first if the source is volatile/current.

### 11.5 State and templates

**`state/ACTIVITY_STATE.yaml`** shape:

```yaml
active_activity:
  id:
  type:
  target_id:
  skill_id:
  assigned_at:
  due_at:
  status:
  reason:
  expected_evidence:
  learner_override_allowed: true

recent_activities: []

activity_preferences:
  learner_likes: []
  learner_dislikes: []
  effective_methods: []
  ineffective_methods: []
```

**`activities/ACTIVITY_TEMPLATES.yaml`** examples:

```yaml
templates:
  - id: paper_drill_basic
    activity_type: paper_exercise
    best_for:
      - primary_math
      - calculation
    expected_evidence:
      - photo
      - answer_sheet

  - id: official_doc_reading
    activity_type: video_or_reading_task
    best_for:
      - it_certification
      - volatile_topic
    expected_evidence:
      - short_summary
      - answer_to_check_question

  - id: lab_screenshot_review
    activity_type: practical_lab
    best_for:
      - sysadmin
      - cloud
      - networking
    expected_evidence:
      - screenshot
      - command_output
      - explanation

  - id: explain_back
    activity_type: explain_back
    best_for:
      - philosophy
      - conceptual_understanding
      - interview_prep
    expected_evidence:
      - written_explanation
      - transcript
```

### 11.6 Activity result evidence model

```yaml
activity_result:
  activity_id:
  evidence_id:
  submitted_as:
    - typed_answer
    - voice_note
    - transcript
    - screenshot
    - photo
    - pdf
    - external_score
    - command_output
    - lab_log
    - presentation_outline
  result:
    - correct
    - partial
    - incorrect
    - insufficient_evidence
  confidence:
  mistake_tags: []
  strengths: []
  next_recommendation:
  readiness_change:
  review_scheduled:
```

### 11.7 Agent tool-building rule

If a recurring learning activity creates evidence that is hard to inspect manually, the agent may build a small deterministic helper script to process it, as long as the script is local, transparent, validated, and does not replace teacher judgment.

Examples:

```yaml
helper_scripts:
  voice_note:
    possible_tools:
      - transcribe audio if a local/available transcription tool exists
      - analyze duration
      - detect long pauses if feasible
      - count filler words from transcript
      - extract structure markers
      - compare against rubric
    never_claim:
      - "perfect emotional analysis"
      - "objective charisma score"
      - "medical or psychological diagnosis"

  presentation_prep:
    possible_tools:
      - parse transcript
      - check opening/structure/closing
      - count jargon
      - identify unsupported claims
      - check timing against target duration
      - compare against slide outline if available

  interview_prep:
    possible_tools:
      - extract STAR structure
      - detect vague claims
      - check for concrete evidence
      - flag overclaims
      - classify answer length
      - generate focused follow-up question

  paper_math:
    possible_tools:
      - accept manually entered answers
      - compare against generated answer key
      - track mistake tags
      - request photo upload when needed
    limitation:
      - OCR/photo grading is optional and should be treated as uncertain unless verified.

  technical_lab:
    possible_tools:
      - parse command output
      - check config snippets
      - compare expected vs actual output
      - extract error messages
      - build a troubleshooting checklist
```

### 11.8 Interview prep support

Track:

```yaml
interview_prep_state:
  target_role:
  company:
  story_bank:
    - id:
      theme:
      evidence:
      weakness:
      last_practiced:
  weak_answer_patterns:
    - too_vague
    - too_long
    - no_concrete_example
    - overclaiming
    - missing_business_impact
    - weak_closing
  practice_modes:
    - behavioral
    - technical
    - role_fit
    - pressure_followup
    - salary_negotiation
```

Agent behavior:

- Ask realistic questions.
- Push for concrete examples.
- Grade clarity, relevance, evidence, concision, and role fit.
- Ask follow-up questions.
- Suggest better answer structure.
- Record improved answer versions.
- Let learner override tone/style.

### 11.9 Presentation prep support

Track:

```yaml
presentation_prep_state:
  presentation_goal:
  audience:
  target_duration_minutes:
  outline:
  rehearsal_history:
  weak_patterns:
    - unclear_opening
    - too_much_jargon
    - weak_transition
    - unsupported_claim
    - rushed_ending
    - low_energy_delivery
```

Agent behavior:

- Help structure the talk.
- Review outline, slides, transcript, or voice note.
- Give timing and clarity feedback.
- Suggest one improvement at a time.
- Encourage rehearsal.
- Track evidence from repeated attempts.
- Avoid vague motivational feedback.

### 11.10 Learner control

Every recommendation ends with:

```text
StudyDD recommendation: <activity>.

Reason: <why this is the highest-value learning move right now>.

You can accept, modify, or override this.
```

If the learner overrides a strong recommendation, record:

```yaml
override:
  timestamp:
  recommended_activity:
  chosen_activity:
  reason:
  agent_warning:
  next_recommendation:
```

### 11.11 Context-pack and demo integration

The context pack should include the active activity, due review, recommended next activity, expected evidence, learner activity preferences, and recent activity effectiveness — using compact summaries only.

The demo should show one non-question activity:

```text
StudyDD recommendation: short comparison drill.

The learner completed the activity outside the chat and uploaded/entered the result.
StudyDD reviewed the submitted evidence, updated skill state, scheduled review, and recorded the next action.
```

### 11.12 Startup/product note

In a future startup version, this becomes the real product surface:

- source panel
- upload zone
- voice-note review
- whiteboard/diagram review
- interview rehearsal
- presentation rehearsal
- exercise platform integration
- paper-work photo review
- progress map
- evidence-backed mastery state

The current template should stay repo-native and coding-agent-first. No UI, web app, database, or external integrations are added in this direction yet.

### 11.13 Scope boundary for the current slice

The Source-Grounded Question Quality v1 slice (Sections 1–8) remains the immediate implementation scope. The Learning Activity Orchestrator is the next product direction and should be designed and implemented in a follow-up slice after v1 is complete.
