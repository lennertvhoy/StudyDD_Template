# StudyDD_Template

**One simple happy-path study system for coding agents.**

StudyDD turns a plain repo directory into a personal study second brain. Give the repo to a coding agent, tell it who you are and what you want to learn, and it maintains your study library, tutor memory, readiness tracker, spaced-repetition queue, source registry, and next-action engine.

The files stay plain, inspectable, and editable. Your progress is never hidden inside an app database or chat history.

## The Promise

> Give this repo to a coding agent, tell it who you are and what you want to learn, and it turns the directory into your personal study library, tutor memory, readiness tracker, spaced-repetition queue, and next-action engine.

## Why This Exists

AI tutors and coding agents are useful study companions, but they often:

- forget what you already know
- inflate readiness after one easy answer
- lose track of weak areas
- grade against the answer they expected instead of what you actually said
- drift into generic encouragement instead of exam-style challenge
- make mistakes and never update the learning state

StudyDD fixes this by making learning state explicit, evidence-based, and auditable.

## The Happy Path

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

There is no architecture menu in the core template. The default path is intentionally boring and powerful.

## Folder Model

- `state/` — current learner truth
- `targets/` — one folder per study, certification, interview, or skill target
- `reviews/` — spaced repetition queues
- `sessions/` — tutor session logs and SkillSignal update packets
- `sources/` — trusted source tracking
- `scripts/check_studydd.py` — repo sanity gate
- `NEXT_ACTIONS.md` — the single next best study action
- `AGENTS.md` — how coding and tutor agents must behave
- `protocols/` — tutor and session rules
- `PROMPTS/` — reusable prompts for coding agents and tutors
- `EXAMPLES/` — reference states only, not defaults

## Quick Start

1. Clone or copy this template into your own folder.

```bash
git clone https://github.com/lennertvhoy/StudyDD_Template.git
cd StudyDD_Template
```

2. Open the folder in your coding agent.
3. Paste `PROMPTS/coding_agent_start_prompt.md` into the agent chat.
4. Tell the agent what you want to learn.

Example:

> Initialize this StudyDD copy for me. I want to prepare for a certification exam. Ask me only the essential setup questions first.

The agent will read `AGENTS.md`, inspect the current state, initialize the learner profile and first target, build a conservative skill map from trusted sources, and set the first next action.

## What The Agent Maintains

- `state/STUDY_STATUS.md` — short human-readable snapshot
- `state/STUDY_STATE.yaml` — structured current truth
- `state/SKILL_MAP.yaml` — skills with readiness and confidence
- `state/EVIDENCE_LOG.md` — demonstrated evidence
- `state/STUDY_BACKLOG.md` — strategic backlog
- `targets/` — target-specific files
- `reviews/REVIEW_QUEUE.md` — spaced repetition queue
- `sessions/SESSION_LOG.md` — session history
- `sessions/SKILLSIGNAL_PACKETS.md` — proposed skill updates
- `sources/SOURCE_INDEX.md` — trusted source registry
- `NEXT_ACTIONS.md` — immediate next step

You can inspect or override any of these files. They are plain Markdown and YAML.

## Validation

Run the sanity gate after setup or state changes:

```bash
python3 scripts/check_studydd.py
```

The validator checks required files, parses YAML when PyYAML is available, and verifies the happy-path folder structure.

## Source And Readiness Discipline

Readiness is earned through demonstrated answers, not through source coverage or encouragement.

- A new skill starts as `pending`.
- One good answer can make a skill `practiced`, not `confirmed`.
- Weak and repaired answers go into `reviews/REVIEW_QUEUE.md`.
- Confirmed status requires strong or varied evidence.
- Official and authoritative sources come first. Old spreadsheets, exports, notes, blogs, and generated summaries are secondary until verified.

## Examples

- `EXAMPLES/ai-103-example/` — reference certification study state.
- `EXAMPLES/product-engineer-interview-example/` — reference interview prep state.

Examples show how maintained state can look after sessions. They are not the root template's default learner or target.

## Future Add-Ons

These are intentionally backlog items, not part of the core slice:

- `addon-telegram-study-bot` — daily review prompt, answer capture, reminders, low-energy study mode.
- `addon-containerized-studydd` — Docker, Podman, devcontainer, or compose setup for portable local execution.

## License

This project is licensed under the MIT License. See `LICENSE.md` for the full text.

## Status

v0.3 — public template with one happy path, target/review/session/source surfaces, conservative readiness rules, and validation-backed agent workflow.
