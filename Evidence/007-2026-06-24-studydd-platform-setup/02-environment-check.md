# Environment Check Output

Command:

```bash
python scripts/check_environment.py
```

Output:

```
StudyDD environment check
=========================

Platform: Linux (7.0.12-201.fc44.x86_64)
Machine: x86_64
Python version: 3.14.5
  Python version: OK
Interpreter: /usr/bin/python
Virtual environment: no
Required packages:
  yaml: installed
Git available: yes
Repo root: yes
Git remote: StudyDD_Template detected
Template version: 0.10.0

Warning: you are not inside a virtual environment.
StudyDD works best in a local venv. To create one:
  Linux/macOS: python3 -m venv .venv && source .venv/bin/activate
  Windows PS:  py -m venv .venv && .\.venv\Scripts\Activate.ps1

Environment check passed. StudyDD should run.
Run validation: python scripts/check_studydd.py
Run demo:       python scripts/run_demo_replay.py
```

Result: **pass** (exit code 0).
