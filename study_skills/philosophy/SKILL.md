# StudyDD Skill: Philosophy

## Use when

The active target is philosophy, critical thinking, ethics, political theory, or any domain centered on arguments, concepts, and primary texts.

## Learning goal shape

The learner should be able to reconstruct arguments, distinguish concepts, interpret primary texts charitably, compare thinkers, and produce objections and replies. Mastery is transfer: can the learner apply a concept to a new passage or problem?

## What good tutoring looks like

- Ask the learner to explain an argument before criticizing it.
- Steelman positions before attacking them.
- Reward clarity, charity, and conceptual precision.
- Encourage outline-style answers for complex questions.
- Keep the focus on reasoning, not memorized names or dates.

## Question types to prefer

- Argument reconstruction: "State the argument in numbered premises."
- Concept distinction: "How does X differ from Y?"
- Primary-text interpretation: "What does this passage mean, and what argument does it support?"
- Comparison between thinkers: "How would A reply to B?"
- Objection/reply: "Give the strongest objection to this argument and a possible reply."
- Essay outlines: "Outline a short essay defending or criticizing this claim."

## Question types to avoid

- Trivia-only questions (dates, names without reasoning).
- Questions that treat philosophy as a vocabulary list.
- Leading questions that give away the answer.

## Grading policy

Reward clarity, charity, and conceptual precision.

- **correct** — accurately reconstructs or applies the argument/concept.
- **partial** — right direction but misses a premise, distinction, or nuance.
- **incorrect** — misrepresents the argument or confuses concepts.
- **unclear** — answer is too vague to grade.

Tag mistake types such as `vague-answer`, `source-confusion`, `memorized-wording-without-transfer`, and `correct-concept-weak-implementation`.

## Evidence policy

Evidence can be based on textual interpretation, argument maps, and written answers. Record the learner's ability to reconstruct arguments and apply concepts, not just name them.

## Spaced repetition policy

Schedule reviews for:

- concept distinctions
- named arguments
- thinker comparisons
- common misinterpretations

Use review modes: explain, compare, apply-to-new-passage.

## Readiness upgrade rules

- A single correct reconstruction moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- To move above 70, demonstrate the concept across varied passages or problems.
- To move above 80, perform well in mixed-topic checkpoint sessions.
- High readiness requires transfer: applying a concept to a new text or problem without hints.

## Common learner failure modes

- `vague-answer` — hand-wavy summary instead of precise reconstruction.
- `source-confusion` — attributing a view to the wrong thinker.
- `memorized-wording-without-transfer` — repeating a definition but unable to apply it.
- `correct-concept-weak-implementation` — names the distinction but cannot use it in an argument.

## Agent instructions

1. Load the active target and any primary-text or source list.
2. Build the context pack with `--task start_session`.
3. Before asking, define the argument or concept to be tested.
4. Ask one question at a time; prefer reconstruction before criticism.
5. Grade for clarity, charity, and precision.
6. Record evidence and schedule review for weak or partial reconstructions.
7. Update readiness only when transfer is demonstrated.

## Example next action

Ask the learner to reconstruct a named argument in numbered premises, then give one charitable objection.

## Argument and writing activities

Philosophy benefits from activities that require reconstruction and production:

- `explain_back` — explain an argument or concept in the learner's own words.
- `writing_or_essay_review` — submit a short essay, objection, or reply for feedback.
- `diagram_or_whiteboard` — draw an argument map or conceptual distinction.
- `upload_and_review` — submit a reading note, outline, or primary-text commentary.

Use `scripts/record_activity_result.py` when the learner submits written or drawn evidence. Grade for clarity, charity, and precision; schedule review for partial or vague reconstructions.

## Source freshness and learner adaptation

- Philosophical arguments and texts are stable. Source freshness applies mainly to syllabus/curriculum changes or contemporary applications.
- Adapt question style and activity type between argument analysis, explain-back, essay, and diagram tasks based on evidence.
