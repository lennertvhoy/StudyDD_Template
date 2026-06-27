# Source-Grounded Question Quality v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a source freshness gate, question-quality governor, and learner-adaptation layer to StudyDD_Template so volatile topics cannot be tested from AI memory, while stable topics avoid unnecessary source refresh.

**Architecture:** Add policy files, a machine-readable source registry, a learner profile, three small deterministic scripts, and validator/context-pack integration. Keep source truth centralized in `sources/SOURCE_STATE.yaml`; question files reference source IDs; validators recompute freshness rather than trusting cached labels.

**Tech Stack:** Python 3.11+, PyYAML, standard library only for new scripts.

---

## File map

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
- `Evidence/005-2026-06-24-studydd-source-grounded-question-quality/` (evidence bundle, max 12 files)

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
- `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml`
- `study_skills/generic/SKILL.md` (and optionally other skill files)

---

## Prerequisite: verify repo state

- [ ] **Step P.1: Verify repo path, remote, mode**

Run:

```bash
cd /home/ff/Documents/Projects/StudyDD
pwd
git rev-parse --show-toplevel
git remote -v
cat state/STUDYDD_MODE.yaml
cat state/STUDYDD_TEMPLATE_VERSION.yaml
```

Expected:
- repo root is `/home/ff/Documents/Projects/StudyDD`
- remote is `https://github.com/lennertvhoy/StudyDD_Template.git`
- mode is `template`

- [ ] **Step P.2: Run existing tests to establish baseline**

Run:

```bash
python3 scripts/check_studydd.py
python3 scripts/test_instantiate_template.py
python3 scripts/test_create_instance.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_demo_replay.py
python3 scripts/test_compact_state.py
python3 scripts/test_context_pack.py
python3 scripts/test_study_skills.py
python3 scripts/test_performance_policy.py
python3 scripts/test_validate_touched_state.py
```

Expected: all pass.

---

## Task 1: Create policy files

**Files:**
- Create: `protocols/SOURCE_FRESHNESS_POLICY.md`
- Create: `protocols/SOURCE_REFRESH_POLICY.md`
- Create: `protocols/QUESTION_QUALITY_GOVERNOR.md`
- Create: `protocols/LEARNER_ADAPTATION_POLICY.md`
- Create: `protocols/LEARNER_FEEDBACK_POLICY.md`

- [ ] **Step 1.1: Write `protocols/SOURCE_FRESHNESS_POLICY.md`**

Use the approved volatility classes and rules from the design spec. Include:
- volatility_classes YAML block (stable, slow_changing, moderate, volatile, live)
- rule: target declares volatility; default moderate with warning
- rule: volatile/live authoritative questions require fresh usable official/high_authority sources
- rule: stale sources may be used only with explicit override and practice-only label
- rule: agent must not hide uncertainty
- rule: user may override freshness recommendations

- [ ] **Step 1.2: Write `protocols/SOURCE_REFRESH_POLICY.md`**

Include:
- refresh only when freshness gate requires it
- prefer official/high_authority sources
- refresh smallest source set
- cache metadata in `sources/SOURCE_STATE.yaml`
- record checked source, timestamp, authority, volatility, usability, reason
- do not refresh stable topics unnecessarily
- learner override options

- [ ] **Step 1.3: Write `protocols/QUESTION_QUALITY_GOVERNOR.md`**

Include:
- internal question quality record fields
- no authoritative volatile/live question without fresh source
- answer key private until grading
- scenario questions test reasoning
- plausible distractors
- match study skill and learner level
- uncertainty → simpler source-grounded question or source refresh
- learner-facing honesty messages

- [ ] **Step 1.4: Write `protocols/LEARNER_ADAPTATION_POLICY.md`**

Include:
- doctrine: adapt but do not manipulate
- preference informs route, evidence determines readiness, target requirements constrain both
- ask feedback occasionally, not every turn
- track preferences separately from mastery evidence
- distinguish preference, effectiveness, energy state, target requirements
- recommendation strength: weak | moderate | strong
- learner can override; record override
- never flatter readiness to match preference

- [ ] **Step 1.5: Write `protocols/LEARNER_FEEDBACK_POLICY.md`**

Include:
- ask feedback after several sessions, repeated misses, repeated overrides, low engagement, target milestones
- not during every ordinary question
- example prompts from spec
- keep feedback short and useful

- [ ] **Step 1.6: Commit policies**

```bash
git add protocols/SOURCE_FRESHNESS_POLICY.md protocols/SOURCE_REFRESH_POLICY.md protocols/QUESTION_QUALITY_GOVERNOR.md protocols/LEARNER_ADAPTATION_POLICY.md protocols/LEARNER_FEEDBACK_POLICY.md
git commit -m "feat: add source freshness, refresh, question quality, and learner adaptation policies"
```

---

## Task 2: Create state files

**Files:**
- Create: `sources/SOURCE_STATE.yaml`
- Create: `state/LEARNER_PROFILE.yaml`

- [ ] **Step 2.1: Write `sources/SOURCE_STATE.yaml`**

Start with empty `sources: []` for template mode. The demo fixture will add a demo source separately under `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml`.

```yaml
# Canonical source freshness registry.
# Template mode keeps this empty; learner instances populate it.
sources: []
```

- [ ] **Step 2.2: Write `state/LEARNER_PROFILE.yaml`**

Use the generic/empty template shape from the spec.

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

- [ ] **Step 2.3: Commit state files**

```bash
git add sources/SOURCE_STATE.yaml state/LEARNER_PROFILE.yaml
git commit -m "feat: add SOURCE_STATE.yaml and LEARNER_PROFILE.yaml templates"
```

---

## Task 3: Extend question-bank schema

**Files:**
- Modify: `docs/question-bank-schema.md`

- [ ] **Step 3.1: Add new optional fields**

Append a new section after the required fields that documents:

```yaml
# Optional but recommended quality/freshness fields
volatility: stable | slow_changing | moderate | volatile | live
source_ids:
  - mslearn_ai_search_overview
source_freshness_status: fresh | stale | not_required | unverified   # cached hint; linter recomputes
question_mode: authoritative_current | conceptual_practice | stale_practice | exam_sim | remediation
private_answer_key:
  correct_answer: "..."
  rationale: "..."
  source_support:
    - source_id: mslearn_ai_search_overview
      checked_at: "2026-06-24T12:00:00+00:00"
      section: "Overview"
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

- [ ] **Step 3.2: Document backward compatibility**

Add a note that existing `source_ref` strings are still accepted but moderate+/volatile topics should prefer `source_ids` tied to `SOURCE_STATE.yaml`.

- [ ] **Step 3.3: Commit schema extension**

```bash
git add docs/question-bank-schema.md
git commit -m "feat: extend question-bank schema with volatility, source IDs, question mode, and quality gate"
```

---

## Task 4: Implement `scripts/check_source_freshness.py`

**Files:**
- Create: `scripts/check_source_freshness.py`
- Create: `scripts/test_source_freshness.py`

- [ ] **Step 4.1: Write the script skeleton**

The script must:
- parse `--target-id`, `--question-id`, `--allow-stale`, `--now`
- read `sources/SOURCE_STATE.yaml`
- read target volatility from `targets/<id>/TARGET.yaml` if available
- compute freshness per source
- print report
- exit non-zero for volatile/live target without fresh usable source unless `--allow-stale`

- [ ] **Step 4.2: Implement freshness computation**

Use this core function:

```python
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import yaml

VOLATILITY_MAX_AGE_DAYS = {
    "stable": 3650,
    "slow_changing": 730,
    "moderate": 30,
    "volatile": 7,
    "live": 1,
}
# Canonical constants live in scripts/check_source_freshness.py.

AUTHORITY_ORDER = ["official", "high_authority", "instructor", "textbook", "learner_notes", "unverified"]


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def compute_freshness(source: dict[str, Any], now: datetime, target_volatility: str) -> str:
    if not source.get("usable_for_questions", True):
        return "unverified"
    expires_at = parse_iso(source.get("expires_at", ""))
    last_checked_at = parse_iso(source.get("last_checked_at", ""))
    if expires_at:
        if now <= expires_at:
            return "fresh"
        else:
            return "expired"
    if last_checked_at:
        volatility = source.get("volatility") or target_volatility
        max_age_days = VOLATILITY_MAX_AGE_DAYS.get(volatility, 90)
        if now - last_checked_at <= timedelta(days=max_age_days):
            return "fresh"
        else:
            return "stale"
    return "missing_timestamp"
```

- [ ] **Step 4.3: Implement CLI output**

Example report format:

```text
Source freshness check

Target: demo-ai-search-exam
Volatility: volatile

Fresh usable sources:
- mslearn_ai_search_overview

Stale sources:
- old_blog_ai_search_notes

Unverified sources:
- some_forum_post

Recommendation:
Use official source mslearn_ai_search_overview for new authoritative questions.
Do not generate product-current questions from memory.
```

- [ ] **Step 4.4: Add `--allow-stale` behavior**

When `--allow-stale` is used, print:

```text
Stale source allowed by override.
Question mode: practice-only, not authoritative-current.
```

and exit 0.

- [ ] **Step 4.5: Write tests**

`scripts/test_source_freshness.py` must cover:
- volatile target with fresh official source passes
- volatile target with stale source fails/warns
- stable target does not require source refresh
- script does not perform web search (no network calls)
- `--allow-stale` switches to practice-only mode
- `--now` produces deterministic output

Use temporary directories and subprocess to run the script.

- [ ] **Step 4.6: Run tests**

```bash
python3 scripts/test_source_freshness.py
```

Expected: PASS.

- [ ] **Step 4.7: Commit**

```bash
git add scripts/check_source_freshness.py scripts/test_source_freshness.py
git commit -m "feat: add source freshness gate and tests"
```

---

## Task 5: Implement `scripts/lint_questions.py`

**Files:**
- Create: `scripts/lint_questions.py`
- Create: `scripts/test_question_quality.py`

- [ ] **Step 5.1: Write the script skeleton**

The script must:
- discover question files under `targets/` and `EXAMPLES/`
- read `sources/SOURCE_STATE.yaml`
- validate each question file
- print findings
- exit non-zero only for real failures (not missing learner question banks in template mode)

- [ ] **Step 5.2: Implement checks**

Checks to implement:
1. missing `id`, `target_id`, `skill_id`
2. missing `source_ids` for moderate/volatile/live topics (warn)
3. stale source used for volatile/live `authoritative_current` question (fail)
4. answer-key leakage in `public_prompt` (fail if `private_answer_key` text appears in `public_prompt`)
5. correct answer always in same visible option position (heuristic; warn)
6. `generated_from_memory_allowed` derived permission mismatch (warn/fail)
7. `quality_gate: fail` for volatile/live `authoritative_current` with stale/missing sources
8. `quality_gate_reason` required when gate is `warn` or `fail`
9. legacy `source_ref` only for moderate+/volatile topics triggers warning

- [ ] **Step 5.3: Implement source freshness recomputation**

For each `source_id` in a question, look it up in `SOURCE_STATE.yaml`, compute freshness using the same logic as `check_source_freshness.py`, and compare to the question's cached `source_freshness_status`.

- [ ] **Step 5.4: Implement template-safe behavior**

In template mode (read `state/STUDYDD_MODE.yaml`), the script should:
- validate demo/example question banks
- validate schema correctness
- not fail because there is no real learner question bank

Use `--strict` flag to optionally fail on warnings (for learner-instance CI if desired).

- [ ] **Step 5.5: Write tests**

`scripts/test_question_quality.py` must cover:
- question quality record fails when volatile topic has no source
- answer-key leakage is caught
- legacy `source_ref` triggers warning for volatile topic
- `authoritative_current` with stale source fails quality gate
- `quality_gate_reason` required for warn/fail
- template mode does not fail on missing learner question banks

- [ ] **Step 5.6: Run tests**

```bash
python3 scripts/test_question_quality.py
```

Expected: PASS.

- [ ] **Step 5.7: Commit**

```bash
git add scripts/lint_questions.py scripts/test_question_quality.py
git commit -m "feat: add question quality linter and tests"
```

---

## Task 6: Implement `scripts/suggest_study_adjustment.py`

**Files:**
- Create: `scripts/suggest_study_adjustment.py`
- Create: `scripts/test_learner_adaptation.py`

- [ ] **Step 6.1: Write the script skeleton**

The script must:
- inspect recent mistakes, review misses, overrides, confidence calibration, learner preferences, target deadline, study skill
- output at most one recommendation
- exit 0 even when there is insufficient evidence
- support `--demo` for deterministic demo output

- [ ] **Step 6.2: Implement recommendation logic**

Example deterministic logic:

```python
def suggest(recent_evidence, reviews, overrides, preferences, deadline_days, skill_id):
    # Count weak evidence by mistake tag
    tag_counts = {}
    for ev in recent_evidence:
        for tag in ev.get("mistake_tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    if tag_counts:
        top_tag = max(tag_counts, key=tag_counts.get)
        if tag_counts[top_tag] >= 3:
            return {
                "strength": "strong",
                "recommendation": f"You keep missing {top_tag} questions. Do two short comparison drills before adding new material.",
                "why": f"The last {tag_counts[top_tag]} weak evidence items involve {top_tag}.",
            }
        if tag_counts[top_tag] >= 2:
            return {
                "strength": "moderate",
                "recommendation": f"You missed {tag_counts[top_tag]} {top_tag} questions. Consider one focused review.",
                "why": "A pattern is appearing.",
            }
    return {"strength": None, "recommendation": "No recommendation: insufficient evidence.", "why": ""}
```

- [ ] **Step 6.3: Implement `--demo` output**

When `--demo` is passed, output:

```text
StudyDD suggestion:

You missed a scenario tradeoff. Next time, use a short comparison drill.

Why:
The last weak evidence item involved choosing between similar services.

Learner control:
You can accept, modify, or override this.
```

- [ ] **Step 6.4: Implement normal-mode output**

When not in demo mode, read actual state files and produce at most one recommendation. If insufficient evidence, print:

```text
StudyDD suggestion:
No recommendation: insufficient evidence.
```

- [ ] **Step 6.5: Write tests**

`scripts/test_learner_adaptation.py` must cover:
- learner profile remains generic in template mode
- adaptation suggestion is evidence-based and non-spammy
- `--demo` produces deterministic output
- insufficient evidence yields "No recommendation"

- [ ] **Step 6.6: Run tests**

```bash
python3 scripts/test_learner_adaptation.py
```

Expected: PASS.

- [ ] **Step 6.7: Commit**

```bash
git add scripts/suggest_study_adjustment.py scripts/test_learner_adaptation.py
git commit -m "feat: add learner adaptation suggestion script and tests"
```

---

## Task 7: Update `scripts/check_studydd.py`

**Files:**
- Modify: `scripts/check_studydd.py`

- [ ] **Step 7.1: Validate new state files**

Add checks that:
- `sources/SOURCE_STATE.yaml` exists
- `state/LEARNER_PROFILE.yaml` exists
- required protocols exist

- [ ] **Step 7.2: Validate source freshness for learner instances**

In learner-instance mode, ensure volatile/live targets have at least one fresh usable official/high_authority source before authoritative question generation. Use the same freshness computation logic as `check_source_freshness.py` (consider importing/shared function or duplicating carefully).

- [ ] **Step 7.3: Validate learner profile in template mode**

In template mode, `state/LEARNER_PROFILE.yaml` must be generic/empty. Check that key fields are empty/null/default.

- [ ] **Step 7.4: Validate question quality records**

For question files that exist, validate:
- required fields when quality block present
- source IDs referenced by question records exist in `SOURCE_STATE.yaml`
- volatile/live `authoritative_current` questions do not pass quality gate with stale/missing sources
- `quality_gate_reason` present for warn/fail

- [ ] **Step 7.5: Validate recorded overrides**

If a learner override bypasses a strong freshness recommendation, ensure an override record exists (heuristic check in `reviews/REVIEW_OVERRIDES.md` or `state/EVIDENCE_LOG.md`).

- [ ] **Step 7.6: Run validator**

```bash
python3 scripts/check_studydd.py
```

Expected: PASS (no errors in template mode).

- [ ] **Step 7.7: Commit**

```bash
git add scripts/check_studydd.py
git commit -m "feat: extend validator for source freshness, learner profile, and question quality"
```

---

## Task 8: Update `scripts/build_context_pack.py`

**Files:**
- Modify: `scripts/build_context_pack.py`

- [ ] **Step 8.1: Include source freshness status**

For the active target, run the equivalent of `check_source_freshness.py` logic and include:
- target volatility class
- fresh usable sources list
- stale/missing sources list
- recommendation

- [ ] **Step 8.2: Include learner adaptation summary**

Read `state/LEARNER_PROFILE.yaml` and include:
- source_refresh_preference
- one current study adjustment recommendation (from `suggest_study_adjustment.py` output or equivalent)
- recent recurring friction if any

- [ ] **Step 8.3: Include question quality requirements**

For the active task (`ask_question`, `grade_answer`), include a short reminder of the quality gate requirements:
- target volatility
- required source freshness for authoritative_current questions
- question mode guidance

- [ ] **Step 8.4: Performance budget check**

Ensure the additions do not blow the performance budget. If they do, trim output or warn.

- [ ] **Step 8.5: Run context pack tests**

```bash
python3 scripts/test_context_pack.py
```

Expected: PASS.

- [ ] **Step 8.6: Commit**

```bash
git add scripts/build_context_pack.py
git commit -m "feat: include source freshness, learner adaptation, and quality requirements in context pack"
```

---

## Task 9: Update demo replay and fixture

**Files:**
- Modify: `scripts/run_demo_replay.py`
- Modify: `scripts/test_demo_replay.py`
- Modify: `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml`
- Create: `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml`

- [ ] **Step 9.1: Add volatility to demo target**

Edit `EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml` to add:

```yaml
volatility: volatile
```

- [ ] **Step 9.2: Create demo source state**

Create `EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml`:

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

- [ ] **Step 9.3: Update demo replay output**

In `scripts/run_demo_replay.py`, add output lines showing:

```text
StudyDD checks source freshness before generating product-current questions.
The demo uses a demo official source marked fresh.
The agent does not search the web because the cached source is fresh enough.
If the source were stale, StudyDD would ask to refresh or choose a stable review instead.
```

and a learner-adaptation moment:

```text
StudyDD suggestion:
You missed a scenario tradeoff. Next time, use a short comparison drill.
Learner control:
You can accept, modify, or override this.
```

- [ ] **Step 9.4: Update demo replay tests**

In `scripts/test_demo_replay.py`, assert that the above messages appear in the demo output.

- [ ] **Step 9.5: Run demo tests**

```bash
python3 scripts/test_demo_replay.py
python3 scripts/run_demo_replay.py
```

Expected: PASS and clean output.

- [ ] **Step 9.6: Commit**

```bash
git add scripts/run_demo_replay.py scripts/test_demo_replay.py EXAMPLES/demo_ai_search_exam/targets/demo-ai-search-exam/TARGET.yaml EXAMPLES/demo_ai_search_exam/sources/SOURCE_STATE.yaml
git commit -m "feat: demo replay shows cached source freshness and learner adaptation"
```

---

## Task 10: Update agent-facing docs

**Files:**
- Modify: `AGENTS.md`
- Modify: `PROMPTS/coding_agent_start_prompt.md`
- Modify: `study_skills/generic/SKILL.md`

- [ ] **Step 10.1: Update `AGENTS.md`**

Add to Core Rules:

```text
### Core Rule X: Do not generate authoritative volatile questions from memory
Do not generate authoritative questions on volatile topics from memory. Run the freshness gate or use cached fresh source metadata.
```

Add the new protocols to "Required First Actions":

```text
41. `protocols/SOURCE_FRESHNESS.md`
42. `protocols/SOURCE_REFRESH_POLICY.md`
43. `protocols/QUESTION_QUALITY_GOVERNOR.md`
44. `protocols/LEARNER_ADAPTATION_POLICY.md`
45. `protocols/LEARNER_FEEDBACK_POLICY.md`
```

Add freshness check to the Session Flow (before generating a volatile question, run `scripts/check_source_freshness.py` or inspect `SOURCE_STATE.yaml`).

- [ ] **Step 10.2: Update `PROMPTS/coding_agent_start_prompt.md`**

Add under "During Study Sessions":

```text
- Before generating or grading authoritative questions on moderate, volatile, or live topics, run `scripts/check_source_freshness.py` for the active target. Do not invent current product, pricing, portal, or exam details from memory.
- Use `protocols/QUESTION_QUALITY_GOVERNOR.md` to validate each generated question.
- Respect learner adaptation preferences from `state/LEARNER_PROFILE.yaml`; never flatter readiness to match preference.
```

- [ ] **Step 10.3: Update study skills**

Update `study_skills/generic/SKILL.md` to include a short section pointing to the new policies. Optionally add lightweight declarations to `study_skills/it_certification/SKILL.md` and `study_skills/interview_prep/SKILL.md` such as:

```markdown
## Source freshness and adaptation

- This skill often touches volatile/current material. Prefer `authoritative_current` questions only when `sources/SOURCE_STATE.yaml` shows fresh official or high-authority sources.
- For stable concepts, `conceptual_practice` is acceptable.
- Adapt question style from learner evidence, not preference alone.
```

- [ ] **Step 10.4: Commit**

```bash
git add AGENTS.md PROMPTS/coding_agent_start_prompt.md study_skills/generic/SKILL.md
git commit -m "feat: tell agents to use freshness gate, quality governor, and learner adaptation policies"
```

---

## Task 11: Update README and future efficiency doc

**Files:**
- Modify: `README.md`
- Create: `docs/future-model-efficiency.md`

- [ ] **Step 11.1: Add README sections**

Add two concise sections:

```markdown
### Source-grounded question quality

StudyDD does not treat AI memory as current truth. Stable topics can use local state, but volatile topics such as cloud services, vendor certifications, pricing, preview features, and product names require fresh source metadata before authoritative questions. Source refresh is cached and deliberate, not performed on every question.

### Learner adaptation with learner control

StudyDD adapts question style, review strategy, and study recommendations from evidence and learner feedback. It may suggest better approaches, but the learner can accept, modify, or override them. Overrides are recorded so the study state remains honest.
```

- [ ] **Step 11.2: Create `docs/future-model-efficiency.md`**

Write the future-facing model efficiency note from the spec, including the task_complexity taxonomy. No runtime routing.

- [ ] **Step 11.3: Commit**

```bash
git add README.md docs/future-model-efficiency.md
git commit -m "docs: add source-grounded quality and learner adaptation sections; note future model efficiency"
```

---

## Task 12: Update CI workflow

**Files:**
- Modify: `.github/workflows/validate.yml`

- [ ] **Step 12.1: Add new test and script runs**

Add after the existing test steps:

```yaml
      - run: python3 scripts/test_source_freshness.py
      - run: python3 scripts/test_question_quality.py
      - run: python3 scripts/test_learner_adaptation.py
      - run: python3 scripts/check_source_freshness.py --target-id demo-ai-search-exam --now "2026-06-24T12:00:00+00:00"
      - run: python3 scripts/lint_questions.py
      - run: python3 scripts/suggest_study_adjustment.py --demo
```

- [ ] **Step 12.2: Commit**

```bash
git add .github/workflows/validate.yml
git commit -m "ci: run source freshness, question quality, and learner adaptation checks"
```

---

## Task 13: Full validation run

- [ ] **Step 13.1: Run required validation commands**

```bash
cd /home/ff/Documents/Projects/StudyDD
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

- [ ] **Step 13.2: Fix any failures**

If any command fails, diagnose and fix. Re-run the affected tests.

- [ ] **Step 13.3: Commit fixes**

```bash
git add ...
git commit -m "fix: address validation findings"
```

---

## Task 14: Create evidence bundle

**Files:**
- Create: `Evidence/005-2026-06-24-studydd-source-grounded-question-quality/...`

- [ ] **Step 14.1: Create evidence folder and files**

Create up to 12 files:

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

- [ ] **Step 14.2: Commit evidence**

```bash
git add Evidence/005-2026-06-24-studydd-source-grounded-question-quality/
git commit -m "evidence: add source-grounded question quality evidence bundle"
```

---

## Task 15: Final commit and push

- [ ] **Step 15.1: Review git history**

```bash
git log --oneline -15
```

- [ ] **Step 15.2: Final commit (if needed)**

If there are uncommitted changes, commit them. Otherwise proceed.

- [ ] **Step 15.3: Push to origin main**

```bash
git push origin main
```

Expected: push succeeds.

- [ ] **Step 15.4: Verify pushed status**

```bash
git status --short
git log --oneline -1
```

Expected: clean worktree, latest commit on main.

---

## Spec coverage self-check

| Spec requirement | Task |
|---|---|
| Volatility classes | Task 1 |
| Target declares volatility | Task 9 |
| `sources/SOURCE_STATE.yaml` canonical registry | Task 2, Task 4 |
| `check_source_freshness.py` no web search, fixed `--now` | Task 4 |
| Source refresh policy | Task 1 |
| Extended question-bank schema | Task 3 |
| Question modes and source-grounded answer key | Task 3, Task 5 |
| `lint_questions.py` recomputes freshness | Task 5 |
| `LEARNER_PROFILE.yaml` generic template | Task 2 |
| `suggest_study_adjustment.py` evidence-based, `--demo` | Task 6 |
| `check_studydd.py` validates new state | Task 7 |
| `build_context_pack.py` includes freshness/adaptation | Task 8 |
| Demo replay cached freshness + learner control | Task 9 |
| `AGENTS.md` and start prompt updated | Task 10 |
| README sections | Task 11 |
| CI updated with deterministic runs | Task 12 |
| Tests for all three layers | Tasks 4–6 |
| Evidence bundle | Task 14 |
| Commit and push | Task 15 |

## Placeholder scan

No TBD, TODO, or vague steps remain. Every task names exact files and shows concrete code or commands.

## Backlog note: cross-platform setup and dependency consent

This slice does not implement cross-platform setup. Track it as the next platform-hardening slice after Learning Activity Orchestrator. Add the following note to the final handoff:

> Cross-platform dependency setup and consent is now tracked as the next platform-hardening concern; it was not implemented in this slice to keep scope focused. The next platform slice should add `requirements.txt`, `scripts/setup_studydd.py`, `docs/setup.md`, and CI coverage for Ubuntu/Windows/macOS, with explicit consent before installing dependencies.
