#!/usr/bin/env python3
"""Public-safe synthetic tests for completed source-check recording."""

from __future__ import annotations

import shutil
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)

sys.path.insert(0, str(ROOT / "scripts"))
import check_source_freshness
import record_source_check


def write_yaml(path: Path, value: dict) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def read_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def make_repo(mode: str, sources: list[dict] | None = None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="studydd-source-check-"))
    (root / "scripts").mkdir()
    for name in ("record_source_check.py", "check_source_freshness.py"):
        shutil.copy(ROOT / "scripts" / name, root / "scripts" / name)
    write_yaml(root / "state/STUDYDD_MODE.yaml", {"mode": mode})
    write_yaml(
        root / "sources/SOURCE_STATE.yaml",
        {"metadata": {"template_version": "synthetic"}, "sources": sources or []},
    )
    return root


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/record_source_check.py", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_template_and_bootstrap_refuse_without_writes() -> None:
    for mode in ("template", "bootstrap"):
        root = make_repo(mode)
        path = root / "sources/SOURCE_STATE.yaml"
        before = path.read_bytes()
        result = run_cli(
            root,
            "synthetic-source",
            "--target-id",
            "synthetic-target",
            "--checked-at",
            NOW.isoformat(),
        )
        assert result.returncode == 2, result.stderr
        assert path.read_bytes() == before
        assert not list(path.parent.glob(".*.tmp"))


def test_dry_run_and_demo_are_read_only() -> None:
    root = make_repo("template")
    path = root / "sources/SOURCE_STATE.yaml"
    before = path.read_bytes()
    result = run_cli(
        root,
        "synthetic-source",
        "--target-id",
        "synthetic-target",
        "--checked-at",
        NOW.isoformat(),
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "Dry-run: no file written" in result.stdout
    assert path.read_bytes() == before

    demo = run_cli(root, "--demo")
    assert demo.returncode == 0
    assert "no file written" in demo.stdout
    assert path.read_bytes() == before


def test_validation_happens_before_write() -> None:
    root = make_repo("learner_instance")
    path = root / "sources/SOURCE_STATE.yaml"
    before = path.read_bytes()
    for args in (
        ("bad/id", "--target-id", "synthetic-target"),
        ("synthetic-source", "--target-id", "synthetic-target", "--outcome", "invalid"),
        ("synthetic-source", "--target-id", "synthetic-target", "--checked-at", "not-a-time"),
        (
            "synthetic-source",
            "--target-id",
            "synthetic-target",
            "--checked-at",
            NOW.isoformat(),
            "--expires-at",
            "2026-06-30T12:00:00+00:00",
        ),
    ):
        result = run_cli(root, *args)
        assert result.returncode == 1
        assert path.read_bytes() == before


def test_create_and_repeat_is_idempotent() -> None:
    root = make_repo("learner_instance")
    args = (
        "synthetic-official",
        "--target-id",
        "synthetic-target",
        "--outcome",
        "fresh",
        "--authority",
        "official",
        "--volatility",
        "volatile",
        "--checked-at",
        NOW.isoformat(),
        "--summary",
        "Synthetic official source confirmed",
        "--evidence-id",
        "ev_synthetic_001",
        "--activity-id",
        "act_synthetic_001",
    )
    first = run_cli(root, *args)
    assert first.returncode == 0, first.stderr
    path = root / "sources/SOURCE_STATE.yaml"
    first_bytes = path.read_bytes()
    second = run_cli(root, *args)
    assert second.returncode == 0, second.stderr
    assert "Already recorded" in second.stdout
    assert path.read_bytes() == first_bytes
    state = read_yaml(path)
    assert [source["id"] for source in state["sources"]] == ["synthetic-official"]
    assert state["metadata"]["last_updated"] == NOW.isoformat()


def test_stale_outcome_preserves_timestamp_and_classifier_marks_stale() -> None:
    old_checked = "2026-06-20T12:00:00+00:00"
    source = {
        "id": "synthetic-source",
        "target_ids": ["synthetic-target"],
        "authority": "official",
        "volatility": "volatile",
        "usable_for_questions": True,
        "last_checked_at": old_checked,
        "expires_at": "2026-07-20T12:00:00+00:00",
    }
    root = make_repo("learner_instance", [source])
    result = run_cli(
        root,
        "synthetic-source",
        "--outcome",
        "stale",
        "--checked-at",
        NOW.isoformat(),
        "--summary",
        "Synthetic check found the source stale",
    )
    assert result.returncode == 0, result.stderr
    recorded = read_yaml(root / "sources/SOURCE_STATE.yaml")["sources"][0]
    assert recorded["last_checked_at"] == old_checked
    assert recorded["expires_at"] == "2026-07-20T12:00:00+00:00"
    status, reason = check_source_freshness.classify_source(recorded, NOW, "volatile")
    assert status == "stale"
    assert "recorded check outcome" in (reason or "")


def test_fresh_outcome_is_consumed_by_single_classifier() -> None:
    root = make_repo("learner_instance")
    result = run_cli(
        root,
        "synthetic-official",
        "--target-id",
        "synthetic-target",
        "--outcome",
        "fresh",
        "--checked-at",
        NOW.isoformat(),
        "--volatility",
        "volatile",
    )
    assert result.returncode == 0, result.stderr
    state = read_yaml(root / "sources/SOURCE_STATE.yaml")
    summary = check_source_freshness.target_freshness_summary(
        "synthetic-target", "volatile", state, NOW
    )
    assert summary.status == "fresh"
    assert summary.has_fresh_usable


def test_atomic_failure_leaves_original_and_cleans_temporary_file() -> None:
    root = make_repo(
        "learner_instance",
        [
            {
                "id": "synthetic-source",
                "target_ids": ["synthetic-target"],
                "authority": "official",
                "volatility": "volatile",
                "usable_for_questions": True,
                "last_checked_at": "2026-06-20T12:00:00+00:00",
            }
        ],
    )
    path = root / "sources/SOURCE_STATE.yaml"
    before = path.read_bytes()
    original_replace = record_source_check.os.replace

    def fail_replace(_source: str | bytes | os.PathLike[str], _destination: str | bytes | os.PathLike[str]) -> None:
        raise OSError("synthetic replace failure")

    record_source_check.os.replace = fail_replace  # type: ignore[assignment]
    try:
        status = record_source_check.record_source_check(
            "synthetic-source",
            outcome="fresh",
            checked_at=NOW.isoformat(),
            repo_root=root,
        )
    finally:
        record_source_check.os.replace = original_replace  # type: ignore[assignment]
    assert status == 1
    assert path.read_bytes() == before
    assert not list(path.parent.glob(".*.tmp"))


def test_activity_completion_handoff_records_only_source_state() -> None:
    root = make_repo("learner_instance")
    shutil.copy(ROOT / "scripts/record_activity_result.py", root / "scripts/record_activity_result.py")
    write_yaml(
        root / "state/ACTIVITY_STATE.yaml",
        {
            "active_activity": {
                "id": "act_synthetic_001",
                "type": "recent_info_check",
                "target_id": "synthetic-target",
                "skill_id": "synthetic-skill",
                "status": "proposed",
                "expected_evidence": ["source_metadata"],
            },
            "recent_activities": [],
        },
    )
    (root / "activities").mkdir()
    (root / "state/EVIDENCE_LOG.md").parent.mkdir(exist_ok=True)
    (root / "activities/ACTIVITY_LOG.md").write_text("## Activities\n\nNone yet.\n", encoding="utf-8")
    (root / "state/EVIDENCE_LOG.md").write_text("## Evidence items\n\nNone yet.\n", encoding="utf-8")
    write_yaml(root / "state/SKILL_MAP.yaml", {"skills": []})

    result = subprocess.run(
        [
            sys.executable,
            "scripts/record_activity_result.py",
            "--activity-id",
            "act_synthetic_001",
            "--result",
            "correct",
            "--evidence-id",
            "ev_synthetic_001",
            "--source-id",
            "synthetic-source",
            "--source-checked-at",
            NOW.isoformat(),
            "--source-summary",
            "Synthetic current-source check completed",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    source = read_yaml(root / "sources/SOURCE_STATE.yaml")["sources"][0]
    assert source["last_check"]["activity_id"] == "act_synthetic_001"
    assert source["last_check"]["evidence_id"] == "ev_synthetic_001"


def main() -> int:
    tests = [
        test_template_and_bootstrap_refuse_without_writes,
        test_dry_run_and_demo_are_read_only,
        test_validation_happens_before_write,
        test_create_and_repeat_is_idempotent,
        test_stale_outcome_preserves_timestamp_and_classifier_marks_stale,
        test_fresh_outcome_is_consumed_by_single_classifier,
        test_atomic_failure_leaves_original_and_cleans_temporary_file,
        test_activity_completion_handoff_records_only_source_state,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("All synthetic source-check tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
