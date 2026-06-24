# StudyDD — LinkedIn Product Blurb

Use this short text when sharing StudyDD publicly.

---

## Short version

**StudyDD** is a GitHub-template study system that turns a coding agent into a disciplined tutor, while the repo remains the source of truth.

Serious learning should have state.

StudyDD keeps skills, readiness, evidence, spaced-repetition reviews, and next actions in plain Markdown and YAML files — not inside a chat history or a proprietary database.

Run `python3 scripts/run_demo_replay.py` to watch the full learning loop happen in under a minute.

---

## Slightly longer version

Most AI tutors forget what you already know and inflate your confidence after one easy answer.

**StudyDD** fixes that by making learning state explicit and auditable. It is a GitHub template that turns a coding agent into a disciplined tutor:

- one question at a time
- honest grading against an answer key
- readiness backed by evidence, not encouragement
- spaced-repetition reviews recommended first
- overrides recorded without shame

Your progress lives in the repo: `state/`, `targets/`, `reviews/`, `sessions/`, `sources/`, and `NEXT_ACTIONS.md`.

Run `python3 scripts/run_demo_replay.py` to see the loop in action, or read `docs/demo-walkthrough.md` for a five-minute tour.
