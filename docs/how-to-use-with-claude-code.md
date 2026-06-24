# How to Use StudyDD with Claude Code

## Setup

1. Clone or copy `StudyDD_Template` into a folder.
2. Open the folder in Claude Code.

## Start a study session

1. Open `PROMPTS/coding_agent_start_prompt.md`.
2. Copy the entire prompt.
3. Paste it into Claude Code.
4. Add your study goal on a new line.

Example:

```text
[paste the start prompt here]

I am studying for a product scenario practice. Set up StudyDD and start a behavioral + system design rehearsal.
```

## During the session

- Answer one question at a time.
- If the agent's grading feels wrong, challenge it.
- Ask the agent to show you the active question ID and answer key if needed.

## End of session

- Let the agent propose state updates.
- Confirm or correct them.
- Ask the agent to re-read `state/SKILL_MAP.yaml` if you want to audit weak areas.

## Tips

- Claude Code can edit the state files directly. Let it.
- If context resets, re-paste the start prompt.
- Use `PROMPTS/interview_prep_prompt.md` for interview-specific practice.
- Use `PROMPTS/reflection_prompt.md` after a tough session.
