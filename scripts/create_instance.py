#!/usr/bin/env python3
"""Create a deterministic StudyDD learner instance from the public template.

Usage:
    python3 scripts/create_instance.py \
        --target ../Study_MyTarget \
        --remote https://github.com/example/Study_MyTarget.git
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AGENT_NAME = "StudyDD Agent"
AGENT_EMAIL = "studydd-agent@example.invalid"
TEMPLATE_ORIGIN = "https://github.com/lennertvhoy/StudyDD_Template.git"


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"  cwd: {cwd}")
        print(f"  stderr: {result.stderr.strip()}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def is_non_empty_dir(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.is_dir():
        return False
    for child in path.iterdir():
        if child.name != ".git":
            return True
    return False


def get_template_version_and_commit(yaml: object) -> tuple[str, str]:
    version_path = ROOT / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    data = yaml.safe_load(version_path.read_text(encoding="utf-8")) or {}
    version = data.get("template_version", "unknown")

    commit = ""
    try:
        commit = run(["git", "rev-parse", "HEAD"], ROOT, check=False).stdout.strip()
    except Exception:
        pass
    return version, commit


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a StudyDD learner instance")
    parser.add_argument("--target", required=True, help="Target directory for the instance")
    parser.add_argument("--remote", required=True, help="Git remote URL for the instance")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    remote = args.remote

    print("StudyDD create-instance")
    print("=======================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    # 1. Verify current repo is template mode.
    mode_path = ROOT / "state" / "STUDYDD_MODE.yaml"
    mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
    if mode_data.get("mode") != "template":
        print(f"Error: current repo is not in template mode (mode={mode_data.get('mode')}).")
        return 1

    remotes = run(["git", "remote", "-v"], ROOT, check=False).stdout
    if "StudyDD_Template" not in remotes:
        print("Error: current repo does not appear to be the StudyDD_Template remote.")
        return 1

    # 2. Refuse to overwrite existing non-empty target.
    if is_non_empty_dir(target):
        print(f"Error: target directory already exists and is not empty: {target}")
        return 1
    if target.exists() and target.is_file():
        print(f"Error: target path is a file: {target}")
        return 1

    # 3. Copy template excluding caches and git history.
    print(f"1. Copying template to {target}")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        ROOT,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
        ),
    )

    copied_git = target / ".git"
    if copied_git.exists():
        shutil.rmtree(copied_git)

    # 4. Initialize Git.
    print("2. Initializing Git")
    try:
        run(["git", "init", "-b", "main"], target)
    except subprocess.CalledProcessError:
        run(["git", "init"], target)
        try:
            run(["git", "checkout", "-b", "main"], target)
        except subprocess.CalledProcessError:
            run(["git", "branch", "-M", "main"], target)

    run(["git", "config", "user.name", AGENT_NAME], target)
    run(["git", "config", "user.email", AGENT_EMAIL], target)
    run(["git", "remote", "add", "origin", remote], target)

    # 5. Switch mode to bootstrap.
    print("3. Switching to bootstrap mode")
    target_mode_path = target / "state" / "STUDYDD_MODE.yaml"
    target_mode_data = yaml.safe_load(target_mode_path.read_text(encoding="utf-8")) or {}
    target_mode_data["mode"] = "bootstrap"
    target_mode_data["template_origin"] = TEMPLATE_ORIGIN
    target_mode_data["personalized"] = False
    target_mode_data["public_safe"] = "false_or_review_required"
    target_mode_path.write_text(yaml.safe_dump(target_mode_data, sort_keys=False), encoding="utf-8")

    # 6. Preserve template origin metadata.
    print("4. Recording template origin metadata")
    template_version, template_commit = get_template_version_and_commit(yaml)
    version_path = target / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    version_data = yaml.safe_load(version_path.read_text(encoding="utf-8")) or {}
    version_data["instance_created_from_template_version"] = template_version
    version_data["instance_created_from_template_commit"] = template_commit
    version_data["last_template_upgrade_version"] = template_version
    version_data["last_template_upgrade_commit"] = template_commit
    version_path.write_text(yaml.safe_dump(version_data, sort_keys=False), encoding="utf-8")

    # 7. Run bootstrap validation.
    print("5. Running bootstrap validation")
    result = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("Bootstrap validation failed.")
        return 1
    print("Bootstrap validation passed.")

    # 8. Print next prompt.
    prompt_path = target / "PROMPTS" / "coding_agent_start_prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    print("\nNext step: open the new instance in your coding agent and paste the following prompt:")
    print(f"\n{prompt_text}\n")

    print(f"Instance created at: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
