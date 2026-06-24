# SCHEDULE_REVIEW — Schedule Spaced Repetition

> **Agent action.** Add review items when evidence shows weakness.

## When To Schedule

Schedule a review when:

- answer is partial
- answer is incorrect
- answer is unclear and later resolved
- answer was repaired after a hint
- answer was correct but shaky or lucky
- the skill has not been tested in a long time and readiness may be stale

Do not schedule a review for:

- a single confident correct answer on a freshly learned skill
- a `confirmed` skill with recent strong evidence

## Review Item Format

```markdown
- **Review ID:** R-YYYYMMDD-<target>-NNN
- **Target ID:**
- **Skill ID:**
- **Evidence ID:**
- **Prompt:**
- **Due date:**
- **Interval days:**
- **Confidence/ease:**
- **Lapse count:**
- **Last result:**
- **Mistake type:**
- **Review mode:** recall / scenario / explain / troubleshoot / choose-best
```

## Interval Guidance

- First review after a weak/repaired answer: 1 day.
- Correct recall: double the interval (1d → 2d → 4d → 8d → …), capped at the target deadline or 30 days.
- Partial or lapse: reset interval to 1 day and increment lapse count.
- Stale confirmed skill: 14 days or shorter if the target deadline is near.

## Review Mode Selection

- **recall** — definition, list, or fact.
- **scenario** — application in a realistic situation.
- **explain** — why and how something works.
- **troubleshoot** — diagnose and fix a problem.
- **choose-best** — select the best option among plausible distractors.

Choose a different mode than the original evidence when possible.
