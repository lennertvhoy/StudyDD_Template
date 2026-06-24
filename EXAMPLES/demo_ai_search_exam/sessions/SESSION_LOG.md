# SESSION_LOG — Study Session History

> **Agent-maintained.** Append one entry per completed study session.

## Format

Each entry should include:

- **Date:** ISO 8601 date
- **Target ID:** target folder ID
- **Focus:** topic or skill practiced
- **Questions asked:** list of question IDs
- **Result summary:** what was demonstrated
- **Evidence added:** references to `state/EVIDENCE_LOG.md`
- **Reviews added:** references to `reviews/REVIEW_QUEUE.md`
- **State changes:** what changed in `state/STUDY_STATE.yaml` or `state/SKILL_MAP.yaml`
- **Next action proposed:** what the learner should do next

For fixed-option questions (multiple-choice, choose-two, choose-three, matching), also record per question **after grading**:

- **Internal option IDs (optional):** stable IDs like `opt_1`, `opt_2`, etc., mapped to option content
- **Final visible option order:** the shuffled labels and option content shown to the learner
- **Correct answer label(s):** the label(s) that mapped to the private answer key after shuffling
- **Learner answer:** the label(s) the learner selected
- **Grading result:** correct / partial / incorrect / unclear

Do not record the private answer key, internal option IDs, or correct labels in repo files before the learner answers.

## Sessions
- **Date:** 2026-06-24
- **Target ID:** demo-ai-search-exam
- **Focus:** keyword vs vector search
- **Questions asked:** Q-DEMO-001
- **Result summary:** Learner gave a partial answer; review scheduled.
- **Evidence added:** ev_demo_001
- **Reviews added:** rev_demo-search-basics_20260624_100000
- **State changes:** demo-search-basics marked weak, readiness 35, review scheduled.
- **Next action proposed:** Review demo-search-basics or continue with Q-DEMO-002.

