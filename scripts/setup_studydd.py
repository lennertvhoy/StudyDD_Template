#!/usr/bin/env python3
"""StudyDD setup helper with explicit consent.

This script checks the environment and, with explicit user confirmation,
installs the dependencies from requirements.txt into the active Python
environment. It never uses sudo or system package managers.

Usage:
    python scripts/setup_studydd.py --check
    python scripts/setup_studydd.py --install
    python scripts/setup_studydd.py --install --yes   # non-interactive confirmation
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_PATH = ROOT / "requirements.txt"


def in_virtual_environment() -> bool:
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or sys.prefix != sys.base_prefix
    )


def run_check() -> int:
    print("StudyDD setup check")
    print("===================")
    print("")
    print("This script will:")
    print("  - check your Python version and virtual environment")
    print("  - read dependencies from requirements.txt")
    print("  - (only with --install) run `pip install -r requirements.txt`")
    print("")

    if not REQUIREMENTS_PATH.is_file():
        print(f"Missing dependency manifest: {REQUIREMENTS_PATH}")
        return 1

    print(f"Dependency manifest: {REQUIREMENTS_PATH}")
    print("Required packages:")
    for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            print(f"  - {stripped}")

    print("")
    print(f"Active interpreter: {sys.executable}")
    print(f"Inside virtual environment: {'yes' if in_virtual_environment() else 'no'}")

    try:
        import yaml  # noqa: F401

        print("PyYAML status: installed")
    except ImportError:
        print("PyYAML status: NOT installed")

    print("")
    if in_virtual_environment():
        print("Environment looks ready for install.")
    else:
        print("WARNING: you are not inside a virtual environment.")
        print("Installing into the system or user Python can affect other projects.")
        print("Recommended: create and activate a virtual environment first.")
        print("  Linux/macOS: python3 -m venv .venv && source .venv/bin/activate")
        print("  Windows PS:  py -m venv .venv && .\\.venv\\Scripts\\Activate.ps1")

    print("")
    print("Next step:")
    print("  python scripts/setup_studydd.py --install")
    return 0


def read_requirements() -> list[str]:
    if not REQUIREMENTS_PATH.is_file():
        print(f"Missing dependency manifest: {REQUIREMENTS_PATH}")
        return []
    packages: list[str] = []
    for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            packages.append(stripped)
    return packages


def ask_confirm(message: str, auto_confirm: bool) -> bool:
    if auto_confirm:
        print(f"{message} (auto-confirmed via --yes)")
        return True
    try:
        answer = input(f"{message} [yes/no]: ").strip().lower()
    except EOFError:
        print("No input available. Use --yes for non-interactive confirmation.")
        return False
    return answer in ("yes", "y")


def run_install(auto_confirm: bool) -> int:
    print("StudyDD setup install")
    print("=====================")
    print("")

    packages = read_requirements()
    if not packages:
        return 1

    print("This will install the following packages into the ACTIVE Python environment:")
    print(f"  {sys.executable}")
    print("")
    for pkg in packages:
        print(f"  - {pkg}")
    print("")
    print("Rules:")
    print("  - no sudo")
    print("  - no apt/dnf/brew/choco")
    print("  - only the active Python environment is modified")
    print("")

    if not in_virtual_environment():
        print("WARNING: you are NOT inside a virtual environment.")
        print("This will install into your system or user Python environment.")
        if not ask_confirm("Do you want to continue anyway?", auto_confirm):
            print("Install cancelled.")
            return 1
    else:
        if not ask_confirm("Do you want to install these packages?", auto_confirm):
            print("Install cancelled.")
            return 1

    cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)]
    print("")
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print("Install failed.")
        return result.returncode

    print("")
    print("Install complete.")
    print("Run validation: python scripts/check_studydd.py")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StudyDD setup helper with explicit consent"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check environment and print next steps without installing",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies after explicit confirmation",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm install non-interactively (use with --install)",
    )
    args = parser.parse_args()

    if args.check and args.install:
        print("Use either --check or --install, not both.")
        return 1

    if not args.check and not args.install:
        print("StudyDD setup helper")
        print("")
        print("Run with --check to see what would be installed.")
        print("Run with --install to install after explicit confirmation.")
        return 0

    if args.check:
        return run_check()

    if args.install:
        return run_install(auto_confirm=args.yes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
