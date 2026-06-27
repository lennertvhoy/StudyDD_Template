# Compact State Test Output

Command:

```bash
python3 scripts/test_compact_state.py
```

Output (truncated to final status):

```
StudyDD compact state test
==========================
StudyDD create-instance
=======================
...
Running compact_state.py
Compacting StudyDD state...
Updated state/CURRENT_CONTEXT.md
Updated state/EVIDENCE_INDEX.yaml (1 evidence items)
Updated sessions/SESSION_SUMMARIES.md

Running validator
StudyDD validation
==================

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.

Compact state test passed.
```

Result: **pass**.
