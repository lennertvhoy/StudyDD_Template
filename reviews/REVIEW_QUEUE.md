# REVIEW_QUEUE — Spaced Repetition

> **Agent-maintained.** Add review items only when evidence shows a weak, partial, repaired, or shaky answer.

## Due now

- None. This public template has not been initialized for a learner yet.

## Scheduled

- None.

## Review item format

Each review item should include:

- **Review ID:**
- **Target ID:**
- **Skill ID:**
- **Evidence ID:**
- **Prompt:**
- **Due date:**
- **Interval days:**
- **Confidence/ease:**
- **Lapse count:**
- **Last result:**
- **Mistake type:** (see `protocols/MISTAKE_TAXONOMY.md`)
- **Review mode:** recall / scenario / explain / troubleshoot / choose-best

## Rules

- Schedule a review after every partial, incorrect, unclear, repaired, or shaky answer.
- Do not schedule a review for a single confident correct answer on a fresh skill.
- First interval after a weak answer: 1 day.
- Correct recall: double the interval, capped by target deadline or 30 days.
- Lapse or partial: reset interval to 1 day and increment lapse count.
- Choose a review mode that differs from the original question mode when possible.
