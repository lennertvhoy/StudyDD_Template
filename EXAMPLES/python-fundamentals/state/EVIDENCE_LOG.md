# EVIDENCE_LOG — Python Fundamentals Example

- **Date:** 2026-06-24
- **Target ID:** python-fundamentals
- **Skill ID:** py-concurrency
- **Question ID:** Q-PY-001
- **Question summary:** Explain threading vs asyncio in Python with concrete scenarios.
- **Learner answer summary:** Correctly identified OS thread overhead vs event loop efficiency. Gave web scraping for asyncio and Selenium for threading. Did not address the GIL's role in CPU-bound vs I/O-bound distinction.
- **Verdict:** partial
- **Mistake type:** correct-concept-weak-implementation
- **Explanation:** Core distinction was correct but GIL nuance was missing. Needs repair question on GIL interaction.
- **Confidence:** medium

---

- **Date:** 2026-06-24
- **Target ID:** python-fundamentals
- **Skill ID:** py-typing
- **Question ID:** Q-PY-002
- **Question summary:** Write a type-annotated function for counting user appearances from JSON strings.
- **Learner answer summary:** Wrote `def count(records: list[str]) -> dict[str, int]` with correct generics. Used `defaultdict` for the implementation.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Correct signature and implementation. No issues.
- **Confidence:** high

---

- **Date:** 2026-06-23
- **Target ID:** python-fundamentals
- **Skill ID:** py-dstructs
- **Question ID:** (practical lab)
- **Question summary:** Practical lab: refactor a legacy Python script to use comprehensions, generators, and context managers.
- **Learner answer summary:** Submitted a rewritten module with generator-based file processing, `with` statements for resource handling, and list comprehensions replacing manual loops.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Demonstrated idiomatic Python across multiple patterns in a practical exercise.
- **Confidence:** high

---

- **Date:** 2026-06-22
- **Target ID:** python-fundamentals
- **Skill ID:** py-dstructs
- **Question ID:** Q-PY-003
- **Question summary:** Identify O(n^2) list membership and rewrite with set.
- **Learner answer summary:** Identified the `if w not in words` O(n) scan inside a loop. Rewrote with a set comprehension.
- **Verdict:** correct
- **Mistake type:** N/A
- **Explanation:** Correctly diagnosed and fixed the performance issue.
- **Confidence:** high
