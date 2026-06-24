# StudyDD Study Skills

Study skills are tutoring policies, not learner records.

They shape how the agent teaches, questions, grades, and reviews.
They do not replace canonical learner state.

## What a study skill is

A `study_skills/<id>/SKILL.md` file tells a coding agent how to tutor a particular kind of learning target. IT certifications, philosophy, primary maths, language learning, interview prep, and practical labs need different question styles, grading rules, evidence standards, and review strategies.

## How targets select a study skill

A target declares its study skill in `TARGET.yaml`:

```yaml
study_skill: it_certification
```

If no skill is declared, the agent falls back to `study_skills/generic/SKILL.md`.

## How agents use the active study skill

When a target declares a study skill, the agent must load the matching `SKILL.md` before asking, grading, scheduling reviews, or upgrading readiness. The context pack builder includes the active study skill automatically.

The study skill controls:

- question style and difficulty
- grading emphasis and common failure modes
- evidence requirements
- readiness upgrade rules
- review mode preferences

## Relationship to learner state

Study skills are read-only policy files. They are not modified per learner. The learner's actual progress still lives in:

- `state/STUDY_STATE.yaml`
- `state/SKILL_MAP.yaml`
- `state/EVIDENCE_LOG.md`
- `reviews/REVIEW_STATE.yaml`
- `sessions/SESSION_LOG.md`

## How to add a new study skill

1. Create `study_skills/<new_id>/SKILL.md` using the same sections as existing skills.
2. Add the skill ID to `scripts/check_studydd.py` `check_study_skills` required list if it should be a core skill.
3. Update this README to mention the new skill.
4. Add an example target using the new skill if it helps learners discover it.

## Built-in study skills

- `generic` — fallback for any target that does not declare a skill.
- `it_certification` — scenario-heavy, service-boundary aware, strict grading.
- `philosophy` — argument reconstruction, primary-text interpretation, charitable reading.
- `primary_math` — small steps, concrete examples, confidence-building, no shame.
- `language_learning` — active recall, production, spaced vocabulary, grammar in context.
- `interview_prep` — behavioral and technical realism, evidence-based stories, follow-up pressure.
- `practical_lab` — hands-on tasks, troubleshooting, process grading.
