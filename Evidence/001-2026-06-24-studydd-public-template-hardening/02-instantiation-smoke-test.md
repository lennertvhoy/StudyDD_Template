# Instantiation Smoke Test

Command: `python3 scripts/test_instantiate_template.py`

Result: **PASS**

Key behaviors verified:

- Template copied to a temporary directory.
- Template `.git/` history removed.
- Git reinitialized with `main` branch.
- Repo-local identity set before first commit:
  - `user.name = StudyDD Smoke Test`
  - `user.email = studydd-smoke-test@example.invalid`
- Bootstrap mode validation passed.
- Minimal learner initialization succeeded.
- Learner-instance mode validation passed.
- First commit created without relying on global Git config.
- Template origin/version metadata recorded in `state/STUDYDD_TEMPLATE_VERSION.yaml`.
