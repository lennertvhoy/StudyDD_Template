# REVIEW_OVERRIDES — Spaced-Repetition Override Log

> **Agent-maintained.** Record every time the learner overrides the
> review-first recommendation. Silent neglect is not allowed.

## Doctrine

> Spaced repetition is the default. Human override is allowed. Silent neglect is not.

## Override format

Each override entry should include:

- **Timestamp:** ISO 8601 with timezone
- **Learner:** learner name or identifier
- **Skipped review IDs:** list of reviews passed over
- **Reason:** why the learner chose not to review now
- **Chosen action:** what the learner chose instead
- **Agent recommendation:** what the agent recommended at the time
- **Next review recommendation:** when/how to revisit the skipped reviews

## Overrides
- **Timestamp:** 2026-06-25T12:05:00+00:00
- **Learner:** Demo Learner
- **Skipped review IDs:** rev_demo-search-basics_20260624_100000
- **Reason:** learner wanted to see a new topic in the demo
- **Chosen action:** continue with Q-DEMO-002 on hybrid retrieval
- **Agent recommendation:** review demo-search-basics first
- **Next review recommendation:** revisit the skipped review within 24 hours

