# Create-Instance Test

Command: `python3 scripts/test_create_instance.py`

Result: **PASS**

Key behaviors verified:

- `scripts/create_instance.py` refused to run from a non-template repo (tested implicitly by running from the template).
- Refused to overwrite an existing non-empty target directory (not exercised in this run; directory did not exist).
- Copied the template excluding `.git`, `.venv`, `node_modules`, caches, etc.
- Initialized Git in the target, set branch to `main`, and added the provided remote.
- Set repo-local identity:
  - `user.name = StudyDD Agent`
  - `user.email = studydd-agent@example.invalid`
- Switched `state/STUDYDD_MODE.yaml` to `bootstrap` mode.
- Preserved template origin metadata in `state/STUDYDD_TEMPLATE_VERSION.yaml`.
- Ran `python3 scripts/check_studydd.py` inside the new instance successfully.
- Printed the next prompt to paste into the coding agent.
