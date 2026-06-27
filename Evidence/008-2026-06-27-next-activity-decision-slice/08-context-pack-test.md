# Context Pack Test Output

Command:

```bash
python3 scripts/test_context_pack.py
```

Output (truncated to final status):

```
StudyDD context pack test
=========================
StudyDD create-instance
=======================
...
Test: start_session includes canonical state and active study skill
StudyDD context pack built.

Task: start_session
Mode: session_boundary
Files included: 14
Files skipped: 3
Raw log files loaded: 0
Cache used: True
...
Test: context pack is gitignored

Running validator
StudyDD validation
==================

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.

Context pack test passed.
```

Result: **pass**.
