# EVIDENCE_LOG — System Design Skills Example

- **Date:** 2026-06-24
- **Target ID:** system-design-skills
- **Skill ID:** sd-consistency
- **Question ID:** Q-SD-001
- **Question summary:** Compare eventual consistency and strong consistency with concrete scenarios.
- **Learner answer summary:** Correctly distinguished both models; gave a ledger example for strong and a social like-counter for eventual. Mentioned quorum but did not elaborate on latency trade-offs.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Answered correctly with appropriate scenarios. Minor depth gap on quorum configuration did not affect correctness.
- **Confidence:** medium

---

- **Date:** 2026-06-24
- **Target ID:** system-design-skills
- **Skill ID:** sd-caching
- **Question ID:** Q-SD-002
- **Question summary:** Caching strategy for a read-heavy social feed service.
- **Learner answer summary:** Correctly suggested Redis for timeline caching and CDN for media. Proposed TTL-based invalidation but did not address active invalidation when a followed user posts. Did not distinguish cache-aside vs read-through.
- **Verdict:** partial
- **Mistake type:** correct-concept-weak-implementation
- **Explanation:** High-level approach was sound but the invalidation strategy was incomplete. Needs repair on active invalidation patterns.
- **Confidence:** medium

---

- **Date:** 2026-06-21
- **Target ID:** system-design-skills
- **Skill ID:** sd-observability
- **Question ID:** (mixed drill)
- **Question summary:** Identify three observability signals and give a concrete tool for each in a microservice architecture.
- **Learner answer summary:** Named logging (structured JSON), metrics (Prometheus), and tracing (OpenTelemetry). Explained how a trace spans across service boundaries.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Strong answer with concrete tooling examples.
- **Confidence:** high

---

- **Date:** 2026-06-20
- **Target ID:** system-design-skills
- **Skill ID:** sd-observability
- **Question ID:** (initial assessment)
- **Question summary:** What is the difference between a metric and a log? When would you use each?
- **Learner answer summary:** Correctly contrasted structured logs with aggregatable metrics. Gave an example of using metrics for alerting and logs for debugging.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Demonstrated clear understanding of both signals.
- **Confidence:** high
