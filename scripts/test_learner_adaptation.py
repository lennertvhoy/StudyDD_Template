#!/usr/bin/env python3
"""Tests for scripts/suggest_study_adjustment.py.

Creates temporary StudyDD state fixtures and invokes the suggestion script via
subprocess. No learner state is modified.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_SRC = ROOT / "scripts" / "suggest_study_adjustment.py"


def run_script(tmp_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Copy the suggestion script into tmp_root so ROOT resolves to tmp_root."""
    script_dst = tmp_root / "scripts" / "suggest_study_adjustment.py"
    script_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPT_SRC, script_dst)
    return subprocess.run(
        [sys.executable, str(script_dst), *args],
        cwd=tmp_root,
        capture_output=True,
        text=True,
        check=False,
    )


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def write_evidence_log(tmp_root: Path, items: list[dict[str, Any]]) -> None:
    path = tmp_root / "state" / "EVIDENCE_LOG.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Evidence log",
        "",
        "## Evidence items",
        "",
    ]
    for item in items:
        lines.append("- **Date:** " + item.get("date", "2026-06-24T10:00:00+00:00"))
        lines.append("- **Target ID:** " + item.get("target_id", "target-example"))
        lines.append("- **Skill ID:** " + item.get("skill_id", "skill-example"))
        lines.append("- **Question ID:** " + item.get("question_id", "Q-001"))
        lines.append(
            "- **Question summary:** " + item.get("question_summary", "Summary")
        )
        lines.append(
            "- **Learner answer summary:** " + item.get("answer_summary", "Answer")
        )
        lines.append("- **Verdict:** " + item.get("verdict", "partial"))
        lines.append("- **Explanation:** " + item.get("explanation", "Explanation"))
        lines.append("- **Confidence:** " + item.get("confidence", "medium"))
        if item.get("mistake_type"):
            lines.append("- **Mistake type:** " + item["mistake_type"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_review_state(tmp_root: Path, items: list[dict[str, Any]]) -> None:
    write_yaml(
        tmp_root / "reviews" / "REVIEW_STATE.yaml",
        {"review_items": items},
    )


def write_learner_profile(tmp_root: Path, personalized: bool = False) -> None:
    profile: dict[str, Any] = {
        "metadata": {"template_version": "0.8.1"},
        "learner_preferences": {
            "explanation_style": "",
            "question_style_preference": "",
            "desired_difficulty": "",
            "feedback_style": "",
            "session_length_preference_minutes": None,
            "low_energy_mode_preference": "",
            "source_refresh_preference": "ask_when_needed",
        },
        "adaptation_state": {
            "methods_tried": [],
            "methods_that_helped": [],
            "methods_that_failed": [],
            "recurring_friction": [],
            "last_feedback_prompt_at": "",
            "feedback_prompt_cooldown_days": 7,
        },
        "control": {
            "learner_overrides": [],
            "agent_recommendations_declined": [],
        },
    }
    if personalized:
        profile["learner_preferences"]["explanation_style"] = "detailed"
        profile["learner_preferences"]["desired_difficulty"] = "hard"
    write_yaml(tmp_root / "state" / "LEARNER_PROFILE.yaml", profile)


def write_mode(tmp_root: Path, mode: str) -> None:
    write_yaml(
        tmp_root / "state" / "STUDYDD_MODE.yaml",
        {"mode": mode, "public_safe": mode == "template", "personalized": False},
    )


def test_learner_profile_remains_generic_and_unmutated() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_mode(tmp_root, "template")
        write_learner_profile(tmp_root, personalized=False)
        write_review_state(tmp_root, [])
        write_evidence_log(tmp_root, [])

        profile_before = (tmp_root / "state" / "LEARNER_PROFILE.yaml").read_text(
            encoding="utf-8"
        )

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_learner_profile_remains_generic_and_unmutated stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "No recommendation: insufficient evidence." in result.stdout

        profile_after = (tmp_root / "state" / "LEARNER_PROFILE.yaml").read_text(
            encoding="utf-8"
        )
        assert profile_before == profile_after, "Script modified the learner profile"


def test_adaptation_is_evidence_based_and_non_spammy() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(tmp_root, [])
        write_evidence_log(
            tmp_root,
            [
                {
                    "date": "2026-06-24T10:00:00+00:00",
                    "verdict": "partial",
                    "mistake_type": "service-boundary-confusion",
                }
            ],
        )

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_adaptation_is_evidence_based stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "No recommendation: insufficient evidence." in result.stdout


def test_demo_output_is_deterministic() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        result1 = run_script(tmp_root, "--demo")
        result2 = run_script(tmp_root, "--demo")
        print("--- test_demo_output_is_deterministic stdout 1 ---")
        print(result1.stdout)
        print("--- test_demo_output_is_deterministic stdout 2 ---")
        print(result2.stdout)
        assert result1.returncode == 0, f"Expected exit 0, got {result1.returncode}"
        assert result2.returncode == 0, f"Expected exit 0, got {result2.returncode}"
        assert result1.stdout == result2.stdout
        assert "You missed a scenario tradeoff" in result1.stdout
        assert "Learner control:" in result1.stdout


def test_insufficient_evidence_yields_no_recommendation() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(tmp_root, [])
        write_evidence_log(tmp_root, [])

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_insufficient_evidence stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "No recommendation: insufficient evidence." in result.stdout


def test_repeated_mistake_tag_produces_strong_recommendation() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(tmp_root, [])
        items = [
            {
                "date": f"2026-06-{22 + i:02d}T10:00:00+00:00",
                "verdict": "partial",
                "mistake_type": "service-boundary-confusion",
            }
            for i in range(3)
        ]
        write_evidence_log(tmp_root, items)

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_repeated_mistake_tag stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "service-boundary" in result.stdout
        assert "Recommendation strength: strong" in result.stdout
        assert "Recommended adjustment:" in result.stdout
        assert "Learner control:" in result.stdout


def test_two_weak_evidence_items_produce_moderate_recommendation() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(tmp_root, [])
        items = [
            {
                "date": f"2026-06-{22 + i:02d}T10:00:00+00:00",
                "verdict": "partial",
                "mistake_type": "service-boundary-confusion",
            }
            for i in range(2)
        ]
        write_evidence_log(tmp_root, items)

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_two_weak_evidence_items_produce_moderate_recommendation stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "service-boundary" in result.stdout
        assert "Recommendation strength: moderate" in result.stdout
        assert "Recommended adjustment:" in result.stdout
        assert "Learner control:" in result.stdout


def test_compound_repaired_verdict_counts_as_weak_evidence() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(tmp_root, [])
        items = [
            {
                "date": f"2026-06-{22 + i:02d}T10:00:00+00:00",
                "verdict": "partial -> correct after repair",
                "mistake_type": "service-boundary-confusion",
            }
            for i in range(2)
        ]
        write_evidence_log(tmp_root, items)

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_compound_repaired_verdict_counts_as_weak_evidence stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "service-boundary" in result.stdout
        assert "Recommendation strength: moderate" in result.stdout
        assert "Recommended adjustment:" in result.stdout
        assert "Learner control:" in result.stdout


def test_overdue_reviews_produce_moderate_recommendation() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-adapt-") as tmp:
        tmp_root = Path(tmp)
        write_review_state(
            tmp_root,
            [
                {
                    "id": "rev_001",
                    "skill_id": "skill-example",
                    "evidence_id": "ev_001",
                    "target_id": "target-example",
                    "due_at": "2026-06-23T10:00:00+00:00",
                    "last_reviewed_at": None,
                    "interval_days": 1,
                    "stability": None,
                    "difficulty": None,
                    "lapses": 0,
                    "priority": "normal",
                    "status": "scheduled",
                    "source": "missed_question",
                    "override_count": 0,
                }
            ],
        )
        write_evidence_log(tmp_root, [])

        result = run_script(tmp_root, "--now", "2026-06-24T12:00:00+00:00")
        print("--- test_overdue_reviews stdout ---")
        print(result.stdout)
        if result.stderr:
            print("stderr:", result.stderr)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
        assert "overdue reviews" in result.stdout.lower()
        assert "Recommendation strength: moderate" in result.stdout
        assert "due reviews" in result.stdout.lower()
        assert "There is 1 review item past its due date." in result.stdout
        assert "Learner control:" in result.stdout


def main() -> int:
    tests = [
        test_learner_profile_remains_generic_and_unmutated,
        test_adaptation_is_evidence_based_and_non_spammy,
        test_demo_output_is_deterministic,
        test_insufficient_evidence_yields_no_recommendation,
        test_repeated_mistake_tag_produces_strong_recommendation,
        test_two_weak_evidence_items_produce_moderate_recommendation,
        test_compound_repaired_verdict_counts_as_weak_evidence,
        test_overdue_reviews_produce_moderate_recommendation,
    ]

    failures = 0
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        try:
            test()
            print("  PASSED")
        except AssertionError as exc:
            print(f"  FAILED: {exc}")
            failures += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            failures += 1

    if failures:
        print(f"\n{failures} test(s) failed.")
        return 1

    print("\nAll learner adaptation tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
