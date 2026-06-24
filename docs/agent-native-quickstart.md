# Agent-Native Quickstart

StudyDD is easiest when you use it with a coding agent. You do not need to edit YAML by hand.

## What You Need

- A copy of this template.
- A coding-agent workflow such as Codex, Kimi Code, Claude Code, Cursor, OpenClaw, or similar.

## Steps

1. **Copy the template.**

   ```bash
   git clone https://github.com/lennertvhoy/StudyDD_Template.git
   cd StudyDD_Template
   ```

2. **Open the folder in your coding agent.**

3. **Copy the start prompt.**

   Open `PROMPTS/coding_agent_start_prompt.md` and paste the whole thing into the agent chat.

4. **Tell the agent to initialize your copy.**

   Example:

   > Initialize this StudyDD copy for me. I want to prepare for a certification exam. Ask me only the essential setup questions first.

5. **Let the agent build the first target.**

   It will read the contract, inspect state, ask only essential setup questions, create the first target folder, register trusted sources, build a conservative skill map, and set `NEXT_ACTIONS.md`.

6. **Answer one question at a time.**

7. **Review proposed state updates.**

   The agent will propose updates to the state files. Confirm or correct them.

8. **Run validation.**

   ```bash
   python3 scripts/check_studydd.py
   ```

## What The Agent Maintains

- `state/STUDY_STATE.yaml` — current truth
- `state/SKILL_MAP.yaml` — skills and readiness
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/STUDY_STATUS.md` — human-readable snapshot
- `targets/` — one folder per study target
- `reviews/REVIEW_QUEUE.md` — spaced repetition queue
- `sessions/SESSION_LOG.md` — session history
- `sources/SOURCE_INDEX.md` — trusted source registry
- `NEXT_ACTIONS.md` — what to do next

You can inspect these files whenever you want. They are plain Markdown and YAML.

## Next Steps

- Read `docs/studydd-principles.md` to understand the rules.
- Read `docs/inspect-and-override-state.md` to learn how to correct the agent.
- Read a platform guide such as `docs/how-to-use-with-codex.md` for workflow tips.
