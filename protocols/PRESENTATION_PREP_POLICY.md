# PRESENTATION_PREP_POLICY — Presentation and Oral-Exam Rehearsal

> **Agent rule.** Presentation prep builds clarity, structure, and timing through rehearsal and review.

## Doctrine

```text
Structure first. Rehearse often. Review one improvement at a time.
```

Presentation prep helps the learner structure a talk, rehearse it, and review the result. Evidence includes outlines, transcripts, timing notes, and repeated attempts.

## Tracked state

StudyDD tracks presentation prep state in `state/ACTIVITY_STATE.yaml` and `activities/ACTIVITY_LOG.md`. The canonical structure is:

```yaml
presentation_prep_state:
  presentation_goal: ""
  audience: ""
  target_duration_minutes: null
  outline: []
  rehearsal_history: []
  weak_patterns:
    - unclear_opening
    - too_much_jargon
    - weak_transition
    - unsupported_claim
    - rushed_ending
    - low_energy_delivery
```

In template mode these fields stay empty. Learner instances populate them with the presentation goal and audience.

## Agent behavior

- Help structure the talk: opening, main points, evidence, closing.
- Review outlines, slides, transcripts, or voice notes.
- Give timing and clarity feedback.
- Suggest one improvement at a time.
- Encourage rehearsal.
- Track evidence from repeated attempts.
- Avoid vague motivational feedback.

## Activity types

Use these activity types from `activities/ACTIVITY_TEMPLATES.yaml`:

- `presentation_prep` — rehearse a presentation, pitch, class explanation, demo talk, or oral exam answer.
- `voice_note_review` — review a recorded rehearsal transcript.
- `diagram_or_whiteboard` — draw a model or flow to support the talk.
- `explain_back` — explain the key idea in your own words.

## Weak patterns

Track and tag:

- `unclear_opening` — the audience does not know why the talk matters.
- `too_much_jargon` — unexplained terms block understanding.
- `weak_transition` — the audience loses the thread between sections.
- `unsupported_claim` — a strong claim without evidence or example.
- `rushed_ending` — the closing is hurried or missing.
- `low_energy_delivery` — transcript shows flat or monotone markers (heuristic only, not emotion analysis).

## Timing feedback

Use `scripts/analyze_presentation_rehearsal.py` to estimate speaking time from a transcript and compare it to the target duration. Do not overclaim precision; word-count estimates vary by speaker.

## Evidence recording

Record each rehearsal attempt with:

- activity ID,
- transcript word count,
- estimated speaking time,
- structure markers found,
- weak patterns observed,
- one suggested improvement,
- verdict against the presentation goal.

## Readiness

A single clear rehearsal can move a skill to `practiced`. High readiness requires consistent structure, timing, and clarity across repeated rehearsals.
