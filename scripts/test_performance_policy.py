#!/usr/bin/env python3
"""Test StudyDD fast-path performance policy.

Checks that the performance budget file exists, context packs report file counts,
fast paths skip raw logs, and stale-check avoids unnecessary writes.
"""

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


def build_instance() -> Path:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="studydd-perf-")
    target = Path(tmp) / "Study_Perf"
    remote = "https://github.com/example/Study_Perf.git"

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
    study_state["learner"]["name"] = "Perf Test Learner"
    study_state["active_target_id"] = "perf-target"
    study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

    target_dir = target / "targets" / "perf-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "TARGET.yaml").write_text(
        "---\n"
        "id: perf-target\n"
        "type: skill\n"
        "title: Performance test target\n"
        "description: Temporary target for performance policy test.\n"
        "study_skill: it_certification\n",
        encoding="utf-8",
    )

    skill_map_path = target / "state" / "SKILL_MAP.yaml"
    skill_map = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
    skill_map["skills"] = [
        {
            "id": "perf-search-basics",
            "label": "Keyword vs vector search",
            "status": "weak",
            "readiness": 35,
            "confidence": "low",
            "evidence": ["ev_perf_001"],
            "next_validation_question": "Q-PERF-001",
        },
    ]
    skill_map_path.write_text(yaml.safe_dump(skill_map, sort_keys=False), encoding="utf-8")

    evidence_path = target / "state" / "EVIDENCE_LOG.md"
    evidence_text = evidence_path.read_text(encoding="utf-8")
    evidence_entry = (
        "\n- **Evidence ID:** ev_perf_001\n"
        "- **Date:** 2026-06-24\n"
        "- **Target ID:** perf-target\n"
        "- **Skill ID:** perf-search-basics\n"
        "- **Question ID:** Q-PERF-001\n"
        "- **Question summary:** Explain keyword vs vector search.\n"
        "- **Learner answer summary:** Partial answer.\n"
        "- **Verdict:** partial\n"
        "- **Explanation:** Missing scenario.\n"
        "- **Confidence:** low\n"
    )
    evidence_path.write_text(evidence_text + evidence_entry, encoding="utf-8")

    return target


def main() -> int:
    print("StudyDD performance policy test")
    print("===============================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    print("\nTest: performance budget file exists and validates")
    budget_path = ROOT / "state" / "PERFORMANCE_BUDGET.yaml"
    assert budget_path.is_file(), "Missing state/PERFORMANCE_BUDGET.yaml"
    budget = yaml.safe_load(budget_path.read_text(encoding="utf-8")) or {}
    assert "budgets" in budget, "PERFORMANCE_BUDGET.yaml missing budgets"
    assert "fast_path" in budget["budgets"], "PERFORMANCE_BUDGET.yaml missing fast_path budget"
    assert "session_boundary" in budget["budgets"], "PERFORMANCE_BUDGET.yaml missing session_boundary budget"
    assert "deep_audit" in budget["budgets"], "PERFORMANCE_BUDGET.yaml missing deep_audit budget"
    assert "rules" in budget, "PERFORMANCE_BUDGET.yaml missing rules"
    print("Performance budget OK")

    target = build_instance()

    print("\nTest: context pack reports file counts and skips raw logs on fast path")
    run([sys.executable, "scripts/compact_state.py"], target)
    result = run(
        [sys.executable, "scripts/build_context_pack.py", "--task", "grade_answer", "--skill-id", "perf-search-basics"],
        target,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return 1
    assert "Files included:" in result.stdout
    assert "Raw log files loaded: 0" in result.stdout
    assert "raw audit log" in result.stdout
    assert "state/EVIDENCE_LOG.md" in result.stdout
    print("Context pack fast path OK")

    print("\nTest: compact_state --check-stale does not rewrite files unnecessarily")
    result = run([sys.executable, "scripts/compact_state.py", "--check-stale"], target, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return 1
    assert "No compaction needed" in result.stdout
    print("Stale check OK")

    print("\nTest: demo replay mentions fast path and minimal loading")
    result = run([sys.executable, "scripts/run_demo_replay.py"], ROOT, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return 1
    assert "fast path" in result.stdout.lower()
    assert "only relevant state is loaded" in result.stdout.lower()
    assert "only touched files are updated" in result.stdout.lower()
    assert "full validation runs at session boundary" in result.stdout.lower()
    print("Demo replay mentions fast path OK")

    print("\nTest: full validator still passes")
    val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(val.stdout)
    if val.returncode != 0:
        print(val.stderr)
        return 1

    print("Performance policy test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
