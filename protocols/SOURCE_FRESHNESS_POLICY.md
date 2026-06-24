# SOURCE_FRESHNESS_POLICY.md — Source Freshness Rules

This policy defines how fresh a source must be for a given study topic, and how agents must handle stale or uncertain information.

## Volatility Classes

```yaml
volatility_classes:
  stable:
    examples: [basic arithmetic, classical logic forms, long-established historical facts, basic grammar patterns]
    default_max_age_days: 3650
    source_required_for_new_questions: false
  slow_changing:
    examples: [general networking fundamentals, basic programming concepts, established philosophical arguments, standard mathematical techniques]
    default_max_age_days: 730
    source_required_for_new_questions: false
  moderate:
    examples: [certification objectives, school curriculum standards, cloud architecture best practices, software library behavior]
    default_max_age_days: 90
    source_required_for_new_questions: true
  volatile:
    examples: [Microsoft Azure services, cloud security products, vendor certification exam objectives, pricing, preview features, portal UI locations, product names, compliance features]
    default_max_age_days: 30
    source_required_for_new_questions: true
  live:
    examples: [current outages, current prices, current exam retirement dates, current product availability, breaking changes]
    default_max_age_days: 1
    source_required_for_new_questions: true
```

## Rules

- Targets should declare a volatility class in their `TARGET.yaml`. If the class is missing, the agent must default to `moderate` and warn the learner.
- Authoritative questions about volatile or live topics require fresh, usable official or `high_authority` sources before they may be treated as current.
- Stale sources may be used only with explicit learner override. Questions built from stale sources must be labelled as practice-only and not treated as authoritative.
- The agent must not hide uncertainty. If source freshness is unknown or borderline, the agent must disclose that to the learner.
- The learner may override freshness recommendations. Any override must be recorded in `state/EVIDENCE_LOG.md` and `sessions/SESSION_LOG.md`.
