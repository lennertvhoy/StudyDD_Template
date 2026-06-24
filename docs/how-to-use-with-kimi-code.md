# How to Use StudyDD with Kimi Code

## Setup

1. Clone or copy `StudyDD_Template` into a folder.
2. Open the folder in Kimi Code.

## Start a study session

1. Open `PROMPTS/coding_agent_start_prompt.md`.
2. Copy the entire prompt.
3. Paste it into the Kimi Code chat.
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
- Ask the agent to run `docs/inspect-and-override-state.md` checks if you want to audit the state.

## Tips

- Kimi Code can read and edit the state files directly. Let it.
- If context resets, re-paste the start prompt.
- Use `PROMPTS/exam_drill_prompt.md` before an exam.
- Use `PROMPTS/reflection_prompt.md` to capture what still feels uncertain.
