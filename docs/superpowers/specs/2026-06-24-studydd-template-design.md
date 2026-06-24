# StudyDD_Template v0.1 Design

**Status:** Approved. Built as agent-native documentation template.

**Goal:** Create an open-source educational state template that lets a coding agent act as a long-term study copilot. The agent maintains plain Markdown/YAML state files; the learner talks to the agent and can inspect or override the files at any time.

## Product framing

StudyDD_Template applies StateDD principles to learning, certification prep, interview prep, and skill development. It is not a CLI app, web app, or manual YAML editor for users. It is an agent-native workflow.

## Two surfaces

- **User surface:** README.md and `docs/*` — written for the human learner.
- **Agent surface:** `state/`, `protocols/`, `PROMPTS/`, `EXAMPLES/` — read and maintained by the coding agent.

## File structure

```text
StudyDD_Template/
  README.md
  LICENSE.md
  docs/
    agent-native-quickstart.md
    how-to-use-with-codex.md
    how-to-use-with-kimi-code.md
    studydd-principles.md
    inspect-and-override-state.md
  AGENTS.md
  state/
    STUDY_STATUS.md
    STUDY_STATE.yaml
    NEXT_STUDY_ACTIONS.md
    STUDY_BACKLOG.md
    SESSION_LOG.md
    EVIDENCE_LOG.md
    SKILL_MAP.yaml
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
  EXAMPLES/
    ai-103-example/
      state/
        STUDY_STATUS.md
        STUDY_STATE.yaml
        NEXT_STUDY_ACTIONS.md
        SKILL_MAP.yaml
        SESSION_LOG_EXAMPLE.md
```

## Core UX

1. Clone or copy the template.
2. Open it in a coding agent (Codex, Kimi Code, Claude Code, Cursor, etc.).
3. Paste the prompt from `PROMPTS/coding_agent_start_prompt.md`.
4. Tell the agent your study goal.
5. The agent reads `AGENTS.md`, initializes or updates state, asks minimal setup questions, runs study sessions, records evidence, updates weak areas and next actions, and avoids readiness inflation.

## Validation

- YAML parses.
- Required files exist.
- No heavy app, CLI, database, or web app.

## License

Custom permissive license: free for study and commercial use; author reserves the right to use the work in teaching, sessions, webinars, etc.
