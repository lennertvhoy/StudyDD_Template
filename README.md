# StudyDD_Template

**Agent-native educational state template.**

StudyDD applies [StateDD](https://github.com/lennertvhoy/StateDD_Template) principles to learning, certification prep, interview prep, and skill development.

You talk to a coding agent. The agent maintains the study state. The state stays plain, inspectable, and editable — so your learning progress is never hidden inside a black box.

## The problem

AI tutors and coding agents are useful study companions, but they often:

- forget what you already know
- inflate your readiness after one easy answer
- lose track of weak areas
- grade against the answer they expected instead of what you actually said
- drift into generic encouragement instead of exam-style challenge
- make mistakes and never update the learning state

StudyDD fixes this by making your learning state explicit, evidence-based, and auditable.

## What StudyDD gives you

The same structure serious projects have, applied to your study journey:

- **current state** — what you are studying, what you know, and what is still weak
- **evidence log** — proof of what you have actually demonstrated
- **session log** — record of each study session
- **backlog** — topics and skills still to cover
- **next actions** — the next best study move
- **tutor protocol** — rules for asking, grading, and repairing questions
- **skill map** — tracked competencies with readiness and confidence
- **correction history** — where the tutor or agent made a mistake and how it was fixed

## How to start

StudyDD is designed for **coding-agent workflows**: Codex, Kimi Code, Claude Code, Cursor, OpenClaw, or similar.

### Quick start

1. Clone or copy this template into your own folder.

```bash
git clone https://github.com/lennertvhoy/StudyDD_Template.git
cd StudyDD_Template
```

2. Open the folder in your coding agent.
3. Open `PROMPTS/coding_agent_start_prompt.md` and paste it into the agent chat.
4. Tell the agent what you are studying.

Example:

> I am studying for Microsoft AI-103. Set up StudyDD for me and start a hard exam-style study session.

The agent will:

- read `AGENTS.md`
- inspect existing state
- ask only essential setup questions
- initialize missing state files
- run one study question at a time
- grade your actual answer
- record evidence
- update weak areas and next actions
- avoid inflating your readiness
- preserve any human override you give
- end with a clear next action

## Two surfaces

### User surface — what the human touches

These files are written for you:

- `README.md` — this file
- `docs/agent-native-quickstart.md` — fastest path to your first session
- `docs/how-to-use-with-codex.md`
- `docs/how-to-use-with-kimi-code.md`
- `docs/how-to-use-with-claude-code.md`
- `docs/how-to-use-with-cursor.md`
- `docs/studydd-principles.md` — the ideas behind StudyDD
- `docs/inspect-and-override-state.md` — how to audit or correct the agent

Your normal workflow is the coding-agent chat plus these docs.

### Agent surface — what the agent maintains

These files are the transparent project memory the agent reads and updates:

- `AGENTS.md` — agent behavior contract
- `state/STUDY_STATUS.md` — short human-readable snapshot
- `state/STUDY_STATE.yaml` — structured current truth
- `state/NEXT_STUDY_ACTIONS.md` — active queue
- `state/STUDY_BACKLOG.md` — roadmap and backlog
- `state/SESSION_LOG.md` — session history
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/SKILL_MAP.yaml` — skills with readiness and confidence
- `protocols/TUTOR_PROTOCOL.md` — ask/grade/repair rules
- `protocols/SESSION_TEMPLATE.md` — session structure
- `PROMPTS/*.md` — copy-paste prompts for agents and tutors
- `PROMPTS/interview_prep_prompt.md` — interview-specific rehearsal
- `EXAMPLES/ai-103-example/` — a concrete certification example

You are always allowed to inspect, edit, or override these files. They are plain Markdown and YAML. The default workflow, however, is that the agent maintains them for you.

## You can always inspect the state

Nothing is hidden. If you want to know why the agent thinks you are weak on a topic, read `state/SKILL_MAP.yaml` and `state/EVIDENCE_LOG.md`. If the agent misgrades an answer or makes a mistake, correct it and the agent must update the state rather than hide the error.

## Who it is for

- certification prep
- exam study
- professional upskilling
- interview preparation
- course design
- self-study with AI tutors
- teacher or trainer-guided learning paths

## How it relates to StateDD

[StateDD](https://github.com/lennertvhoy/StateDD_Template) treats a software project as something with explicit, inspectable state: current truth, backlog, next actions, evidence, and handoff discipline.

StudyDD applies the same idea to education. Your study journey becomes a project the agent can maintain, audit, improve, and hand off between human learner, tutor AI, coding agent, teacher, coach, or mentor.

## Examples

- `EXAMPLES/ai-103-example/` — a realistic Microsoft AI-103 certification study state.

Both show how skills, evidence, session history, and next actions look once the agent has maintained them for a few sessions.

## License

This project is licensed under the MIT License. See `LICENSE.md` for the full text.

## Status

v0.2 — agent-native template with AI-103 and product scenario practice examples, expanded agent guidance, and stronger validation.
