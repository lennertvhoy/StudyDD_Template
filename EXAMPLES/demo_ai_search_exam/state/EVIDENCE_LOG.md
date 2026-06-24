# EVIDENCE_LOG — Demonstrated Learning Evidence

> **Agent-maintained.** Append evidence items after learner answers, repairs, reflections, overrides, or validated demonstrations.

## What counts as evidence

Evidence links a specific learner response to a target, skill, and question. It must be concrete enough that a third party could audit it.

Good evidence:

- "Learner correctly explained the difference between keyword and vector retrieval and gave a target-specific hybrid retrieval configuration."
- "Learner identified the authoritative source system and described how to use a spreadsheet as secondary evidence."
- "Learner repaired an incomplete answer by naming the missing safety evaluation step."

Weak evidence:

- "Learner seems to understand the topic."
- "Correct."
- "Doing great."

## Format

- **Date:**
- **Target ID:**
- **Skill ID:**
- **Question ID:**
- **Question summary:**
- **Learner answer summary:**
- **Verdict:** correct / partial / incorrect / unclear / override
- **Explanation:**
- **Confidence:** high / medium / low

## Evidence items

- **Evidence ID:** ev_demo_001
- **Date:** 2026-06-24
- **Target ID:** demo-ai-search-exam
- **Skill ID:** demo-search-basics
- **Question ID:** Q-DEMO-001
- **Question summary:** Explain keyword vs vector search and when to combine them.
- **Learner answer summary:** Correctly distinguished keyword and vector search but omitted a concrete scenario.
- **Verdict:** partial
- **Mistake type:** correct-concept-weak-implementation
- **Explanation:** Concept was right; answer lacked target-specific implementation detail.
- **Confidence:** medium
