#!/usr/bin/env python3
"""Regression tests for scripts/check_studydd.py reference-fixture handling.

EXAMPLES/ fixtures carry deterministic source timestamps ("deterministic test
metadata"). The validator must not fail on wall-clock staleness for them, while
live targets/ keep full freshness enforcement, and --now must apply an explicit
clock everywhere including fixtures.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IGNORED_COPY_ENTRIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".studydd",
}


def copy_repo(dst: Path) -> Path:
    shutil.copytree(
        ROOT,
        dst,
        ignore=shutil.ignore_patterns(*IGNORED_COPY_ENTRIES),
        dirs_exist_ok=True,
    )
    return dst


def run_validator(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/check_studydd.py", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


EXPIRED_TARGET_QUESTION = """\
id: Q-EXP-001
target_id: expired-live-target
skill_id: demo-search-basics
cognitive_level: explain
difficulty: 2
source_ids:
  - expired_live_source
volatility: volatile
question_mode: authoritative_current
question_quality:
  generated_from_memory_allowed: false
  quality_gate: pass
  quality_gate_reason: "Fixture for validator regression test."
public_prompt: >
  Explain one concept.
private_answer_key: |
  A correct explanation.
rubric:
  - Mentions the concept
common_traps: []
transfer_probe: When would this fail?
last_used: 2026-01-01
cooldown_days: 7
"""


def add_expired_live_target(repo: Path) -> None:
    target_dir = repo / "targets" / "expired-live-target" / "questions"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "Q-EXP-001.yaml").write_text(EXPIRED_TARGET_QUESTION, encoding="utf-8")
    (repo / "targets" / "expired-live-target" / "TARGET.yaml").write_text(
        "\n".join(
            [
                "id: expired-live-target",
                "name: Expired live fixture target",
                "study_skill: generic",
                "volatility: volatile",
                'status: example',
                "",
            ]
        ),
        encoding="utf-8",
    )
    source_state = repo / "sources" / "SOURCE_STATE.yaml"
    source_state.write_text(
        "\n".join(
            [
                "---",
                "sources:",
                "  - id: expired_live_source",
                '    title: "Expired live source"',
                '    url: "https://example.invalid/expired"',
                "    authority: official",
                "    target_ids:",
                "      - expired-live-target",
                "    volatility: volatile",
                '    last_checked_at: "2025-12-01T12:00:00+00:00"',
                '    expires_at: "2026-01-01T12:00:00+00:00"',
                '    checked_by: "validator_regression_test"',
                '    notes: "Regression fixture."',
                "    usable_for_questions: true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="studydd-validator-") as tmp:
        repo = copy_repo(Path(tmp) / "repo")

        # 1. Expired EXAMPLES fixture timestamps must not fail validation.
        result = run_validator(repo)
        if result.returncode != 0:
            failures.append(
                "Wall-clock staleness must not fail EXAMPLES reference fixtures.\n"
                + result.stdout
                + result.stderr
            )

        # 2. An explicit --now clock applies to fixtures too: an expired fixture
        #    evaluated at a later clock must fail.
        result = run_validator(repo, "--now", "2026-08-26T12:00:00+00:00")
        if result.returncode == 0 or "is stale" not in result.stdout:
            failures.append(
                "Explicit --now must enforce staleness on EXAMPLES fixtures.\n"
                + result.stdout
                + result.stderr
            )

        # 3. --now accepts only valid ISO 8601 input.
        result = run_validator(repo, "--now", "not-a-date")
        if result.returncode != 2:
            failures.append("Invalid --now values must exit with code 2.")

        # 4. lint_questions.py shares the reference-snapshot semantics.
        def run_lint(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/lint_questions.py", *args],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )

        if run_lint().returncode != 0:
            failures.append("Lint must pass expired EXAMPLES fixtures without --now.")
        if run_lint("--now", "2026-08-26T12:00:00+00:00").returncode != 1:
            failures.append("Lint must fail expired fixtures when an explicit later --now is given.")
        if run_lint("--now", "2026-06-24T12:00:00+00:00").returncode != 0:
            failures.append("Lint must pass fixtures evaluated at their own frozen clock.")

        # 5. Live targets keep wall-clock freshness enforcement.
        add_expired_live_target(repo)
        result = run_validator(repo)
        if result.returncode == 0 or "is stale" not in result.stdout:
            failures.append(
                "Wall-clock staleness must still fail expired sources under targets/.\n"
                + result.stdout
                + result.stderr
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("All check_studydd reference-snapshot tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
