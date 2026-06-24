#!/usr/bin/env python3
"""Smoke test for the StudyDD template -> bootstrap -> learner_instance lifecycle.

This script creates a temporary copy of the current repo, removes the template
Git history, reinitializes Git, runs through bootstrap validation, simulates
minimal learner initialization, switches to learner_instance mode, runs full
validation, and then cleans up.

Requires PyYAML (same as scripts/check_studydd.py).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    print("StudyDD instantiation smoke test")
    print("================================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required for this smoke test.")
        print("Install with: pip install pyyaml")
        return 1

    with tempfile.TemporaryDirectory(prefix="studydd-instantiate-") as tmp:
        instance = Path(tmp) / "StudyDD_Instance"

        # 1. Copy the template into a fresh directory.
        print(f"\n1. Copying template to {instance}")
        shutil.copytree(
            ROOT,
            instance,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".venv",
                "node_modules",
                "*.pyc",
            ),
        )

        # 2. Remove any leftover .git/ and reinitialize Git.
        print("2. Removing template Git history and reinitializing Git")
        git_dir = instance / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        result = run(["git", "init"], instance)
        if result.returncode != 0:
            print(result.stderr)
            return 1

        result = run(["git", "branch", "-M", "main"], instance)
        if result.returncode != 0:
            print(result.stderr)
            return 1

        result = run(
            ["git", "remote", "add", "origin", "https://github.com/lennertvhoy/Study_Lenny.git"],
            instance,
        )
        if result.returncode != 0:
            print(result.stderr)
            return 1

        # 3. Switch to bootstrap mode.
        print("3. Switching to bootstrap mode")
        mode_path = instance / "state" / "STUDYDD_MODE.yaml"
        mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
        mode_data["mode"] = "bootstrap"
        mode_data.setdefault("template_origin", "https://github.com/lennertvhoy/StudyDD_Template.git")
        mode_data["personalized"] = False
        mode_data["public_safe"] = "false_or_review_required"
        mode_path.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")

        # 4. Run bootstrap-safe validation.
        print("4. Running bootstrap validation")
        result = run([sys.executable, "scripts/check_studydd.py"], instance)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("Bootstrap validation failed.")
            return 1
        print("Bootstrap validation passed (warnings about incomplete personalization are expected).")

        # 5. Simulate minimal learner initialization.
        print("5. Simulating minimal learner initialization")
        state_path = instance / "state" / "STUDY_STATE.yaml"
        study_state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
        study_state["learner"]["name"] = "Smoke Test Learner"
        study_state["active_target_id"] = "bootstrap-smoke-target"
        state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

        target_dir = instance / "targets" / "bootstrap-smoke-target"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_yaml = target_dir / "TARGET.yaml"
        target_yaml.write_text(
            "---\n"
            "id: bootstrap-smoke-target\n"
            "type: skill\n"
            "title: Bootstrap smoke target\n"
            "description: Temporary target used only for instantiation smoke test.\n",
            encoding="utf-8",
        )

        # 6. Switch to learner_instance mode.
        print("6. Switching to learner_instance mode")
        mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        mode_data["public_safe"] = "false_or_review_required"
        mode_path.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")

        # 7. Run full learner-instance validation.
        print("7. Running learner_instance validation")
        result = run([sys.executable, "scripts/check_studydd.py"], instance)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("Learner instance validation failed.")
            return 1
        print("Learner instance validation passed.")

        # 8. Verify a first commit can be created.
        print("8. Creating first commit")
        result = run(["git", "add", "."], instance)
        if result.returncode != 0:
            print(result.stderr)
            return 1
        result = run(["git", "commit", "-m", "chore: initialize StudyDD learner instance"], instance)
        if result.returncode != 0:
            print(result.stderr)
            return 1
        print("First commit created successfully.")

    print("\nInstantiation smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
