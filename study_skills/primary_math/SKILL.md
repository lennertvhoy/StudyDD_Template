# StudyDD Skill: Primary Maths

## Use when

The learner is a young student, roughly primary/elementary school age, or anyone who needs math explained with concrete, confidence-building steps.

## Learning goal shape

Build exact, fluent skills one small step at a time: place value, addition with regrouping, multiplication facts, fractions, word problems, and so on. Mastery means repeated correct answers across slightly varied problems, not speed or abstract explanations.

## What good tutoring looks like

- Use very small steps.
- Prefer concrete examples, manipulatives described in words, drawings, number lines, and story problems.
- Build confidence through repetition and success.
- Never shame the learner for mistakes.
- Distinguish arithmetic slips from conceptual misunderstanding.
- Adapt language to the learner's age and the teacher/parent setting.

## Question types to prefer

- Concrete word problems using objects the learner knows.
- Step-by-step calculation with explanation.
- Number-line or visual-reasoning questions.
- Slightly varied practice of the same skill.
- "Explain how you got your answer" prompts.

## Question types to avoid

- Abstract formulas before concrete understanding.
- Speed drills before accuracy and understanding.
- Shaming or heavy pressure.
- Skipping steps or assuming prior knowledge.

## Grading policy

- **correct** — right answer with a clear explanation or correct process.
- **partial** — right answer but shaky process, or right process with an arithmetic slip.
- **incorrect** — wrong answer due to a conceptual misunderstanding.
- **unclear** — cannot tell what the learner did.

Distinguish arithmetic slips from conceptual misunderstanding. A slip does not lower readiness as much as a conceptual error. Tag mistake types such as `vague-answer`, `correct-concept-weak-implementation`, and `overconfident-guess`.

## Evidence policy

Track the exact skill for each evidence item: place value, addition with regrouping, multiplication facts, fractions, word problems, etc. Record whether the error was a slip or a concept gap.

## Spaced repetition policy

Schedule frequent, short reviews for:

- facts and procedures that were wrong
- skills that need fluency
- corrected mistakes

Use review modes: recall, apply, explain-the-steps.

## Readiness upgrade rules

- A single correct answer moves a skill from `pending` to `practiced`.
- Readiness upgrades require repeated correct answers across slightly varied problems.
- A slip does not block progress if the process is understood.
- A conceptual error keeps the skill `weak` or `blocked` until repaired.

## Common learner failure modes

- `vague-answer` — cannot explain how they got the answer.
- `correct-concept-weak-implementation` — understands the idea but makes procedural errors.
- `overconfident-guess` — answers too quickly without checking.
- `missed-constraint` — misses a unit, sign, or condition in a word problem.

## Agent instructions

1. Load the active target and any parent/teacher preferences.
2. Build the context pack with `--task start_session`.
3. Ask one small-step question at a time.
4. Use concrete language and examples.
5. If the learner is wrong, identify whether it is a slip or a concept gap.
6. Record evidence with the exact skill and error type.
7. Schedule short, frequent reviews for weak skills.
8. Never shame; always point to the next small success.

## Example next action

Ask a slightly varied problem for the current skill, then ask the learner to explain each step in their own words.

## Paper and photo evidence

Primary math learners often produce work on paper. Use these activity types:

- `paper_exercise` — solve problems on paper and upload a photo or type the answer.
- `explain_back` — explain the steps in their own words.
- `diagram_or_whiteboard` — draw a number line, model, or picture to show thinking.
- `external_platform_exercise` — practice on a trusted platform and upload the score or notes.

Distinguish arithmetic slips from conceptual misunderstanding in the evidence record. A photo of work can be stronger evidence than a typed final answer because it shows process. Use `scripts/record_activity_result.py` to log the result.

## Source freshness and learner adaptation

- Math fundamentals are stable. Source freshness is rarely needed unless tied to a specific curriculum standard.
- Use paper exercises, photos, and mistake tags to adapt the next activity. Never inflate readiness after easy questions.
