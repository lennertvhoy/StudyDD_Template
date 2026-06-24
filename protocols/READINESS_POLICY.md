# READINESS_POLICY — Evidence-Gated Readiness

> **Agent rule.** Readiness is earned through demonstrated answers, not encouragement or source coverage.

## Readiness Bands

Use these bands in `state/SKILL_MAP.yaml`:

| Band | Label | Meaning |
|------|-------|---------|
| 0–30 | exposed / new | Has seen the topic, no or weak evidence. |
| 31–50 | familiar | Can talk about the topic, evidence is thin or unrepaired. |
| 51–70 | practiced | Correct in targeted questions, not yet stable. |
| 71–80 | demonstrated | Correct across varied targeted questions. |
| 81–90 | mixed-checkpoint ready | Holds up in mixed-topic drills. |
| 91–100 | exam ready | Repeated high-pressure or timed evidence. |

## Upgrade Rules

- A single correct answer can move a skill from `pending` to `practiced` (roughly 50–60).
- A repaired answer stays at or below `practiced` (roughly 40–55).
- A partial answer stays `weak` or `practiced` at the low end (roughly 30–50).
- An incorrect answer marks the skill `weak` (0–35).
- `confirmed` status requires strong or varied evidence; do not set it after one question.
- To move above 70, require at least two correct answers across different question types or scenarios.
- To move above 80, require mixed-checkpoint evidence.
- To move above 90, require timed or high-pressure evidence.

## What Does Not Count

- Reading or summarizing source material.
- Watching a video or lecture.
- Saying "I know this."
- A single easy definition question.
- A correct answer that was rehearsed immediately before.

## Certification Targets

- High confidence needs fresh official sources.
- Stale source maps should block confidence above `medium`.
- Exam readiness (90–100) should be rare and backed by repeated evidence.

## Active Study Skill

If the active target declares a `study_skill`, also follow that skill's readiness upgrade rules. When the skill policy and the general readiness policy conflict, the stricter anti-inflation rule wins.
