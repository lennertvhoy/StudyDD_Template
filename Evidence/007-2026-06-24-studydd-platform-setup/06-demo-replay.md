# Demo Replay Output

Command:

```bash
python scripts/run_demo_replay.py
```

Final transcript output:

```
StudyDD demo replay
===================

1. Created learner instance from template.
2. Initialized learner profile: Demo Learner.
3. Initialized target: AI Search Fundamentals Demo.
4. Active study skill: it_certification.
5. Built a context pack instead of loading every file.
6. StudyDD uses the fast path during ordinary tutoring turns.
7. Only relevant state is loaded.
8. Only touched files are updated.
9. Full validation runs at session boundary.
10. Agent asked one question: Q-DEMO-001.
11. Learner answered: distinguished keyword and vector search, no scenario.
12. Agent graded honestly: partial.
13. Evidence recorded: ev_demo_001.
14. StudyDD planned a non-question activity based on the weak skill.
15. Learner completed the activity outside the chat and submitted evidence.
16. StudyDD reviewed the submitted evidence and updated state.
17. Review scheduled: rev_demo-search-basics_20260624_100000 due in 1 day.
18. Selector before due: new material is allowed.
19. Selector when review is due: review first.
20. Learner override recorded with reason.
21. Validation passed.
```

Result: **pass**. Demo replay works with the new setup scripts and dependency manifest in place.
