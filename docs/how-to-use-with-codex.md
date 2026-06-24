# How To Use StudyDD With Codex

## Setup

1. Clone or copy `StudyDD_Template` into a folder.
2. Open the folder in Codex.

## Start A Study Session

1. Open `PROMPTS/coding_agent_start_prompt.md`.
2. Copy the entire prompt.
3. Paste it into the Codex chat.
4. Ask Codex to initialize your copy.

Example:

```text
[paste the start prompt here]

Initialize this StudyDD copy for me. I want to prepare for a certification exam. Ask only the essential setup questions first.
```

## During The Session

- Answer one question at a time.
- If the agent's grading feels wrong, challenge it.
- Ask the agent to show you the active question ID and answer key after you answer if needed.

## End Of Session

- Let the agent propose state updates.
- Confirm or correct them.
- Ask the agent to run `python3 scripts/check_studydd.py`.
- Inspect `NEXT_ACTIONS.md` for the next study move.

## Tips

- Keep the whole repo in context so the agent can read and write state files.
- If Codex loses context, paste the start prompt again and ask it to re-read the required files in `AGENTS.md`.
- Use `PROMPTS/exam_drill_prompt.md` for realistic practice.
- Use `PROMPTS/reflection_prompt.md` after a tough session.
