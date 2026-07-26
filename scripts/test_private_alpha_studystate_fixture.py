#!/usr/bin/env python3
"""Regression tests for the deterministic, public-safe private-alpha fixture."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPLAY = [sys.executable, "scripts/run_demo_replay.py"]
TIME_A = "2026-07-26T12:00:00+00:00"
TIME_B = "2026-07-27T12:00:00+00:00"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(REPLAY + list(args), cwd=ROOT, text=True, capture_output=True, check=False)


def assert_ok(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)


def main() -> int:
    first = run("--evaluation-time", TIME_A)
    second = run("--evaluation-time", TIME_A)
    assert_ok(first)
    assert_ok(second)
    assert first.stdout == second.stdout, "same logical time must replay identically"
    assert "Logical evaluation time: 2026-07-26T12:00:00+00:00" in first.stdout
    assert "rev_demo-search-basics_20260726_120000" in first.stdout

    advanced = run("--evaluation-time", TIME_B)
    assert_ok(advanced)
    assert "rev_demo-search-basics_20260727_120000" in advanced.stdout
    assert advanced.stdout != first.stdout, "logical time must be an explicit scenario input"

    from check_source_freshness import classify_source

    stale, _ = classify_source(
        {"usable_for_questions": True, "expires_at": "2026-07-24T12:00:00+00:00"},
        datetime(2026, 7, 26, tzinfo=timezone.utc),
        "volatile",
    )
    assert stale == "stale", "production freshness semantics must remain strict"

    candidate = yaml.safe_load(
        (ROOT / "EXAMPLES/demo_ai_search_exam/DEVELOPMENT_CANDIDATE.yaml").read_text(encoding="utf-8")
    )
    assert candidate["classification"] == "development_candidate"
    assert candidate["productionEligible"] is False
    assert candidate["clockContract"] == "explicit_evaluation_time_only"
    assert candidate["journey"]["reversibleAdaptation"]["authority"] == "human_on_the_loop"
    assert "undo" in candidate["journey"]["reversibleAdaptation"]["userOptions"]

    print("private-alpha StudyState fixture tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
