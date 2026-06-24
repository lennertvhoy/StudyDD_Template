# StudyDD_Template v0.3 Design

**Status:** Approved direction. Public template, single happy path.

**Goal:** Create an open-source educational state template that lets a coding agent turn any repo directory into a personal study second brain. The agent maintains plain Markdown/YAML files; the learner talks to the agent and can inspect or override the files at any time.

## Product Framing

StudyDD_Template applies StateDD principles to learning, certification prep, interview prep, and skill development. It is not a CLI app, web app, database, or architecture chooser. It is an agent-native workflow.

The promise:

> Give this repo to a coding agent, tell it who you are and what you want to learn, and it turns the directory into your personal study library, tutor memory, readiness tracker, spaced-repetition queue, and next-action engine.

## Happy Path

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

## File Structure

```text
StudyDD_Template/
  README.md
  LICENSE.md
  AGENTS.md
  NEXT_ACTIONS.md
  state/
    STUDY_STATUS.md
    STUDY_STATE.yaml
    STUDY_BACKLOG.md
    EVIDENCE_LOG.md
    SKILL_MAP.yaml
  targets/
    README.md
  reviews/
    README.md
    REVIEW_QUEUE.md
  sessions/
    README.md
    SESSION_LOG.md
  sources/
    README.md
    SOURCE_INDEX.md
  protocols/
    TUTOR_PROTOCOL.md
    SESSION_TEMPLATE.md
  PROMPTS/
    coding_agent_start_prompt.md
    ai_tutor_prompt.md
    study_session_prompt.md
    exam_drill_prompt.md
    reflection_prompt.md
    update_state_prompt.md
    interview_prep_prompt.md
  scripts/
    check_studydd.py
  docs/
  EXAMPLES/
```

## Core UX

1. Clone or copy the template.
2. Open it in a coding agent.
3. Paste the prompt from `PROMPTS/coding_agent_start_prompt.md`.
4. Ask the agent to initialize this copy for the learner's target.
5. The agent reads `AGENTS.md`, initializes or updates state, asks minimal setup questions, creates target/source/review/session surfaces, runs one-question-at-a-time tutoring, records evidence, updates weak areas and next actions, and avoids readiness inflation.

## Validation

- Required files exist.
- Required directories exist.
- YAML parses.
- Required YAML keys are present.
- Target folders, when created, include `TARGET.yaml`.
- No heavy app, CLI, database, or web framework is required.

## Add-On Backlog

- `addon-telegram-study-bot`: daily review prompt, answer capture, reminders, low-energy study mode.
- `addon-containerized-studydd`: Docker, Podman, devcontainer, or compose setup for portable local execution.

## Public Template Rule

The root template state remains generic until a learner explicitly asks to initialize their copy. Example states live under `EXAMPLES/` and must not become root defaults.
