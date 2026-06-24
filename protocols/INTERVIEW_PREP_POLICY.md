# INTERVIEW_PREP_POLICY — Interview and Mock-Interview Activities

> **Agent rule.** Interview prep is practice under realistic pressure with concrete evidence.

## Doctrine

```text
Realistic questions. Concrete examples. Follow-up pressure. Honest grading.
```

Interview prep is not about writing perfect answers in a chat. It is about practicing realistic questions, pushing for concrete examples, and catching weak patterns before a real interviewer does.

## Tracked state

StudyDD tracks interview prep state in `state/ACTIVITY_STATE.yaml` and `activities/ACTIVITY_LOG.md`. The canonical structure is:

```yaml
interview_prep_state:
  target_role: ""
  company: ""
  story_bank:
    - id: ""
      theme: ""
      evidence: ""
      weakness: ""
      last_practiced: ""
  weak_answer_patterns:
    - too_vague
    - too_long
    - no_concrete_example
    - overclaiming
    - missing_business_impact
    - weak_closing
  practice_modes:
    - behavioral
    - technical
    - role_fit
    - pressure_followup
    - salary_negotiation
```

In template mode these fields stay empty. Learner instances populate them with the target role and company.

## Agent behavior

- Ask realistic interview questions.
- Push for concrete examples, especially for behavioral questions.
- Ask follow-up questions before grading.
- Grade clarity, relevance, evidence, concision, and role fit.
- Suggest better structure when needed.
- Record improved answer versions after practice.
- Let the learner override tone and style.

## Activity types

Use these activity types from `activities/ACTIVITY_TEMPLATES.yaml`:

- `interview_prep` — behavioral, technical, or role-fit mock questions.
- `voice_note_review` — recorded answer review from a transcript.
- `explain_back` — explain a concept in your own words.
- `upload_and_review` — submit a written answer, outline, or notes.

## Grading

- **correct** — clear, concrete, well-structured, with evidence and role fit.
- **partial** — good structure but missing a concrete example, too vague, or too long.
- **incorrect** — does not answer the question or makes an unsupported claim.
- **unclear** — cannot understand the answer or its relevance.

Tag weak patterns from the tracked list: `too_vague`, `too_long`, `no_concrete_example`, `overclaiming`, `missing_business_impact`, `weak_closing`.

## Voice-note review

Interview answers can be submitted as voice notes or transcripts. Review them with `scripts/analyze_voice_note.py` and `protocols/VOICE_NOTE_REVIEW_POLICY.md`. Focus on structure, clarity, filler words, and target fit. Do not infer emotion or charisma.

## Story bank

Track STAR-style stories:

- **id** — short identifier.
- **theme** — leadership, conflict, failure, impact, etc.
- **evidence** — what the story proves.
- **weakness** — what still needs work.
- **last_practiced** — ISO timestamp.

## Readiness

A single strong mock answer can move a skill to `practiced`. High readiness requires strong answers across varied question types and follow-up pressure.
