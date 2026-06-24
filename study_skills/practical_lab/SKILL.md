# StudyDD Skill: Practical Lab

## Use when

The active target is hands-on: command-line tools, system administration, networking, hardware, experiments, or any skill learned by doing.

## Learning goal shape

The learner should be able to perform or explain a process in a new context. Evidence includes commands run, observations, log excerpts, and cause/effect reasoning.

## What good tutoring looks like

- Use hands-on tasks and troubleshooting questions.
- Ask "what would you check next?" often.
- Grade process, not only final answer.
- Encourage the learner to predict what a command or change will do before executing.
- Connect observations to underlying cause/effect.

## Question types to prefer

- "What command would you run and what output do you expect?"
- "What would you check next?" troubleshooting sequences.
- Configuration reasoning: "Why set this value?"
- Log interpretation questions.
- "Explain the cause and effect of this failure."
- Hands-on tasks with expected observations.

## Question types to avoid

- Theory-only questions that do not connect to action.
- Questions that ask for memorized commands without context.
- Skipping safety or rollback steps.

## Grading policy

Grade process and reasoning, not just the final answer.

- **correct** — right command/sequence with correct reasoning and safety awareness.
- **partial** — right direction but missing a step, check, or safety consideration.
- **incorrect** — wrong command, wrong order, or dangerous action.
- **unclear** — cannot tell what the learner would do.

Tag mistake types such as `missed-constraint`, `ignored-monitoring`, `service-boundary-confusion`, and `correct-concept-weak-implementation`.

## Evidence policy

Evidence should include:

- commands run or proposed
- observations made
- log excerpts or screenshots when available
- explanation of cause/effect

Record whether the learner actually performed the step or only explained it.

## Spaced repetition policy

Revisit:

- failed procedures
- fragile steps
- commands that were misremembered
- troubleshooting paths that were wrong

Use review modes: troubleshoot, explain, scenario.

## Readiness upgrade rules

- A single correct explanation moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- To move above 70, demonstrate the process across varied scenarios.
- To move above 80, perform or explain the process under realistic constraints or time pressure.
- High readiness requires doing or explaining the process in a new context, not just recalling the steps.

## Source freshness and learner adaptation

- Labs often involve volatile/current tools, cloud consoles, or product versions. Before authoritative product-current questions, run `scripts/check_source_freshness.py`.
- Use screenshots, command output, and lab logs as evidence.
- Adapt lab difficulty from recent mistakes, not preference alone.

## Common learner failure modes

- `missed-constraint` — ignores permissions, environment, or prerequisites.
- `ignored-monitoring` — forgets to check logs or metrics.
- `service-boundary-confusion` — checks the wrong component.
- `correct-concept-weak-implementation` — knows the idea but proposes an unsafe or incomplete command.

## Agent instructions

1. Load the active target and any lab environment notes.
2. Build the context pack with `--task start_session`.
3. Ask one hands-on or troubleshooting question at a time.
4. Ask the learner to predict outcomes before revealing results.
5. Grade process and reasoning, not just final answers.
6. Record evidence with commands, observations, and cause/effect notes.
7. Schedule review for failed or fragile procedures.

## Example next action

Present a symptom and ask what the learner would check first, second, and third; then explain what each check would reveal.
