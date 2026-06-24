# Future model efficiency note

> StudyDD should become cheaper over time by making easy tasks explicit, deterministic, and tool-like. The strongest model should only be needed at the moments where teaching judgment actually matters.

This document is a future architecture direction, not a runtime feature. StudyDD currently does not route tasks by model.

## Task complexity classes

```yaml
task_complexity:
  deterministic:
    examples:
      - parse YAML
      - validate timestamps
      - check source freshness metadata
      - update review interval
      - build context pack
      - run lint checks
    future_model: script_or_local_small_model

  low_reasoning:
    examples:
      - summarize recent session into fixed schema
      - classify mistake tags from a short answer
      - detect answer-key leakage
      - suggest due review from existing state
    future_model: cheap_small_model

  medium_reasoning:
    examples:
      - generate simple practice question from fresh source notes
      - explain a missed concept
      - propose a study adjustment from recent evidence
      - grade short factual answers
    future_model: small_or_mid_model

  high_reasoning:
    examples:
      - generate high-quality scenario questions
      - grade nuanced philosophy essays
      - judge ambiguous certification tradeoffs
      - reconcile conflicting sources
      - design a new study plan for a struggling learner
    future_model: strong_reasoning_model

  source_critical:
    examples:
      - current Azure product behavior
      - exam objective changes
      - pricing
      - security/compliance feature claims
      - preview/GA status
    future_model: source_grounded_strong_model_or_verified_tool
```

## Principle

Do not cheapen the tutoring; cheapen the plumbing.

Question creation, nuanced grading, and study-strategy judgment may need a strong model.
Freshness checks, scheduling, state compaction, linting, context packing, and override logging should become deterministic or cheap.
