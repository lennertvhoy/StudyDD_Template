# Study Loop Smoke Test Output

Command:

```bash
python3 scripts/test_study_loop_smoke.py
```

Output (truncated to final status):

```
StudyDD study-loop smoke test
=============================
...
Scheduling review
Scheduled review rev_loop-search-basics_20260624_100000
  skill_id: loop-search-basics
  evidence_id: Q-LOOP-001
  grade: partial
  confidence: low
  interval_days: 1
  due_at: 2026-06-25T10:00:00+00:00

Selecting next action when review is overdue
StudyDD recommendation: review first.

Due reviews: 1
Overdue reviews: 0
Recommended action: review rev_loop-search-basics_20260624_100000 (Keyword vs vector search) before new material.
Reason: this review is due today and spaced retrieval is the highest-retention move.

Override allowed:
Say "override review because <reason>" and the agent must record the override.

Recommended by StudyDD: review first. You can override, but this is the highest-retention move.

Recording override
Compacting state before validation
Compacting StudyDD state...
Updated state/CURRENT_CONTEXT.md
Updated state/EVIDENCE_INDEX.yaml (1 evidence items)
Updated sessions/SESSION_SUMMARIES.md

Running full learner-instance validation
StudyDD validation
==================

Warnings:
  - Active target 'loop-smoke-target' does not declare a study_skill; generic tutoring will be used.

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.

Study-loop smoke test passed.
```

Result: **pass**.
