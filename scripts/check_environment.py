#!/usr/bin/env python3
"""Check whether the current environment can run StudyDD.

Prints OS, Python version, package status, virtualenv status, Git status, and
repo-root status. Exits with a non-zero code if required dependencies are
missing. This script never installs anything.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PYTHON = (3, 10)
REQUIRED_PACKAGES = ["yaml"]  # import name for PyYAML


def in_virtual_environment() -> bool:
    """Return True if running inside a Python virtual environment."""
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or sys.prefix != sys.base_prefix
    )


def python_version_ok() -> tuple[bool, str]:
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if (version.major, version.minor) >= REQUIRED_PYTHON:
        return True, version_str
    return False, version_str


def check_packages() -> tuple[list[str], list[str]]:
    """Return (missing_import_names, installed_import_names)."""
    missing: list[str] = []
    installed: list[str] = []
    for name in REQUIRED_PACKAGES:
        try:
            __import__(name)
            installed.append(name)
        except ImportError:
            missing.append(name)
    return missing, installed


def git_available() -> bool:
    return shutil.which("git") is not None


def in_repo_root() -> bool:
    marker_files = [
        "README.md",
        "AGENTS.md",
        "scripts/check_studydd.py",
        "state/STUDYDD_MODE.yaml",
    ]
    return all((ROOT / name).is_file() for name in marker_files)


def git_remote_includes_template() -> bool:
    if not git_available():
        return False
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return "StudyDD_Template" in result.stdout
    except Exception:
        return False


def read_template_version() -> str:
    version_path = ROOT / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    version = "unknown"
    try:
        import yaml

        data = yaml.safe_load(version_path.read_text(encoding="utf-8")) or {}
        version = data.get("template_version", "unknown")
    except Exception:
        pass
    return version


def main() -> int:
    print("StudyDD environment check")
    print("=========================")
    print("")

    print(f"Platform: {platform.system()} ({platform.release()})")
    print(f"Machine: {platform.machine()}")

    ok, version = python_version_ok()
    print(f"Python version: {version}")
    if ok:
        print("  Python version: OK")
    else:
        print(f"  Python version: too old (need {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+)")

    print(f"Interpreter: {sys.executable}")
    print(f"Virtual environment: {'yes' if in_virtual_environment() else 'no'}")

    missing_packages, installed_packages = check_packages()
    print("Required packages:")
    for name in installed_packages:
        print(f"  {name}: installed")
    for name in missing_packages:
        print(f"  {name}: MISSING")

    print(f"Git available: {'yes' if git_available() else 'no'}")
    print(f"Repo root: {'yes' if in_repo_root() else 'no'}")
    if git_remote_includes_template():
        print("Git remote: StudyDD_Template detected")
    print(f"Template version: {read_template_version()}")

    print("")
    if missing_packages or not ok:
        print("Next steps:")
        if not ok:
            print(f"  - Install Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} or newer.")
        if missing_packages:
            print("  - Create a virtual environment:")
            print("      Linux/macOS: python3 -m venv .venv && source .venv/bin/activate")
            print("      Windows PS:  py -m venv .venv && .\\.venv\\Scripts\\Activate.ps1")
            print("  - Install dependencies:")
            print("      python -m pip install -r requirements.txt")
            print("  - Or run the setup helper with explicit consent:")
            print("      python scripts/setup_studydd.py --check")
        return 1

    if not git_available():
        print("Next steps:")
        print("  - Install Git: https://git-scm.com/downloads")
        return 1

    if not in_repo_root():
        print("Next steps:")
        print(f"  - Run this script from the StudyDD repo root ({ROOT}).")
        return 1

    if not in_virtual_environment():
        print("Warning: you are not inside a virtual environment.")
        print("StudyDD works best in a local venv. To create one:")
        print("  Linux/macOS: python3 -m venv .venv && source .venv/bin/activate")
        print("  Windows PS:  py -m venv .venv && .\\.venv\\Scripts\\Activate.ps1")
        print("")

    print("Environment check passed. StudyDD should run.")
    print("Run validation: python scripts/check_studydd.py")
    print("Run demo:       python scripts/run_demo_replay.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
