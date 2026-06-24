# Add A New Study Target

Use this prompt when the learner wants to add a new certification, exam, interview, course, or skill target.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.

## Gather Target Information

Ask the learner:

- Target title
- Type: certification / interview / course / skill
- Exam or goal description
- Deadline (optional)
- Success criteria
- Trusted sources

## Create Target

1. Create a stable lowercase folder ID under `targets/`, e.g. `targets/new-target/`.
2. Write `targets/<id>/TARGET.yaml` with id, title, type, exam_or_goal, deadline, success_criteria, trusted_sources, and readiness_policy.
3. Optionally add `targets/<id>/SKILL_NOTES.md` for target-specific grading guidance.
4. If this is a certification target, verify the current official credential name before writing.

## Register And Build

1. Register the target in `state/STUDY_STATE.yaml` under `targets`.
2. Set `active_target_id` if the learner wants to focus on this target.
3. Add trusted sources to `sources/SOURCE_INDEX.md`.
4. Build a conservative skill map in `state/SKILL_MAP.yaml`.
5. Set `NEXT_ACTIONS.md` to the first one-question action.
6. Run `python3 scripts/check_studydd.py`.
