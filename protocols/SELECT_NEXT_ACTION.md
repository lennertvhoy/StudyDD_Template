# SELECT_NEXT_ACTION — Choose The One Next Study Action

> **Agent action.** Use this protocol to pick exactly one next study action.

## Selection Priority

Choose the first item that applies:

1. **Due review item** — a review in `reviews/REVIEW_QUEUE.md` with due date `<= today`.
2. **Blocked skill** — a skill in `state/SKILL_MAP.yaml` with status `blocked`.
3. **Weak skill with fresh evidence** — a `weak` skill that has not been re-tested since the last failure.
4. **Pending skill near the active focus** — a `pending` skill related to the current target.
5. **Practiced skill needing varied evidence** — a `practiced` skill that has only one correct answer on record.
6. **Confirmed skill needing maintenance** — only in mixed checkpoint sessions or when other items are exhausted.

## Match Session Mode

- **Deep mode** — pick the hardest due review, weak area, or a mixed checkpoint.
- **Normal mode** — pick one strong question from the highest priority item.
- **Low-energy mode** — pick one due review or a small recall/prompt question.
- **Recovery mode** — pick one concept to read or explain; no question required.

## Write To NEXT_ACTIONS.md

`NEXT_ACTIONS.md` must contain exactly one clear current next action. Move the previous current action to either:

- **Pending actions** if not done, or
- **Recently completed** with a date if done.

## What The Action Must Specify

- target ID
- skill ID
- question ID or review ID
- question type (recall, apply, troubleshoot, choose-best, explain, design)
- mode (deep, normal, low-energy, recovery)
- why this action was chosen
