#!/usr/bin/env python3
"""Tests for scripts/check_source_freshness.py.

Creates temporary SOURCE_STATE.yaml and TARGET.yaml fixtures and invokes the
freshness script via subprocess. No network calls are made.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_SRC = ROOT / "scripts" / "check_source_freshness.py"


def run_script(tmp_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Copy the freshness script into tmp_root so ROOT resolves to tmp_root."""
    script_dst = tmp_root / "scripts" / "check_source_freshness.py"
    script_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPT_SRC, script_dst)
    return subprocess.run(
        [sys.executable, str(script_dst), *args],
        cwd=tmp_root,
        capture_output=True,
        text=True,
        check=False,
    )


def write_source_state(tmp_root: Path, sources: list[dict]) -> None:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    state_path = tmp_root / "sources" / "SOURCE_STATE.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        yaml.safe_dump({"metadata": {"template_version": "0.8.1"}, "sources": sources}, sort_keys=False),
        encoding="utf-8",
    )


def write_target(tmp_root: Path, target_id: str, volatility: str | None) -> None:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    target_dir = tmp_root / "targets" / target_id
    target_dir.mkdir(parents=True, exist_ok=True)
    data: dict = {
        "id": target_id,
        "type": "skill",
        "title": f"Test target {target_id}",
    }
    if volatility:
        data["volatility"] = volatility
    (target_dir / "TARGET.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_volatile_fresh_official_passes() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-fresh-") as tmp:
        tmp_root = Path(tmp)
        target_id = "demo-ai-search-exam"
        write_target(tmp_root, target_id, "volatile")
        write_source_state(
            tmp_root,
            [
                {
                    "id": "mslearn_ai_search_overview",
                    "target_ids": [target_id],
                    "authority": "official",
                    "usable_for_questions": True,
                    "last_checked_at": "2026-06-24T10:00:00+00:00",
                }
            ],
        )

        result = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        print("--- test_volatile_fresh_official_passes stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "Fresh usable sources:" in result.stdout
        assert "mslearn_ai_search_overview" in result.stdout
        assert "Stale sources:" in result.stdout
        assert "Unverified sources:" in result.stdout


def test_volatile_stale_source_fails() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-stale-") as tmp:
        tmp_root = Path(tmp)
        target_id = "demo-ai-search-exam"
        write_target(tmp_root, target_id, "volatile")
        write_source_state(
            tmp_root,
            [
                {
                    "id": "old_blog_ai_search_notes",
                    "target_ids": [target_id],
                    "authority": "unverified",
                    "usable_for_questions": True,
                    "last_checked_at": "2026-05-01T10:00:00+00:00",
                }
            ],
        )

        result = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        print("--- test_volatile_stale_source_fails stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode != 0, f"Expected non-zero exit, got {result.returncode}"
        assert "old_blog_ai_search_notes" in result.stdout
        assert "Stale sources:" in result.stdout


def test_stable_target_no_refresh_required() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-stable-") as tmp:
        tmp_root = Path(tmp)
        target_id = "stable-topic"
        write_target(tmp_root, target_id, "stable")
        # No sources at all.
        write_source_state(tmp_root, [])

        result = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        print("--- test_stable_target_no_refresh_required stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"


def test_no_web_search() -> None:
    """The script source must not import network/web-fetching modules."""
    source = SCRIPT_SRC.read_text(encoding="utf-8")
    forbidden = ["urllib", "http.client", "requests", "httpx", "aiohttp", "curl", "wget"]
    for name in forbidden:
        assert name not in source, f"Script imports or references network module: {name}"


def test_allow_stale_practice_only() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-allow-") as tmp:
        tmp_root = Path(tmp)
        target_id = "demo-ai-search-exam"
        write_target(tmp_root, target_id, "volatile")
        write_source_state(
            tmp_root,
            [
                {
                    "id": "old_blog_ai_search_notes",
                    "target_ids": [target_id],
                    "authority": "unverified",
                    "usable_for_questions": True,
                    "last_checked_at": "2026-05-01T10:00:00+00:00",
                }
            ],
        )

        result = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--allow-stale",
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        print("--- test_allow_stale_practice_only stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "Stale source allowed by override." in result.stdout
        assert "practice-only, not authoritative-current" in result.stdout


def test_now_deterministic() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-now-") as tmp:
        tmp_root = Path(tmp)
        target_id = "demo-ai-search-exam"
        write_target(tmp_root, target_id, "volatile")
        write_source_state(
            tmp_root,
            [
                {
                    "id": "mslearn_ai_search_overview",
                    "target_ids": [target_id],
                    "authority": "official",
                    "usable_for_questions": True,
                    "last_checked_at": "2026-06-24T10:00:00+00:00",
                }
            ],
        )

        result1 = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        result2 = run_script(
            tmp_root,
            "--target-id",
            target_id,
            "--now",
            "2026-06-24T12:00:00+00:00",
        )
        print("--- test_now_deterministic stdout 1 ---")
        print(result1.stdout)
        print("--- test_now_deterministic stdout 2 ---")
        print(result2.stdout)
        assert result1.returncode == 0
        assert result2.returncode == 0
        assert result1.stdout == result2.stdout


def main() -> int:
    tests = [
        test_volatile_fresh_official_passes,
        test_volatile_stale_source_fails,
        test_stable_target_no_refresh_required,
        test_no_web_search,
        test_allow_stale_practice_only,
        test_now_deterministic,
    ]

    failures = 0
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        try:
            test()
            print(f"  PASSED")
        except AssertionError as exc:
            print(f"  FAILED: {exc}")
            failures += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            failures += 1

    if failures:
        print(f"\n{failures} test(s) failed.")
        return 1

    print("\nAll source freshness tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
