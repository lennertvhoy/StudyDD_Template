# CI Workflow Update — StudyDD Demo Path v1

**Date:** 2026-06-24

Updated `.github/workflows/validate.yml` to run the new demo replay test on every push and pull request:

```yaml
      - name: Run study-loop smoke test
        run: python3 scripts/test_study_loop_smoke.py

      - name: Run demo replay test
        run: python3 scripts/test_demo_replay.py

      - name: Check whitespace
        run: git diff --check
```

The CI pipeline now validates:

1. `python3 scripts/check_studydd.py`
2. `python3 scripts/test_instantiate_template.py`
3. `python3 scripts/test_study_loop_smoke.py`
4. `python3 scripts/test_demo_replay.py`
5. `git diff --check`
