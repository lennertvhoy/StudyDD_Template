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

## Answer-Position Randomization Rules

For multiple-choice, choose-two, choose-three, and matching-style questions:

1. **Create stable internal option IDs first.** Assign IDs like `opt_1`, `opt_2`, `opt_3`, `opt_4` to option content before any visible label exists. Mark which IDs are correct in the private answer key.
2. **Do not leak the private answer key before the learner answers.** The answer key may live in the agent's working context only. Do not write it to repo files, active question files, session logs, or evidence logs before grading.
3. **Shuffle visible options.** Assign shuffled visible labels (A, B, C, D) to the stable option IDs. Do not let the correct answer repeatedly be A, first, longest, most detailed, or most obviously worded.
4. **Verify the answer key after shuffling.** Confirm that the answer key points to the correct visible labels, not the original positions.
5. **Randomize choose-two/choose-three positions too.** Correct answers should not cluster as A+B or C+D.
6. **Keep distractors plausible.** Do not make wrong answers obviously weaker just because the correct option moved.
7. **Track recent answer positions.** For generated practice sets, avoid repeating the same label too often.
8. **Record the final order after grading.** The session/evidence log may include the final visible option order, correct visible label(s), learner answer, grading result, and optionally the internal option-ID mapping.

The learner should pass because they understand the concept, not because the template accidentally teaches answer-position habits.

## Option Randomization Checklist

Before presenting a fixed-option question, confirm:

- [ ] Stable internal option IDs are created before visible labels are assigned.
- [ ] Private answer key is defined before visible labels are assigned.
- [ ] Private answer key is not written to repo files before the learner answers.
- [ ] Options are shuffled randomly.
- [ ] Answer key is verified against the final visible labels.
- [ ] Correct answer is not always A, first, longest, or most detailed.
- [ ] For choose-two/choose-three, correct labels do not always cluster (e.g., A+B or C+D).
- [ ] Distractors remain plausible after shuffling.
- [ ] Recent practice-set history does not over-use the same correct label.
- [ ] After grading, session/evidence log records final option order, correct label(s), learner answer, result, and optional option-ID mapping.
