#!/usr/bin/env python3
"""Test StudyDD study skills.

Verifies required skill files exist, target-declared skills resolve correctly,
unknown skills fail validation in learner instance mode, and the context pack
includes the active study skill.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SKILLS = [
    "generic",
    "it_certification",
    "philosophy",
    "primary_math",
    "language_learning",
    "interview_prep",
    "practical_lab",
]


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def make_instance(skill: str | None) -> Path:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="studydd-skills-")
    target = Path(tmp) / "Study_Skills"
    remote = "https://github.com/example/Study_Skills.git"

    result = run(
        [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote],
        ROOT,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

    mode_path = target / "state" / "STUDYDD_MODE.yaml"
    mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
    mode_data["mode"] = "learner_instance"
    mode_data["personalized"] = True
    mode_data["public_safe"] = "false_or_review_required"
    mode_path.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")

    study_state_path = target / "state" / "STUDY_STATE.yaml"
    study_state = yaml.safe_load(study_state_path.read_text(encoding="utf-8")) or {}
    study_state["learner"]["name"] = "Skills Test Learner"
    study_state["active_target_id"] = "skills-target"
    study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

    target_dir = target / "targets" / "skills-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_yaml_text = (
        "---\n"
        "id: skills-target\n"
        "type: skill\n"
        "title: Skills test target\n"
        "description: Temporary target for study skills test.\n"
    )
    if skill:
        target_yaml_text += f"study_skill: {skill}\n"
    (target_dir / "TARGET.yaml").write_text(target_yaml_text, encoding="utf-8")

    return target


def main() -> int:
    print("StudyDD study skills test")
    print("=========================")

    print("\nTest: every required skill has a SKILL.md")
    for skill_id in REQUIRED_SKILLS:
        skill_file = ROOT / "study_skills" / skill_id / "SKILL.md"
        assert skill_file.is_file(), f"Missing study skill file: {skill_file}"
        text = skill_file.read_text(encoding="utf-8")
        for section in (
            "## Use when",
            "## Learning goal shape",
            "## Question types to prefer",
            "## Grading policy",
            "## Readiness upgrade rules",
        ):
            assert section in text, f"{skill_file} missing section {section}"
    print(f"All {len(REQUIRED_SKILLS)} required skills found.")

    print("\nTest: declared known skill resolves and context pack includes it")
    target = make_instance("it_certification")
    run([sys.executable, "scripts/compact_state.py"], target)
    result = run(
        [sys.executable, "scripts/build_context_pack.py", "--task", "start_session"],
        target,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return 1
    pack_text = (target / ".studydd" / "context_pack.md").read_text(encoding="utf-8")
    assert "**Study skill:** it_certification" in pack_text
    assert "study_skills/it_certification/SKILL.md" in pack_text

    val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(val.stdout)
    if val.returncode != 0:
        print(val.stderr)
        return 1

    print("\nTest: unknown skill fails validation in learner instance mode")
    target = make_instance("nonexistent_skill")
    val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(val.stdout)
    if val.returncode == 0:
        print("Expected validation to fail for unknown study skill")
        return 1
    assert "unknown study_skill" in val.stdout

    print("\nTest: demo replay shows active study skill")
    result = run([sys.executable, "scripts/run_demo_replay.py"], ROOT, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return 1
    assert "Active study skill: it_certification" in result.stdout
    assert "Built a context pack instead of loading every file" in result.stdout

    print("Study skills test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
