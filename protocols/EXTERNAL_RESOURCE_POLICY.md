# EXTERNAL_RESOURCE_POLICY — Recommending External Resources

> **Agent rule.** Recommend an external resource when it is better than an AI-generated explanation or exercise.

## Doctrine

```text
One good resource, with a reason.
Prefer official or high-authority sources for volatile topics.
```

StudyDD can assign videos, readings, documentation pages, exercises on other platforms, or any trusted external resource as a learning activity. The agent must choose deliberately and explain why the resource helps.

## When to recommend an external resource

Recommend an external resource when:

- the concept is easier to understand with visualization or worked examples,
- an official source is more authoritative than agent memory,
- the learner needs practice density the agent cannot provide,
- a different teaching style may help a stuck learner,
- the topic is stable and a high-quality educational resource exists.

Do not recommend an external resource when:

- a short agent explanation or question is sufficient,
- the topic is volatile and no fresh authoritative source exists,
- the only goal is to send the learner away from StudyDD tracking.

## Source authority and freshness

For volatile or current domains, prefer official or high-authority sources. Run `scripts/check_source_freshness.py` or inspect `sources/SOURCE_STATE.yaml` before treating a resource as current truth.

For stable subjects, high-quality educational videos, textbooks, or exercise platforms may be acceptable even if they are not official.

## Recommendation format

Each external-resource recommendation must include:

- **Resource:** title and URL (or identifier if offline).
- **Why it helps:** one or two sentences from the list below.
- **Task:** what the learner should do with the resource.
- **Expected evidence:** what the learner will submit after using it.
- **Learner control:** the exact phrase: `You can accept, modify, or override this.`

## Why-it-helps phrases

Use one of these plain explanations:

- **better visualization** — the resource shows the concept in a way text cannot.
- **worked examples** — the resource walks through examples step by step.
- **official explanation** — the resource is authoritative for this topic.
- **practice density** — the resource provides more practice items than StudyDD can generate here.
- **different teaching style** — the resource explains the idea from a different angle.

## One resource at a time

Recommend one good resource per activity. If the learner wants alternatives, offer one or two more after the learner responds. Avoid dumping lists of links.

## Learner decline

If the learner declines the resource or chooses a different one, record the override in `activities/ACTIVITY_LOG.md` and `state/EVIDENCE_LOG.md` if it bypasses a strong recommendation.

## No live web search in this slice

This policy covers state and decision support only. It does not add live web search to StudyDD. The agent may recommend known trusted resources or ask the learner to supply a resource link for review.
