#!/usr/bin/env python3
"""Focused test for scripts/create_instance.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import shutil
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


def snapshot_tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


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
        source_identity = version_data.get("instance_created_from_template_source") or {}
        assert source_identity.get("origin") == "https://github.com/lennertvhoy/StudyDD_Template.git"
        assert source_identity.get("digest", "").startswith("sha256:")

        descriptor = yaml.safe_load((target / "instance.yaml").read_text(encoding="utf-8"))
        assert descriptor["spec"]["mode"] == "bootstrap"
        assert descriptor["spec"]["personalized"] is False
        assert "owner" not in descriptor["spec"]
        assert "learner" not in descriptor["spec"]
        assert "Lenny" not in (target / "instance.yaml").read_text(encoding="utf-8")

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


def test_regeneration_preserves_instance_state_and_template() -> None:
    """The local fallback is deterministic and does not rewrite the source."""
    with tempfile.TemporaryDirectory(prefix="studydd-create-instance-regenerate-") as tmp:
        workspace = Path(tmp)
        source = workspace / "template"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        run(["git", "init", "-b", "main"], source)
        run(["git", "config", "user.name", "StudyDD Test"], source)
        run(["git", "config", "user.email", "test@example.invalid"], source)
        run(["git", "remote", "add", "origin", "https://github.com/lennertvhoy/StudyDD_Template.git"], source)
        run(["git", "add", "."], source)
        run(["git", "commit", "-m", "test template"], source)

        before = snapshot_tree(source)
        target = workspace / "instance"
        result = run(
            [
                sys.executable,
                "scripts/create_instance.py",
                "--target",
                str(target),
                "--remote",
                "https://github.com/example/Study_CreateInstanceRegenerate.git",
            ],
            source,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

        learner_profile = target / "state" / "LEARNER_PROFILE.yaml"
        learner_profile.write_text(
            learner_profile.read_text(encoding="utf-8") + "\n# synthetic instance-owned edit\n",
            encoding="utf-8",
        )
        synthetic_target = target / "targets" / "synthetic"
        synthetic_target.mkdir(parents=True)
        (synthetic_target / "TARGET.yaml").write_text(
            "id: synthetic\nname: Synthetic test target\n", encoding="utf-8"
        )
        profile_after_edit = learner_profile.read_bytes()
        descriptor_before = (target / "instance.yaml").read_bytes()

        regenerated = run(
            [
                sys.executable,
                "scripts/create_instance.py",
                "--target",
                str(target),
                "--template",
                str(source),
                "--regenerate",
            ],
            target,
            check=False,
        )
        assert regenerated.returncode == 0, regenerated.stdout + regenerated.stderr
        assert learner_profile.read_bytes() == profile_after_edit
        assert (synthetic_target / "TARGET.yaml").read_text(encoding="utf-8").startswith("id: synthetic")
        assert (target / "instance.yaml").read_bytes() == descriptor_before
        assert snapshot_tree(source) == before


def main_with_focused_tests() -> int:
    main_result = main()
    if main_result != 0:
        return main_result
    test_regeneration_preserves_instance_state_and_template()
    print("regeneration test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main_with_focused_tests())
