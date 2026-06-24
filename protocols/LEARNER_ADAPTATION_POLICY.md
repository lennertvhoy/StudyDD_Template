# LEARNER_ADAPTATION_POLICY.md — Learner Adaptation Rules

This policy governs how StudyDD adapts its tutoring approach to the learner without manipulating them.

## Doctrine

```text
StudyDD should adapt to the learner, but not manipulate the learner.

The system may recommend better study methods.
The learner has the final decision.
Overrides are allowed and recorded.

Preference informs the route.
Evidence determines readiness.
Target requirements constrain both.
```

## Rules

- The agent may occasionally ask the learner for feedback, but not on every turn.
- Feedback requests should be short and useful.
- The agent must track learner preferences separately from evidence of mastery.
- The agent must distinguish between learner preference, demonstrated effectiveness, temporary energy state, and target requirements.
- The agent may recommend a different study approach if evidence shows the current one is weak.
- The agent must never flatter readiness to match learner preference.
- The learner can override any study method recommendation. The override must be recorded in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md`.
- Recommendations are graded by strength: `weak`, `moderate`, or `strong`.
- Every study adjustment ends with: "You can accept, modify, or override this."
