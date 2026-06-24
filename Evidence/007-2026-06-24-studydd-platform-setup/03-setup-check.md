# Setup Check Output

Command:

```bash
python scripts/setup_studydd.py --check
```

Output:

```
StudyDD setup check
===================

This script will:
  - check your Python version and virtual environment
  - read dependencies from requirements.txt
  - (only with --install) run `pip install -r requirements.txt`

Dependency manifest: /home/ff/Documents/Projects/StudyDD/requirements.txt
Required packages:
  - PyYAML>=6.0,<7.0

Active interpreter: /usr/bin/python
Inside virtual environment: no
PyYAML status: installed

WARNING: you are not inside a virtual environment.
Installing into the system or user Python can affect other projects.
Recommended: create and activate a virtual environment first.
  Linux/macOS: python3 -m venv .venv && source .venv/bin/activate
  Windows PS:  py -m venv .venv && .\.venv\Scripts\Activate.ps1

Next step:
  python scripts/setup_studydd.py --install
```

Result: **pass**. The script correctly reports dependencies, warns about the missing virtual environment, and does not install anything.
