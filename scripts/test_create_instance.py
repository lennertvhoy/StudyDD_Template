#!/usr/bin/env python3
"""Focused test for scripts/create_instance.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def main() -> int:
    print("StudyDD create-instance test")
    print("============================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    with tempfile.TemporaryDirectory(prefix="studydd-create-instance-") as tmp:
        target = Path(tmp) / "Study_CreateInstanceSmoke"
        remote = "https://github.com/example/Study_CreateInstanceSmoke.git"

        result = run(
            [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote],
            ROOT,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("create_instance.py failed.")
            return 1

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8"))
        assert mode_data.get("mode") == "bootstrap", f"expected bootstrap, got {mode_data.get('mode')}"

        version_path = target / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
        version_data = yaml.safe_load(version_path.read_text(encoding="utf-8"))
        assert version_data.get("instance_created_from_template_version"), "missing origin version"
        assert version_data.get("last_template_upgrade_version"), "missing last upgrade version"

        remotes = run(["git", "remote", "-v"], target).stdout
        assert remote in remotes, f"remote not found: {remotes}"

        assert (target / ".git").is_dir(), ".git missing"

        val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
        print(val.stdout)
        if val.returncode != 0:
            print(val.stderr)
            print("Validation failed.")
            return 1

        print("create-instance test passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
