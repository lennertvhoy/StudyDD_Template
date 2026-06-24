# MISTAKE_TAXONOMY — Tag Mistakes After Grading

> **Agent action.** Tag the mistake type whenever an answer is not fully correct.

## Canonical Tags

- `missed-constraint` — ignored a stated requirement, limit, or condition.
- `stale-source-assumption` — relied on outdated information.
- `service-boundary-confusion` — mixed up which service owns which responsibility.
- `chose-training-when-retrieval-was-better` — picked a complex training/fine-tuning solution when retrieval or prompt engineering was sufficient.
- `ignored-cost` — missed cost, pricing, quota, or resource implications.
- `ignored-monitoring` — missed observability, logging, metrics, or alerting.
- `ignored-security` — missed security, safety, privacy, or access-control implications.
- `overconfident-guess` — answered quickly without enough evidence in the answer.
- `keyword-trap` — matched a keyword but misunderstood the concept.
- `vague-answer` — answer was too general or hand-wavy.
- `correct-concept-weak-implementation` — understood the idea but missed concrete details.
- `repaired-after-hint` — needed a hint or repair question to reach correctness.
- `source-confusion` — mixed up sources or applied the wrong source.
- `memorized-wording-without-transfer` — recited wording but could not apply it.
- `answer-changed-after-feedback` — learner changed their answer after seeing feedback, creating unreliable evidence.

## How To Tag

- Use the most specific tag that fits.
- Multiple tags are allowed when more than one mistake pattern appears.
- Record the tag in the evidence item and the review item.
- Use tags to choose the next question and review mode.

## Example

A learner says "hybrid search combines vector and keyword search" but cannot name a field configuration or scenario.

Tag: `correct-concept-weak-implementation`.
