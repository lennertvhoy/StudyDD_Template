# Demo Replay Transcript — StudyDD Demo Path v1

**Date:** 2026-06-24

```bash
python3 scripts/run_demo_replay.py
```

Output:

```text
StudyDD demo replay
===================

1. Created learner instance from template.
2. Initialized learner profile: Demo Learner.
3. Initialized target: AI Search Fundamentals Demo.
4. Agent asked one question: Q-DEMO-001.
5. Learner answered: distinguished keyword and vector search, no scenario.
6. Agent graded honestly: partial.
7. Evidence recorded: ev_demo_001.
8. Review scheduled: rev_demo-search-basics_20260624_100000 due in 1 day.
9. Selector before due: new material is allowed.
    StudyDD recommendation: new material is allowed.
10. Selector when review is due: review first.
     StudyDD recommendation: review first.
11. Learner override recorded with reason.
12. Validation passed.

The repo now contains evidence, a spaced-repetition review, an override log,
and a clear next action. Run `python3 scripts/check_studydd.py` in the instance
to verify repo health at any time.
```

The replay ran deterministically in a temporary directory without touching any private learner repo.
