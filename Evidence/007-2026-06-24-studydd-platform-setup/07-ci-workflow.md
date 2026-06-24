# CI Workflow Update

Updated `.github/workflows/validate.yml`:

- Added a matrix strategy for `os: [ubuntu-latest, windows-latest, macos-latest]`.
- `fail-fast: false` so one OS failure does not cancel the others.
- Replaced the hard-coded `pip install pyyaml` with `pip install -r requirements.txt`.
- Runs on every OS:
  - `python scripts/check_environment.py`
  - `python scripts/test_cross_platform_paths.py`
- Runs the full validation/test/demo suite only on `ubuntu-latest` to keep the matrix lightweight.
- Kept `git diff --check` on Ubuntu.

This satisfies the requirement to validate cross-platform setup while keeping CI deterministic and fast.
