# StudyDD Setup Guide

StudyDD runs on Linux, macOS, and Windows PowerShell. It uses plain Python and a small set of Python packages. This guide shows how to create a local virtual environment, install dependencies, and run validation.

> **No surprise installs.** StudyDD will never install software without your explicit consent. The helper scripts only check your environment and print next steps unless you explicitly run the install command.

## Supported platforms

- Linux (most distributions)
- macOS
- Windows PowerShell

## Requirements

- Python 3.10 or newer
- Git
- Internet connection (only to download PyYAML from PyPI when you choose to install)

## Quick start (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/check_studydd.py
python scripts/run_demo_replay.py
```

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/check_studydd.py
python scripts/run_demo_replay.py
```

If `py` is not available on Windows, use `python` or `python3` instead, depending on what is installed.

## Check your environment first

You can check whether your machine is ready before installing anything:

```bash
python scripts/check_environment.py
```

The checker prints:

- operating system
- Python version
- whether the Python version is supported
- whether required packages are installed
- whether you are inside a virtual environment
- whether Git is available
- whether you are in the repo root

It exits with a non-zero status if required dependencies are missing, but it **never installs anything**.

## Install with explicit consent

If the environment check reports missing packages, run the setup helper:

```bash
python scripts/setup_studydd.py --check
```

This prints what would be installed and asks whether to continue. To install after reviewing the plan:

```bash
python scripts/setup_studydd.py --install
```

The helper:

- installs only the packages listed in `requirements.txt`
- installs only into the active Python environment
- warns strongly if you are not inside a virtual environment
- never uses `sudo`
- never uses `apt`, `dnf`, `brew`, `choco`, or any other system package manager
- asks for explicit confirmation before any change

## Run validation

After setup, run the repo health gate:

```bash
python scripts/check_studydd.py
```

You can also run the full test suite used by CI:

```bash
python scripts/test_instantiate_template.py
python scripts/test_create_instance.py
python scripts/test_study_loop_smoke.py
python scripts/test_demo_replay.py
python scripts/test_learning_activities.py
python scripts/test_source_freshness.py
python scripts/test_question_quality.py
python scripts/test_learner_adaptation.py
```

## Run the demo replay

The demo replay creates a temporary learner instance and walks through one full StudyDD learning loop. It does not touch your repo state.

```bash
python scripts/run_demo_replay.py
```

## Troubleshooting

### `python` or `python3` is not found

Use the exact name of the Python interpreter on your system. On Windows, `py` is usually the launcher. On Linux and macOS, try `python3` first.

### `pip` is not found

Use `python -m pip` or `python3 -m pip` instead of running `pip` directly. This guarantees you are installing into the interpreter you intend to use.

### PyYAML install fails

StudyDD requires PyYAML for YAML parsing. If installation fails:

1. Make sure you are inside the virtual environment.
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Try the install again: `python -m pip install -r requirements.txt`

If you are on a system without a C compiler, install a pre-built wheel from PyPI.

### Virtual environment activation fails on Windows

If PowerShell refuses to run the activation script, you may need to allow scripts for the current session:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Git is not found

Install Git from your platform package manager or from <https://git-scm.com/downloads>. StudyDD uses Git only for local provenance checks and CI; it does not require a specific Git version.

### Files inside `.studydd/` are showing as untracked

The `.studydd/` directory contains generated context packs and cache files. It is listed in `.gitignore` and should not be committed.

## Consent policy

StudyDD does not install dependencies, change system settings, or modify files outside the repo without your explicit consent. The setup helper explains every change and asks before writing anything. You can inspect `scripts/setup_studydd.py` and `requirements.txt` before running them.
