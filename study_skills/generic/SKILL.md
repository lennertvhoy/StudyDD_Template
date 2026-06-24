# StudyDD Skill: Generic

## Use when

No domain-specific study skill is declared for the active target, or the target type is not covered by a specialized skill.

## Learning goal shape

Build concrete, evidenced skill across a mix of recall, application, and transfer questions. Readiness grows only from demonstrated answers, not from reading or encouragement.

## What good tutoring looks like

- Ask one question at a time.
- Define the answer key internally before the learner answers.
- Grade the actual answer, not the intended answer.
- Give immediate, plain-language feedback.
- Record evidence honestly after every answer.
- Schedule review for weak, partial, repaired, or shaky answers.
- Update readiness conservatively.

## Question types to prefer

- Explain questions that require a short paragraph.
- Apply questions that place a concept in a concrete scenario.
- Choose-best questions with plausible distractors.
- Troubleshooting questions that require diagnosis before action.

## Question types to avoid

- Trivia-only questions that do not test transfer.
- Multiple questions in one turn.
- Obvious or keyword-only questions.
- Questions that reveal the answer key before the learner answers.

## Grading policy

- **correct** — fully meets the answer key.
- **partial** — partly correct but missing something important.
- **incorrect** — does not meet the answer key.
- **unclear** — cannot be graded because the answer is ambiguous.

Tag mistake types from `protocols/MISTAKE_TAXONOMY.md` when the answer is not fully correct.

## Evidence policy

One evidence item per question. Each item must link to a target, skill, question, verdict, and confidence. Weak or repaired answers must produce review items.

## Spaced repetition policy

Use `scripts/schedule_review.py` for weak, partial, or repaired answers. First interval after a weak answer: 1 day. Correct recall: double the interval, capped by target deadline or 30 days. Lapse: reset to 1 day and increment lapse count.

## Readiness upgrade rules

- A single correct answer moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- A partial answer stays `weak` or low `practiced`.
- An incorrect answer marks the skill `weak`.
- `confirmed` requires strong or varied evidence.
- To move above 70, require at least two correct answers across varied question types or scenarios.

## Common learner failure modes

- Vague answers that restate the question.
- Keyword traps where the learner names a concept without explaining it.
- Overconfident guesses on choose-best questions.
- Correct concept but weak implementation detail.

## Agent instructions

1. Load the active target and its declared study skill.
2. If no skill is declared, load this generic skill.
3. Build a context pack with `--task start_session`.
4. Ask exactly one question, grade honestly, record evidence, schedule review if needed, and update state conservatively.
5. Run `python3 scripts/check_studydd.py` after state changes.

## Example next action

Review the weakest skill before introducing a new topic; ask one varied question to gather stronger evidence.

## Activity orchestration fallback

When no specialized skill applies, the agent still uses `protocols/LEARNING_ACTIVITY_POLICY.md` to choose the best next move. A question is the default fallback, but the agent may assign a paper exercise, explain-back task, video, external resource, or upload-and-review task when evidence shows that format is better. Always state expected evidence and end with: `You can accept, modify, or override this.`

## Source freshness and learner adaptation

- This generic skill covers stable knowledge by default. For moderate/volatile/live topics, use `scripts/check_source_freshness.py` and `sources/SOURCE_STATE.yaml` before authoritative questions.
- Prefer `authoritative_current` questions only when fresh official or high-authority sources exist.
- For stable concepts, `conceptual_practice` is acceptable without source refresh.
- Adapt question style and activity type from learner evidence, not preference alone.
