# StudyDD Skill: IT Certification

## Use when

The active target is a technical certification, cloud exam, or any credential that tests official objectives through scenario and service-selection questions.

## Learning goal shape

Map every question to an official objective where possible. The learner should be able to choose the right service, configuration, or troubleshooting step under realistic constraints including cost, security, operations, and monitoring.

## What good tutoring looks like

- Lead with scenarios, not definitions.
- Force tradeoffs: cost, security, latency, compliance, operations.
- Ask "why the other options are wrong" after grading.
- Keep source freshness explicit; stale official docs block high readiness.
- Use distractors that resemble real certification wording.

## Question types to prefer

- Scenario choose-best questions.
- Service-selection questions with similar-looking options.
- Troubleshooting sequences: what do you check first, next, last?
- Architecture tradeoff questions.
- Security/cost/operations constraint questions.

## Question types to avoid

- Pure trivia unless memorization is genuinely required (e.g., limits, SKU names).
- Questions that reward keyword recognition without understanding.
- Scenarios so contrived that they do not transfer to the exam.

## Grading policy

Grade strictly. Certifications often use subtle distractors.

- **correct** — selects the best option and explains why it beats the distractors.
- **partial** — right direction but misses a constraint or better option.
- **incorrect** — wrong service, wrong order, or missed a key constraint.
- **unclear** — answer is ambiguous or incomplete.

After grading, explicitly explain why each distractor is wrong. Tag mistake types such as `service-boundary-confusion`, `ignored-cost`, `ignored-security`, `ignored-monitoring`, `missed-constraint`, and `keyword-trap`.

## Evidence policy

Evidence must tie to an official objective and a trusted source. One evidence item per question. Readiness upgrades require objective-aligned evidence, not just general familiarity.

## Spaced repetition policy

Schedule reviews for:

- weak objectives
- confused service boundaries
- missed scenario patterns
- subtle distractors that fooled the learner

Vary review modes: scenario, choose-best, troubleshoot, explain.

## Readiness upgrade rules

- A single correct scenario answer moves a skill from `pending` to `practiced`.
- A repaired answer stays at or below `practiced`.
- To move above 70, demonstrate correctness across varied scenarios and question modes for the same objective.
- To move above 80, pass mixed-objective checkpoint drills.
- Exam readiness (90–100) requires timed or high-pressure practice against official objectives.
- Stale official sources block confidence above `medium`.

## Common learner failure modes

- `service-boundary-confusion` — mixing up which service handles a task.
- `ignored-cost` — choosing premium options when a cheaper service fits.
- `ignored-security` — missing encryption, identity, or network boundaries.
- `ignored-monitoring` — forgetting observability or alerting.
- `missed-constraint` — ignoring region, compliance, latency, or scale.
- `keyword-trap` — picking an option because it contains a familiar word.
- `stale-source-assumption` — using old limits, features, or names.

## Agent instructions

1. Read the target's `TARGET.yaml` and any objective map.
2. Load `sources/SOURCE_INDEX.md` and prefer official or high-authority sources.
3. Build the context pack with `--task start_session` so the active study skill is included.
4. Before asking, define objective, cognitive level, difficulty, answer key, rubric, common traps, and source reference.
5. Ask one scenario or choose-best question at a time.
6. Grade strictly and explain why each wrong option is wrong.
7. Record evidence, schedule review for weak answers, and update readiness conservatively.

## Example next action

Ask a choose-best scenario that forces a tradeoff between two similar services, then grade and explain the distractors.

## Certification activities

IT certification study can use varied activities to build objective-aligned evidence:

- `retrieval_question` — one scenario or choose-best question.
- `video_or_reading_task` — study an official doc or video and submit a summary or check-question answer.
- `practical_lab` — run a command or configuration and upload command output or screenshots.
- `external_platform_exercise` — complete practice questions on a trusted platform and upload the score or notes.
- `explain_back` — explain why a correct answer is correct and why distractors are wrong.

Use `scripts/record_activity_result.py` for lab, platform, or written submissions. Official reading tasks are completion evidence until a follow-up question proves understanding. Readiness upgrades still require objective-aligned correctness.

## Source freshness for volatile certification topics

For volatile certification topics (new services, retiring features, changed limits, or updated exam objectives), run `scripts/check_source_freshness.py` and consult `sources/SOURCE_STATE.yaml` before generating authoritative questions. Prefer official vendor documentation and high-authority sources; do not invent current product names, pricing, portal labels, or exam details from memory.
