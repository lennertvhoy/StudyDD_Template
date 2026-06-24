# SOURCE_TRUST — Trust And Freshness Rules

> **Agent rule.** Build skill maps and questions from trusted sources.

## Source Types

- **official** — vendor exam guide, product documentation, certification page, course syllabus.
- **trusted-internal** — employer materials, recruiter guidance, interview rubric, internal wiki.
- **learner-note** — learner's own notes, flashcards, or summaries.
- **secondary** — blog posts, forum threads, practice-question explanations, generated summaries.
- **generated** — AI-generated content used as a starting point only.

## Authority Levels

- **high** — official or trusted-internal sources that are current.
- **medium** — learner notes or well-known secondary sources.
- **low** — generated summaries, outdated blogs, or unverified claims.

## Rules

1. Prefer official sources first.
2. Treat old notes, spreadsheets, exports, blog posts, and generated summaries as secondary until verified.
3. Record every source in `sources/SOURCE_INDEX.md` with `last_checked`.
4. When sources conflict, record the conflict and choose the most authoritative current source.
5. Do not build readiness claims from source coverage alone. Readiness requires learner evidence.
6. For certification targets, high confidence requires at least one official/high-authority source that has been checked recently.
7. Stale sources should lower confidence and block high readiness.

## Freshness

- `last_checked` should be within the last 90 days for fast-moving topics.
- For stable foundational topics, 180 days is acceptable.
- If a source has no `last_checked`, treat it as medium authority at best.
