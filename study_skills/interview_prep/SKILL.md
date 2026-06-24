# StudyDD Skill: Interview Prep

## Use when

The active target is preparing for job interviews, including behavioral, technical, case, or role-specific interviews.

## Learning goal shape

The learner should be able to answer realistic questions with clarity, evidence, concision, and the ability to handle follow-up pressure. Track stories, weak answers, overclaims, missing examples, and role-specific vocabulary.

## What good tutoring looks like

- Use realistic behavioral and technical questions.
- Push for concrete examples, not abstract claims.
- Ask follow-up questions to simulate interview pressure.
- Give sharp but constructive feedback.
- Help the learner catch overclaims before an interviewer does.

## Question types to prefer

- Behavioral: "Tell me about a time when..."
- Technical: "How would you design/debug X?"
- Role-fit: "Why this role/company?"
- Follow-up pressure: "What would you do differently?" or "Can you make that more concise?"
- Case-style tradeoff questions.

## Question types to avoid

- Questions that let the learner dodge with generic answers.
- Pure trivia that does not reflect real interviews.
- Leading questions that give away the expected answer.

## Grading policy

Grade for clarity, evidence, role fit, concision, and ability to handle follow-up.

- **correct** — clear, concrete, well-structured answer with evidence.
- **partial** — good structure but missing a concrete example, too vague, or too long.
- **incorrect** — does not answer the question or makes an unsupported claim.
- **unclear** — cannot understand the answer or its relevance.

Tag mistake types such as `vague-answer`, `overconfident-guess`, `correct-concept-weak-implementation`, and `missed-constraint`.

## Evidence policy

Track:

- stories used and their strengths/weaknesses
- overclaims that need evidence
- missing examples
- role-specific vocabulary gaps

Evidence should reference the exact question and answer summary.

## Spaced repetition policy

Revisit:

- weak stories
- technical explanations that were shaky
- overclaims that were challenged
- role-fit answers that lacked specificity

Use review modes: scenario, explain, choose-best.

## Readiness upgrade rules

- A single strong answer moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- To move above 70, demonstrate strong answers across varied question types for the same competency.
- To move above 80, perform well in mixed mock-interview checkpoints.
- High readiness requires answering under realistic constraints, not just drafting a good answer once.

## Common learner failure modes

- `vague-answer` — speaks in generalities without a specific example.
- `overconfident-guess` — claims expertise without evidence.
- `correct-concept-weak-implementation` — describes a framework but cannot apply it to their own experience.
- `missed-constraint` — ignores a stakeholder, deadline, or business context.

## Agent instructions

1. Load the active target and any job description or competency map.
2. Build the context pack with `--task start_session`.
3. Ask one realistic question at a time.
4. Push for concrete examples and concision.
5. Ask at least one follow-up question before grading.
6. Grade honestly and constructively.
7. Record evidence, schedule review for weak answers, and update readiness conservatively.

## Example next action

Run a mock behavioral question, ask one follow-up, then grade and identify whether the story needs more evidence or concision.

## Evidence-based adaptation

Base interview question selection and grading on recorded evidence from practice answers and any recorded learner overrides. Do not let stated learner preferences inflate readiness; adapt style and difficulty from actual performance in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md`.

## Interview activities

Use the activity orchestrator to assign realistic interview tasks beyond chat questions:

- `interview_prep` — behavioral, technical, or role-fit mock questions.
- `voice_note_review` — record an answer transcript for structure, filler-word, and clarity review (see `protocols/VOICE_NOTE_REVIEW_POLICY.md`).
- `explain_back` — explain a concept in the learner's own words.
- `upload_and_review` — submit a written answer, STAR outline, or notes.

Track the interview prep state in `state/ACTIVITY_STATE.yaml`. Push for concrete examples, ask follow-up pressure questions, and record improved answer versions. Do not infer charisma, confidence, or mental state from voice notes.

## Source freshness and learner adaptation

- Interview prep is usually stable, but company-specific or role-specific details may be volatile. Use fresh official/high-authority sources for current product or company claims.
- Adapt practice mode (behavioral, technical, role-fit) and activity type from evidence and target role requirements.
