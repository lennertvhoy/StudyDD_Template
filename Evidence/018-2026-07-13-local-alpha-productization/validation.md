# Validation

- `python3 -m pytest -q scripts`: 130 passed.
- `python3 scripts/check_studydd.py`: passed.
- `python3 scripts/validate_manifest.py`: passed (315 current tracked paths,
  46 manifest assets, 4 selected modules).
- compatibility, demo replay, privacy, and diff checks passed.

The privacy checker reported only existing soft warnings for checker keywords
and synthetic invalid-address fixtures; no secret or learner data was added.
