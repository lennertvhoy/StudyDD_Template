# StudyDD Spaced-Repetition Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Make time-aware spaced repetition a first-class StudyDD tutoring doctrine: due reviews are learning debt, and the agent strongly prefers them before new material while allowing explicit human override.

**Architecture:** Add a machine-readable `reviews/REVIEW_STATE.yaml`, a human-readable `reviews/REVIEW_OVERRIDES.md`, two small deterministic scripts (`schedule_review.py`, `select_next_study_action.py`), a new protocol, and validator support. Keep the interval scheduler simple and transparent; FSRS/SM-2 can replace it later without changing the surface.

**Tech Stack:** Python 3, PyYAML, timezone-aware ISO 8601 timestamps.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `protocols/SPACED_REPETITION_POLICY.md` | Doctrine and agent rules for review-first behavior. |
| `reviews/REVIEW_STATE.yaml` | Machine-readable review items with `due_at`, intervals, statuses. |
| `reviews/REVIEW_OVERRIDES.md` | Human-readable override log. |
| `scripts/schedule_review.py` | Create/update a review item from a grade/confidence. |
| `scripts/select_next_study_action.py` | Recommend due/overdue review vs. new material. |
| `AGENTS.md` | Add protocol to required reads and lifecycle references. |
| `protocols/START_SESSION.md` | Run selector at session start. |
| `protocols/SELECT_NEXT_ACTION.md` | Prefer due review; handle override. |
| `protocols/SCHEDULE_REVIEW.md` | Use `schedule_review.py`; keep YAML and queue in sync. |
| `protocols/LOW_ENERGY_MODE.md` | Allow lighter review mode without shaming. |
| `PROMPTS/coding_agent_start_prompt.md` | Add review-first rule. |
| `PROMPTS/exam_drill_prompt.md` | Add review-first rule. |
| `README.md` | Short spaced-repetition section. |
| `scripts/check_studydd.py` | Validate review state in learner instances. |
| `scripts/test_study_loop_smoke.py` | Exercise review scheduling, selector, override, validator. |

---

## Tasks

### Task 1: Create review state and override files

**Files:**
- Create: `reviews/REVIEW_STATE.yaml`
- Create: `reviews/REVIEW_OVERRIDES.md`

- [ ] **Step 1: Create empty `reviews/REVIEW_STATE.yaml`**

```yaml
---
review_items: []

# Schema:
# - id: rev_001
#   skill_id: skill_example
#   evidence_id: ev_001
#   target_id: target_example
#   due_at: "2026-06-25T09:00:00+02:00"
#   last_reviewed_at: "2026-06-24T09:00:00+02:00"
#   interval_days: 1
#   stability: null
#   difficulty: null
#   lapses: 0
#   priority: normal
#   status: scheduled
#   source: missed_question
#   override_count: 0
```

- [ ] **Step 2: Create `reviews/REVIEW_OVERRIDES.md`**

Header + empty log list with documented format.

---

### Task 2: Create scheduler script

**Files:**
- Create: `scripts/schedule_review.py`

- [ ] **Step 1: Accept CLI args**

`--skill-id`, `--evidence-id`, `--target-id` (optional), `--grade`, `--confidence`, `--now`, optional `--output` path.

- [ ] **Step 2: Compute interval**

Simple transparent schedule:

- wrong + low confidence: 0 days (same day)
- wrong + medium/high confidence: 1 day
- partial: 1–2 days
- correct + low confidence: 2–3 days
- correct + medium confidence: 3–5 days
- correct + high confidence: 5–7 days
- lapse: reset to shortest interval and increment lapses

- [ ] **Step 3: Write timezone-aware `due_at` and append to `reviews/REVIEW_STATE.yaml`**

Use `datetime` with timezone. Update `reviews/REVIEW_QUEUE.md` as human-readable mirror.

---

### Task 3: Create selector script

**Files:**
- Create: `scripts/select_next_study_action.py`

- [ ] **Step 1: Load review state, study state, skill map, next actions**

- [ ] **Step 2: Count due/overdue reviews**

Compare `due_at` to current time (use `--now` or system time).

- [ ] **Step 3: Print recommendation**

```text
StudyDD recommendation: review first.

Due reviews: 3
Overdue reviews: 1
Recommended action: review rev_003 before new material.
Reason: this skill is overdue and has weak evidence.

Override allowed:
Say "override review because <reason>" and the agent must record the override.
```

---

### Task 4: Create spaced-repetition protocol

**Files:**
- Create: `protocols/SPACED_REPETITION_POLICY.md`

- [ ] **Step 1: Document doctrine**

"Due reviews are not reminders. They are learning debt."

- [ ] **Step 2: Define rules**

- Check current time at session start.
- Read `reviews/REVIEW_STATE.yaml`.
- Due/overdue reviews are default next action.
- New material allowed only when no reviews due, small review load + deadline plan, explicit override, low-energy mode, or urgent deadline.
- Record overrides with timestamp, skipped IDs, reason, chosen action, next recommendation.
- No shaming; phrase as recommendation.
- Use phrase: "Recommended by StudyDD: review first. You can override, but this is the highest-retention move."

---

### Task 5: Update tutor protocols and prompts

**Files:**
- Modify: `AGENTS.md`, `protocols/START_SESSION.md`, `protocols/SELECT_NEXT_ACTION.md`, `protocols/SCHEDULE_REVIEW.md`, `protocols/LOW_ENERGY_MODE.md`, `PROMPTS/coding_agent_start_prompt.md`, `PROMPTS/exam_drill_prompt.md`

- [ ] **Step 1: Add review-first rule to each relevant file**

At session start, run or perform equivalent of `scripts/select_next_study_action.py`. Recommend due/overdue review before new material. Record override.

- [ ] **Step 2: Add `SPACED_REPETITION_POLICY.md` to AGENTS.md required-read list and lifecycle references**

---

### Task 6: Strengthen validator

**Files:**
- Modify: `scripts/check_studydd.py`

- [ ] **Step 1: Require review state files where appropriate**

Add `reviews/REVIEW_STATE.yaml` and `reviews/REVIEW_OVERRIDES.md` to required review files. Do not fail template mode for empty review state.

- [ ] **Step 2: Validate review items**

In learner_instance mode, validate:
- `due_at` and `last_reviewed_at` are valid timezone-aware ISO timestamps (if present)
- `skill_id` exists in `state/SKILL_MAP.yaml`
- `evidence_id` exists in `state/EVIDENCE_LOG.md` (if provided)
- `interval_days` positive number
- `status` one of `scheduled`, `due`, `overdue`, `completed`, `suspended`
- warn on repeated overrides for same item

- [ ] **Step 3: Warn if overdue active items are not visible**

Check `reviews/REVIEW_QUEUE.md` or `NEXT_ACTIONS.md` mention overdue review IDs.

---

### Task 7: Extend study-loop smoke test

**Files:**
- Modify: `scripts/test_study_loop_smoke.py`

- [ ] **Step 1: Schedule a review with `schedule_review.py`**

- [ ] **Step 2: Run `select_next_study_action.py` with `--now` set after due_at**

- [ ] **Step 3: Log an override**

- [ ] **Step 4: Assert validator still passes**

---

### Task 8: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add short spaced-repetition section**

---

### Task 9: Validate, commit, push

- [ ] **Step 1: Run `python3 scripts/check_studydd.py`**
- [ ] **Step 2: Run `python3 scripts/test_instantiate_template.py`**
- [ ] **Step 3: Run `python3 scripts/test_study_loop_smoke.py`**
- [ ] **Step 4: Run `git diff --check`**
- [ ] **Step 5: Commit and push**

---

## Self-Review

**Spec coverage:** Every numbered requirement maps to a task above.

**Placeholder scan:** No `TBD`/`TODO`; file paths and behaviors are explicit.

**Type consistency:** Review item field names match `reviews/REVIEW_STATE.yaml` schema. Status values are the canonical five.
