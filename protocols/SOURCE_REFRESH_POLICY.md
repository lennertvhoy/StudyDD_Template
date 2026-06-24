# SOURCE_REFRESH_POLICY — Source Refresh Rules

This policy governs when and how agents refresh source material for StudyDD.

## Rules

- Refresh sources only when the freshness gate says it is needed. Do not refresh blindly.
- Prefer official or `high_authority` sources.
- Refresh the smallest source set needed for the current question or task.
- Cache source metadata back to the canonical source registry (`sources/SOURCE_STATE.yaml`) once it is introduced.
- Record: checked source, timestamp, authority level, volatility class, usability verdict, and reason for the refresh.
- Do not refresh stable topics unnecessarily. Stable and slow_changing material may be reused unless a specific reason to recheck exists.
- Learner override options include:
  - "refresh sources now"
  - "use stale source for practice only"
  - "avoid web search"
  - "official sources only"
- Any override must be recorded in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md`.
