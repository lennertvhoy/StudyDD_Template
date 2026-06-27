# Instantiate Template Test Output

Command:

```bash
python3 scripts/test_instantiate_template.py
```

Output:

```
StudyDD instantiation smoke test
================================

1. Copying template to /tmp/studydd-instantiate-61imfus3/StudyDD_Instance
2. Removing template Git history and reinitializing Git
3. Switching to bootstrap mode
4. Running bootstrap validation
StudyDD validation
==================

Warnings:
  - Bootstrap mode: learner profile and first target are not initialized yet. Complete personalization and then switch mode to learner_instance.

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.

Bootstrap validation passed (warnings about incomplete personalization are expected).
5. Simulating minimal learner initialization
5b. Recording template origin metadata
6. Switching to learner_instance mode
7. Running learner_instance validation
StudyDD validation
==================

Warnings:
  - Active target 'bootstrap-smoke-target' does not declare a study_skill; generic tutoring will be used.
  - state/CURRENT_CONTEXT.md appears older than state/STUDY_STATE.yaml. Run scripts/compact_state.py.

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.

Learner instance validation passed.
8. Creating first commit
First commit created successfully.

Instantiation smoke test passed.
```

Result: **pass**.
