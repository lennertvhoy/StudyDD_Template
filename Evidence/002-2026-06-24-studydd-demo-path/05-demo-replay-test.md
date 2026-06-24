# Demo Replay Test Pass — StudyDD Demo Path v1

**Date:** 2026-06-24

```bash
python3 scripts/test_demo_replay.py
```

Result: **passed**.

The test ran `scripts/run_demo_replay.py` and asserted that the transcript contains the expected demo steps, that the temporary instance was created, and that validation passed.

Key assertions verified:

- "Created learner instance" appears in transcript
- "Initialized learner profile: Demo Learner" appears
- "Initialized target: AI Search Fundamentals Demo" appears
- "Agent asked one question" appears
- "Learner answered" appears
- "Agent graded honestly: partial" appears
- "Evidence recorded: ev_demo_001" appears
- "Review scheduled" appears
- "Selector when review is due: review first" appears
- "Learner override recorded with reason" appears
- "Validation passed" appears

Output:

```text
Demo replay test passed.
```
