# VOICE_NOTE_REVIEW_POLICY — Safe Voice-Note and Transcript Review

> **Agent rule.** Review voice evidence for structure, clarity, correctness, and target fit. Do not pretend to read minds.

## Doctrine

```text
Transcript-first, metadata-only if no transcript.
Analyze what is said, not who the learner is.
```

Voice notes and presentation rehearsals can be reviewed without audio dependencies. The agent accepts a transcript or text summary and applies lightweight heuristics. No psychological, emotional, or charisma analysis is allowed.

## Allowed review actions

- Use the transcript if provided.
- Analyze structure (opening, middle, closing, transitions).
- Check correctness against target/source state.
- Count filler words from the transcript (e.g., "um", "uh", "like", "you know").
- Estimate answer length from transcript word count or audio metadata.
- Compare the content against a rubric.
- Suggest one concrete improvement at a time.

## Not allowed

- Do not infer mental health, anxiety, confidence, or emotional state.
- Do not produce objective charisma scores.
- Do not diagnose the learner.
- Do not claim precise emotion detection from tone, pacing, or word choice.
- Do not require audio-processing dependencies without explicit consent.

## Dependency-free review

`scripts/analyze_voice_note.py` is lightweight and uses only text. If the learner provides only an audio file, ask them to provide a transcript or use a local tool of their choice. Do not install audio libraries without consent.

## Filler-word heuristic

Filler words are counted from the transcript. The result is a count, not a personality judgment. Use it to suggest one focused practice target, such as "pause instead of saying 'um' before key points."

## Structure markers

Look for plain-language markers:

- opening: "first", "to start", "let me explain", "the question is"
- closing: "in summary", "to conclude", "the key takeaway", "finally"
- transition: "next", "then", "on the other hand", "for example"

## Feedback style

Keep feedback specific and actionable:

- "Your opening is clear."
- "Add one concrete example in the middle."
- "Your closing restates the main point well."
- "Try replacing 'um' with a short pause before the next key idea."

Avoid vague motivational feedback.

## Evidence recording

Record the review as an evidence item with:

- activity ID,
- transcript word count,
- filler counts,
- structure markers found,
- verdict against the rubric,
- one suggested next practice activity.
