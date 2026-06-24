# StudyDD Skill: Language Learning

## Use when

The active target is learning a new language, refreshing a language, or mastering vocabulary/grammar/pronunciation for communication.

## Learning goal shape

The learner should be able to produce the language, not just recognize it. Track vocabulary, grammar patterns, pronunciation notes, and common interference errors. Readiness upgrades require production, not just recognition.

## What good tutoring looks like

- Prefer active recall and sentence production over multiple-choice recognition.
- Correct with minimal embarrassment.
- Use grammar in context, not isolated rules.
- Separate communicative success from grammar accuracy.
- Encourage the learner to speak or write full sentences.

## Question types to prefer

- Active recall: "Say the word for X."
- Sentence production: "Answer this question in a full sentence."
- Listening/reading comprehension prompts.
- Grammar in context: "Fill in the blank in this sentence."
- Spaced vocabulary review.
- Correction of learner-produced sentences.

## Question types to avoid

- Pure translation drills that ignore context.
- Questions that only test recognition, not production.
- Embarrassing corrections in front of others.
- Overloading the learner with too many new items at once.

## Grading policy

Grade communicative success separately from grammar accuracy.

- **correct** — communicates the meaning accurately and grammatically.
- **partial** — meaning is clear but has grammar or vocabulary errors.
- **incorrect** — meaning is unclear or wrong.
- **unclear** — cannot understand the learner's attempt.

Tag mistake types such as `vague-answer`, `memorized-wording-without-transfer`, and `source-confusion` (e.g., false friends between languages).

## Evidence policy

Track:

- vocabulary items
- grammar patterns
- pronunciation notes
- common interference errors from the learner's native language

Record production evidence, not just recognition.

## Spaced repetition policy

Strongly apply spaced repetition to:

- vocabulary and phrases
- irregular forms
- corrected mistakes
- items the learner almost knew

Use review modes: recall, sentence production, comprehension.

## Readiness upgrade rules

- A single correct production moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- To move above 70, demonstrate production across varied contexts.
- To move above 80, hold up in mixed-skill conversation or writing.
- Recognition-only evidence does not justify high readiness.

## Common learner failure modes

- `memorized-wording-without-transfer` — can repeat a phrase but cannot adapt it.
- `source-confusion` — false friends or interference from another language.
- `vague-answer` — avoids full sentences.
- `overconfident-guess` — answers without checking gender, tense, or register.

## Agent instructions

1. Load the active target and the learner's known languages if available.
2. Build the context pack with `--task start_session`.
3. Ask one recall or production question at a time.
4. Correct gently and explicitly.
5. Record evidence with vocabulary/grammar/pattern tags.
6. Schedule frequent reviews for weak or corrected items.
7. Update readiness based on production, not recognition.

## Example next action

Review five due vocabulary items with active recall, then ask the learner to produce one original sentence using a new grammar pattern.

## Source freshness and learner adaptation

- Language content is generally stable, but exam objectives or proficiency standards can change. Use `source_ids` for official curriculum objectives.
- Adapt exercise types (listening, speaking, writing, grammar) from evidence of weak areas.
