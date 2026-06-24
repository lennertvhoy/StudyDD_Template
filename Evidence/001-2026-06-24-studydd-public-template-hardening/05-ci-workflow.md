# CI Workflow Presence

Created `.github/workflows/validate.yml`.

Triggers:

- Push to `main`
- Pull request to `main`

Permissions: `contents: read` only.

Steps:

1. Checkout with `actions/checkout@v4`.
2. Set up Python 3.11 with `actions/setup-python@v5`.
3. Install `pyyaml`.
4. Run `python3 scripts/check_studydd.py`.
5. Run `python3 scripts/test_instantiate_template.py`.
6. Run `python3 scripts/test_study_loop_smoke.py`.
7. Run `git diff --check`.
