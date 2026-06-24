# Agent-Native Quickstart

StudyDD is easiest when you use it with a coding agent. You do not need to edit YAML by hand.

## What you need

- A copy of this template.
- A coding-agent workflow such as Codex, Kimi Code, Claude Code, Cursor, or OpenClaw.

## Steps

1. **Copy the template.**

   ```bash
   git clone https://github.com/lennertvhoy/StudyDD_Template.git
   cd StudyDD_Template
   ```

2. **Open the folder in your coding agent.**

3. **Copy the start prompt.**

   Open `PROMPTS/coding_agent_start_prompt.md` and paste the whole thing into the agent chat.

4. **Tell the agent your goal.**

   Example:

   > I am studying for Microsoft AI-103. Set up StudyDD for me and start a hard exam-style study session.

5. **Let the agent work.**

   It will read the contract, inspect state, ask only essential setup questions, initialize files, and start the session.

6. **Answer one question at a time.**

7. **Review proposed state updates.**

   The agent will propose updates to the state files. Confirm or correct them.

## What the agent maintains

- `state/STUDY_STATE.yaml` — current truth
- `state/SKILL_MAP.yaml` — skills and readiness
- `state/SESSION_LOG.md` — session history
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/NEXT_STUDY_ACTIONS.md` — what to do next
- `state/STUDY_STATUS.md` — human-readable snapshot

You can inspect these files whenever you want. They are plain Markdown and YAML.

## Next steps

- Read `docs/studydd-principles.md` to understand the ideas.
- Read `docs/inspect-and-override-state.md` to learn how to correct the agent.
- Read `docs/how-to-use-with-codex.md` or `docs/how-to-use-with-kimi-code.md` for platform-specific tips.
