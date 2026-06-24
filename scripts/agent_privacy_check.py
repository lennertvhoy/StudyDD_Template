#!/usr/bin/env python3
"""Practical privacy scan for a StudyDD learner instance.

Warns by default. Run before pushing a learner instance to a public or shared
remote. The template repo itself may contain generic placeholder emails; those
are flagged as warnings, not hard failures.

Usage:
    python3 scripts/agent_privacy_check.py [--fail]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Generic template placeholders that are not private learner data.
ALLOWLIST = {
    "studydd-agent@example.invalid",
    "studydd-smoke-test@example.invalid",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
SECRET_RE = re.compile(
    r"(?i)("
    r"password\s*[:=]\s*[\"']?[^\"'\s]+"
    r"|api[_-]?key\s*[:=]\s*[\"']?[^\"'\s]+"
    r"|secret[_-]?key\s*[:=]\s*[\"']?[^\"'\s]+"
    r"|token\s*[:=]\s*[\"']?[^\"'\s]+"
    r"|private[_-]?key\s*[:=]\s*[\"']?[^\"'\s]+"
    r")"
)

SENSITIVE_KEYWORDS = [
    "ssn",
    "social security",
    "credit card",
    "passport",
    "api_key",
    "apikey",
    "private_key",
    "recovery phrase",
    "health condition",
    "medical",
]

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".yaml", ".yml", ".txt", ".py", ".json"}


def check_file(path: Path) -> list[str]:
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return warnings

    rel = path.relative_to(ROOT)

    for match in EMAIL_RE.finditer(text):
        email = match.group(0)
        if email in ALLOWLIST:
            continue
        warnings.append(f"{rel}: possible email '{email}'")

    for match in PHONE_RE.finditer(text):
        warnings.append(f"{rel}: possible phone number '{match.group(0)}'")

    if SECRET_RE.search(text):
        warnings.append(f"{rel}: possible credential/secret pattern")

    lower = text.lower()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in lower:
            warnings.append(f"{rel}: contains keyword '{keyword}'")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Privacy scan for StudyDD")
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit non-zero if any warning is found.",
    )
    args = parser.parse_args()

    print("StudyDD privacy check")
    print("=====================")

    all_warnings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if not is_text_file(path):
            continue
        all_warnings.extend(check_file(path))

    if all_warnings:
        print("\nWarnings:")
        for warn in all_warnings:
            print(f"  - {warn}")
        if args.fail:
            print("\nPrivacy check failed.")
            return 1
        print("\nPrivacy check completed with warnings (soft mode).")
        return 0

    print("\nNo obvious privacy-sensitive patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
