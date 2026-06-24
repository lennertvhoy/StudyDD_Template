# Exam Drill Prompt

Run a realistic exam-style drill inside StudyDD.

## Path Verification

1. Run `pwd` and `git rev-parse --show-toplevel`. Confirm the repo root.
2. Run `git remote -v` and confirm it matches the learner's StudyDD repo.
3. Run `python3 scripts/check_studydd.py`.

## Setup

1. Read all files listed in `AGENTS.md` "Required First Actions".
2. Select a balanced set of questions covering weak areas, practiced areas, pending skills, and confirmed strengths.
3. Use `protocols/QUESTION_QUALITY.md` to design each question.
4. Simulate exam conditions: clear wording, no hints unless asked.

## During The Drill

1. Ask one question at a time.
2. Do not reveal the answer until the learner has responded.
3. For multiple-choice, choose-two, choose-three, and matching questions:
   - create the private answer key first
   - shuffle visible options randomly
   - verify the answer key still points to the correct visible labels
   - avoid repeating the same correct label too often
4. Grade strictly against the answer key.
5. Record every result as evidence.
6. Record the final visible option order, correct answer label(s), learner answer, and grading result in the session log.
7. Tag mistakes using `protocols/MISTAKE_TAXONOMY.md`.

## Grading

- **correct** — fully meets the answer key
- **partial** — partly correct but missing something important
- **incorrect** — does not meet the answer key
- **unclear** — cannot be graded because the answer is ambiguous

Be strict. Exam drills exist to find gaps, not to inflate readiness.

## End Of Drill

1. Report the score.
2. Highlight weak areas that need more work.
3. Confirm only the strengths that held up under evidence.
4. Propose conservative readiness updates using `protocols/READINESS_POLICY.md`.
5. Add review items for weak or repaired answers.
6. Propose the next action in `NEXT_ACTIONS.md`.
7. Run `python3 scripts/check_studydd.py`.
