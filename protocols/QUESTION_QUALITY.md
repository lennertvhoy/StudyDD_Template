# QUESTION_QUALITY — Question Design Gate

> **Agent rule.** Every question must be designed before it is asked.

## Internal Question Plan

Before asking, the agent must internally define:

- **target ID** — which target this belongs to
- **skill ID** — which skill this tests
- **objective** — exactly what the question measures
- **cognitive level** — recall / apply / troubleshoot / choose-best / explain / design
- **difficulty** — 1 (easy) to 5 (hard)
- **answer key** — required concepts, acceptable synonyms, threshold for correctness
- **common traps** — plausible wrong answers or misconceptions
- **grading rubric** — what earns correct / partial / incorrect
- **source reference** — which trusted source backs the question
- **readiness impact** — whether this question can change readiness

The learner must not see the answer key before answering.

## Cognitive Levels

- **recall** — definition, fact, list, parameter, command.
- **apply** — use a concept in a concrete scenario.
- **troubleshoot** — diagnose and fix a problem.
- **choose-best** — select the best option among plausible distractors.
- **explain** — describe why or how something works.
- **design** — propose a solution and justify tradeoffs.

## Quality Rules

- No obvious answer patterns (e.g., always choosing the longest option).
- No keyword-only questions for serious readiness claims.
- Plausible distractors for choose-best questions.
- Microsoft-style ambiguity where appropriate: more than one option may seem reasonable, but one is clearly best.
- Scenario-first for certification and interview targets.
- Mixed checkpoints for readiness above 80.
- Match difficulty to current readiness; avoid questions that are too easy or impossibly hard.

## What Affects Readiness

Only questions at apply level or above should meaningfully increase readiness above `practiced`.
Definition-only questions can confirm exposure, not mastery.
