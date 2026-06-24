# Inspect And Override State

StudyDD keeps your learning state in plain files so you can always audit, correct, or override the agent.

## How To Inspect The State

Open these files and folders:

- `state/STUDY_STATUS.md` — human-readable snapshot
- `state/STUDY_STATE.yaml` — structured current truth
- `state/SKILL_MAP.yaml` — skills, readiness, and confidence
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/STUDY_BACKLOG.md` — roadmap
- `targets/` — one folder per study target
- `reviews/REVIEW_QUEUE.md` — spaced repetition queue
- `sessions/SESSION_LOG.md` — session history
- `sources/SOURCE_INDEX.md` — trusted source registry
- `NEXT_ACTIONS.md` — immediate next step

You do not need to understand YAML deeply to read these files. The structure is meant to be readable.

## When To Override The Agent

Override the state when:

- the agent graded your answer incorrectly
- the agent forgot a skill you already demonstrated
- the agent inflated your readiness
- the agent misidentified a weak area
- the agent trusted the wrong source
- you want to change your study goal or deadline

## How To Override

1. Tell the agent what is wrong.
2. Ask it to update the relevant state files.
3. Require the agent to record the override in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md` with:
   - what was overridden
   - who requested it
   - why
   - the new value

Example:

> You marked "vector indexing" as weak, but I answered that correctly twice. Please update the skill map, add the override to the evidence log, and propose the next question.

## You Can Also Edit Files Directly

If you prefer, you can edit the state files directly. The agent will read your changes in the next session. Just keep the YAML structure valid.

## Nothing Is Hidden

The files are yours. The agent maintains them as a service, but the state belongs to the learner.
