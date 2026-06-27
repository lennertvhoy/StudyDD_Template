# StudyDD Next-Activity Decision Slice — Design

**Date:** 2026-06-27  
**Scope:** Template-quality improvement to `scripts/plan_learning_activity.py`, activity templates, protocols, tests, and docs.  
**Constraint:** Keep the repo generic, public-safe, and auditable. No personal learner data.

## Problem

`scripts/plan_learning_activity.py` already recommends learning activities, but its decision logic is shallow:

- It does not explicitly distinguish an **exam-style question** from a generic retrieval question.
- It does not explicitly route to **lab/practical exercise** or **diagram/visual explanation** based on skill state.
- It has no concept of a **recent-info check** for volatile topics.
- It does not look at recent activity types when deciding, so it can repeatedly recommend the same format.

The agent should be able to recommend among the five requested categories with clear, auditable rules.

## Goal

Add or improve the next-activity mechanism so StudyDD can recommend among:

1. exam-style question
2. spaced-repetition review
3. lab/practical exercise
4. diagram/visual explanation
5. recent-info check for topics that may change

The decision must be:

- Protocol-driven (rules live in `protocols/SELECT_NEXT_ACTION.md` and `protocols/LEARNING_ACTIVITY_POLICY.md`).
- Auditable (the script prints the rule that triggered the recommendation).
- Template-safe (no learner-specific data in template mode).
- Tested (new tests in `scripts/test_learning_activities.py`).

## Non-goals

- Build a full scheduler or scoring engine.
- Add new state files or schema beyond the existing `state/ACTIVITY_STATE.yaml`.
- Containerize Study_Lenny.
- Personalize the template repo.

## Design

### 1. New activity type: `recent_info_check`

Add to `activities/ACTIVITY_TEMPLATES.yaml`:

```yaml
recent_info_check:
  description: "Verify current facts, sources, or exam objectives for a volatile topic before authoritative study."
```

Add one template:

```yaml
- id: source_freshness_check
  activity_type: recent_info_check
  best_for:
    - volatile_topic
    - it_certification
    - live_topic
  expected_evidence:
    - source_metadata
    - short_summary
    - answer_to_check_question
```

This makes the activity first-class and gives agents a concrete evidence format.

### 2. Extend `scripts/plan_learning_activity.py`

Add helper functions and decision branches:

- `target_is_volatile(study_state, skill_map)` — returns `True` if the active target or skill has volatility in `{"moderate", "volatile", "live"}` and no fresh source metadata is recorded.
- `recent_activity_types(activity_state)` — returns the set/list of recent activity types from `recent_activities`.
- `choose_activity_type(...)` extended with:
  1. **Spaced review** first (unchanged, highest priority).
  2. **Recent-info check** if the active target/skill is volatile and sources are stale or missing.
  3. **Lab/practical exercise** if the weakest skill has tags like `sysadmin`, `cloud`, `networking`, `practical_lab`.
  4. **Diagram/visual explanation** if the weakest skill has tags like `conceptual_understanding`, `architecture`, `philosophy`, or if the same skill was weak after a chat question.
  5. **Exam-style question** if the active target type is `certification` or `exam`, the skill is at least `practiced`, and recent activities have not been heavy on questions.
  6. Fallback to retrieval question / explain-back as today.

The script already records `reason`; we will make the reason reference the triggering rule (e.g., "Rule: volatile target with stale sources → recent_info_check").

### 3. Update protocols

`protocols/SELECT_NEXT_ACTION.md`:

- Add a subsection **Activity-type routing** that lists the five categories and the conditions that trigger each.
- Reference `activities/ACTIVITY_TEMPLATES.yaml` and `scripts/plan_learning_activity.py`.

`protocols/LEARNING_ACTIVITY_POLICY.md`:

- Mention the new `recent_info_check` activity type.
- Document that volatile topics route to `recent_info_check` before authoritative questions.

### 4. Add/update tests

In `scripts/test_learning_activities.py`:

- `test_recent_info_check_activity_type_exists()` — verify `recent_info_check` is in `ACTIVITY_TEMPLATES.yaml`.
- `test_plan_recommends_recent_info_check_for_volatile_target()` — create a temporary learner instance with a volatile target and stale sources, run `plan_learning_activity.py`, assert recommendation is `recent_info_check`.
- `test_plan_recommends_diagram_for_conceptual_skill()` — assert `diagram_or_whiteboard` is recommended when skill tags include `conceptual_understanding`.
- `test_plan_recommends_lab_for_practical_skill()` — assert `practical_lab` is recommended when skill tags include `practical_lab` / `cloud` / etc.
- `test_plan_recommends_exam_question_for_certification_target()` — assert exam-style question routing for certification targets.
- Keep existing tests passing.

### 5. Update docs

`README.md`:

- In the learning-activities paragraph, mention the five categories and source-freshness-aware routing.

Add short section: **How the agent chooses the next activity** with a bullet list:

1. Due reviews first.
2. Fresh-source check for volatile topics.
3. Lab or diagram when the skill domain fits.
4. Exam-style question when the target is an exam/certification.
5. Fallback to a focused retrieval question.

### 6. Public-safety / template-safety

- All changes use generic placeholder data.
- No learner profile, targets, evidence, or review data is seeded in template mode.
- The new tests create temporary instances and clean them up.
- `state/ACTIVITY_STATE.yaml` in template mode remains empty.

## Files touched

- `activities/ACTIVITY_TEMPLATES.yaml`
- `scripts/plan_learning_activity.py`
- `protocols/SELECT_NEXT_ACTION.md`
- `protocols/LEARNING_ACTIVITY_POLICY.md`
- `scripts/test_learning_activities.py`
- `README.md`
- `docs/superpowers/specs/2026-06-27-next-activity-decision-slice-design.md` (this file)

## Validation

Run:

```bash
python3 scripts/check_studydd.py
python3 scripts/test_learning_activities.py
python3 scripts/plan_learning_activity.py --demo
```

CI will also run these via `.github/workflows/validate.yml`.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Overcomplicating the decision tree | Keep rules as simple if/elif branches with explicit reasons. No scoring engine. |
| Template pollution | No learner data; tests use temp instances. |
| Tests become flaky | Use deterministic temp instances and explicit timestamps. |
| Backward incompatibility | Existing activity types and demo output remain unchanged. |

## Next recommended slice

After this lands, a natural follow-up is to wire `scripts/plan_learning_activity.py` into `scripts/build_context_pack.py` so the context pack includes the active activity recommendation reason, and to add a `scripts/test_next_activity_decision.py` focused solely on the decision rules.
