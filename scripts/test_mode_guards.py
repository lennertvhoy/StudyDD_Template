#!/usr/bin/env python3
"""Regression tests for executable template/instance mode boundaries."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_REMOTE = "https://github.com/lennertvhoy/StudyDD_Template.git"
REPO_COUNTER = 0
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def set_mode(repo: Path, mode: str) -> None:
    path = repo / "state" / "STUDYDD_MODE.yaml"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("mode:"):
            lines[index] = f"mode: {mode}"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_repo(tmp: Path, mode: str = "template", remote: str = TEMPLATE_REMOTE) -> Path:
    global REPO_COUNTER
    REPO_COUNTER += 1
    repo = tmp / f"repo-{mode}-{REPO_COUNTER}"
    shutil.copytree(
        ROOT,
        repo,
        ignore=shutil.ignore_patterns(".git", ".studydd", "__pycache__", "*.pyc"),
    )
    result = run(["git", "init", "-b", "main"], repo)
    assert result.returncode == 0, result.stderr
    result = run(["git", "remote", "add", "origin", remote], repo)
    assert result.returncode == 0, result.stderr
    set_mode(repo, mode)
    return repo


def test_mode_contract(tmp: Path) -> None:
    from studydd.mode import (
        ModeViolation,
        RepoMode,
        load_repo_mode,
        normalized_remote,
        require_mode,
    )

    assert [load_repo_mode(make_repo(tmp, mode)) for mode in ("template", "bootstrap", "learner_instance")] == [
        RepoMode.TEMPLATE,
        RepoMode.BOOTSTRAP,
        RepoMode.LEARNER_INSTANCE,
    ]
    assert normalized_remote(TEMPLATE_REMOTE) == normalized_remote("git@github.com:lennertvhoy/StudyDD_Template.git")
    assert normalized_remote("https://github.com/lennertvhoy/StudyDD_Template.git/") == normalized_remote(TEMPLATE_REMOTE)
    assert normalized_remote("https://github.com/example/StudyDD_Template.git") != normalized_remote(TEMPLATE_REMOTE)

    with tempfile.TemporaryDirectory(prefix="studydd-mode-contract-") as raw:
        tmp = Path(raw)
        template = make_repo(tmp, "template")
        assert require_mode(template, RepoMode.TEMPLATE, operation="maintain template") is RepoMode.TEMPLATE

        mismatched_template = make_repo(tmp, "template", "https://github.com/example/other.git")
        try:
            require_mode(mismatched_template, RepoMode.TEMPLATE, operation="maintain template")
        except ModeViolation as exc:
            assert exc.code == "MODE_REMOTE_MISMATCH"
        else:
            raise AssertionError("template mode accepted a non-template remote")

        learner_with_template_remote = make_repo(tmp, "learner_instance")
        try:
            require_mode(learner_with_template_remote, RepoMode.LEARNER_INSTANCE, operation="study")
        except ModeViolation as exc:
            assert exc.code == "MODE_REMOTE_MISMATCH"
        else:
            raise AssertionError("learner mode accepted the template remote")

        learner = make_repo(tmp, "learner_instance", "git@github.com:example/learner.git")
        assert require_mode(learner, RepoMode.LEARNER_INSTANCE, operation="study") is RepoMode.LEARNER_INSTANCE

        missing = tmp / "missing"
        (missing / "state").mkdir(parents=True)
        try:
            load_repo_mode(missing)
        except ModeViolation as exc:
            assert exc.code == "MODE_FILE_MISSING"
        else:
            raise AssertionError("missing mode file did not fail closed")

        set_mode(learner, "unknown")
        try:
            load_repo_mode(learner)
        except ModeViolation as exc:
            assert exc.code == "MODE_INVALID"
        else:
            raise AssertionError("unknown mode did not fail closed")


def fingerprint(repo: Path) -> dict[str, bytes | None]:
    rels = [
        "state/STUDY_STATE.yaml",
        "state/SKILL_MAP.yaml",
        "state/EVIDENCE_LOG.md",
        "state/ACTIVITY_STATE.yaml",
        "activities/ACTIVITY_LOG.md",
        "reviews/REVIEW_STATE.yaml",
        "reviews/REVIEW_QUEUE.md",
        "sources/SOURCE_STATE.yaml",
        "NEXT_ACTIONS.md",
        ".studydd/context_pack.md",
    ]
    return {
        rel: (repo / rel).read_bytes() if (repo / rel).is_file() else None
        for rel in rels
    }


def test_template_commands_refuse_before_state_io() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-mode-cli-") as raw:
        repo = make_repo(Path(raw))
        before = fingerprint(repo)

        plan = run([sys.executable, "scripts/plan_learning_activity.py"], repo)
        assert plan.returncode == 2
        assert "INSTANCE_REQUIRED" in plan.stderr
        assert "retrieval_question" not in plan.stdout + plan.stderr

        context = run([sys.executable, "scripts/build_context_pack.py", "--task", "start_session"], repo)
        assert context.returncode == 2
        assert "INSTANCE_REQUIRED" in context.stderr
        assert "retrieval_question" not in context.stdout + context.stderr

        record = run(
            [
                sys.executable,
                "scripts/record_activity_result.py",
                "--activity-id",
                "act_template",
                "--result",
                "partial",
                "--evidence-id",
                "ev_template",
            ],
            repo,
        )
        assert record.returncode == 2
        assert "INSTANCE_REQUIRED" in record.stderr
        assert fingerprint(repo) == before

        drill = run(
            [sys.executable, "scripts/fast_drill_mode.py", "start", "--session-id", "S-TEMPLATE", "--target-id", "none"],
            repo,
        )
        assert drill.returncode == 2
        assert "INSTANCE_REQUIRED" in drill.stderr
        assert fingerprint(repo) == before


def test_template_planning_split_and_instance_creation() -> None:
    assert (ROOT / "TEMPLATE_BACKLOG.md").is_file()
    assert "TH-01" in (ROOT / "TEMPLATE_BACKLOG.md").read_text(encoding="utf-8")
    assert "TH-01" not in (ROOT / "state" / "STUDY_BACKLOG.md").read_text(encoding="utf-8")
    assert "TEMPLATE_BACKLOG.md" in (ROOT / "NEXT_ACTIONS.md").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="studydd-create-boundary-") as raw:
        target = Path(raw) / "instance"
        result = run(
            [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", "https://github.com/example/instance.git"],
            ROOT,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert not (target / "TEMPLATE_BACKLOG.md").exists()
        assert "TH-01" not in (target / "state" / "STUDY_BACKLOG.md").read_text(encoding="utf-8")


def main() -> int:
    print("StudyDD mode guard tests")
    print("========================")
    with tempfile.TemporaryDirectory(prefix="studydd-mode-unit-") as raw:
        test_mode_contract(Path(raw))
    test_template_commands_refuse_before_state_io()
    test_template_planning_split_and_instance_creation()
    print("Mode guard tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
