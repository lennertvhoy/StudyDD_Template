# EVIDENCE_INTAKE_POLICY — Evidence From Outside the Chat

> **Agent rule.** StudyDD can review evidence submitted from outside the chat, but it grades the evidence, not the effort.

## Doctrine

```text
Submitted evidence is real evidence. Effort is acknowledged.
Readiness only changes from demonstrated competence.
```

Learners may complete a StudyDD activity outside the chat and submit the result. The agent reviews the submitted evidence according to the active study skill, records the result, and updates state conservatively.

## Accepted evidence formats

```yaml
submitted_as:
  - typed_answer
  - voice_note
  - transcript
  - screenshot
  - photo
  - pdf
  - external_score
  - command_output
  - lab_log
  - presentation_outline
  - essay
  - whiteboard_diagram
```

Other formats are allowed if the learner and agent agree on how to review them.

## Evidence categories

Distinguish four kinds of evidence:

- **Completion evidence** — the learner did the task (watched the video, ran the commands, filled the worksheet).
- **Effort evidence** — the learner tried; quality is not yet gradable.
- **Correctness evidence** — the result can be graded against a rubric.
- **Mastery evidence** — the result meets the standard across varied conditions.

Only correctness and mastery evidence can change readiness upward. Completion and effort evidence can be acknowledged and recorded, but they do not inflate readiness.

## Grading submitted evidence

- Load the active study skill (`study_skills/<id>/SKILL.md`).
- Define the rubric before reviewing the evidence.
- Grade the actual submitted evidence, not the learner's description of it.
- If the evidence is unclear, ask one focused clarification.
- If the evidence is insufficient, mark it `insufficient_evidence` and ask the learner to resubmit or switch activity.

## Recording submitted evidence

Every graded submission must produce:

- an evidence ID (linked to the activity ID),
- a verdict (`correct`, `partial`, `incorrect`, `unclear`, `insufficient_evidence`),
- mistake tags when the verdict is not `correct`,
- a confidence level,
- an entry in `state/EVIDENCE_LOG.md`,
- an entry in `activities/ACTIVITY_LOG.md`.

## Activity linkage

Submitted evidence should reference the activity ID that generated it. If the learner submits evidence without a prior activity, create a retroactive activity record so the audit trail stays complete.

## Voice and presentation evidence

Voice notes and presentation rehearsals are reviewed transcript-first or metadata-only. See `protocols/VOICE_NOTE_REVIEW_POLICY.md` and `protocols/PRESENTATION_PREP_POLICY.md`. Do not infer mental state, charisma, or emotion from audio.

## External platform scores

An external score (e.g., 8/10 on a platform drill) is evidence, not proof of mastery. Record the score, the platform, the topic, and the date. Readiness upgrades still require explanation or transfer evidence, not just the score.

## Conservative state updates

- A single strong submission can move a skill from `pending` to `practiced`.
- A partial or repaired submission stays at or below `practiced`.
- A weak submission marks the skill `weak` and schedules a review.
- High readiness still requires varied or repeated evidence.

## Learner override

The learner may ask the agent to accept effort as evidence or to upgrade readiness based on completion. Record the override but keep the readiness upgrade conservative unless the evidence supports it.
