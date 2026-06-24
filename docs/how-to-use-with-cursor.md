:computer_mouse: How to Use StudyDD with Cursor

## Setup

1. Clone or copy `StudyDD_Template` into a folder.
2. Open the folder in Cursor.

## Start a study session

1. Open `PROMPTS/coding_agent_start_prompt.md`.
2. Copy the entire prompt.
3. Paste it into Cursor's agent chat.
4. Add your study goal on a new line.

Example:

```text
[paste the start prompt here]

I am studying for Microsoft AI-103. Set up StudyDD for me and start a hard exam-style study session.
```

## During the session

- Answer one question at a time.
- If the agent's grading feels wrong, challenge it.
- Ask the agent to show you the active question ID and answer key if needed.

## End of session

- Let the agent propose state updates.
- Confirm or correct them.
- Ask the agent to read `docs/inspect-and-override-state.md` if you want to audit the state.

## Tips

- Cursor's agent can read and write the state files. Let it maintain them.
- If agent context resets, re-paste the start prompt.
- Use `PROMPTS/exam_drill_prompt.md` for realistic practice.
- Use `PROMPTS/reflection_prompt.md` after a session.
