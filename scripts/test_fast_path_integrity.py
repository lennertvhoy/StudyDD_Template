#!/usr/bin/env python3
"""Regression tests for generic fast-path integrity guarantees."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


def load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save_yaml(path: Path, data: dict) -> None:
    import yaml

    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def create_instance(tmp: str, name: str = "FastPath") -> Path:
    target = Path(tmp) / f"StudyDD_{name}"
    run(
        [
            sys.executable,
            "scripts/create_instance.py",
            "--target",
            str(target),
            "--remote",
            f"https://github.com/example/studydd-{name.lower()}.git",
        ],
        ROOT,
    )
    mode_path = target / "state" / "STUDYDD_MODE.yaml"
    mode = load_yaml(mode_path)
    mode.update({"mode": "learner_instance", "personalized": True, "public_safe": False})
    save_yaml(mode_path, mode)

    study_path = target / "state" / "STUDY_STATE.yaml"
    study = load_yaml(study_path)
    study["learner"]["name"] = "Fixture Learner"
    study["active_target_id"] = "fixture-target"
    save_yaml(study_path, study)

    target_dir = target / "targets" / "fixture-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "TARGET.yaml").write_text(
        "---\nid: fixture-target\ntype: skill\ntitle: Fixture target\nvolatility: stable\n",
        encoding="utf-8",
    )

    skill_path = target / "state" / "SKILL_MAP.yaml"
    skill_map = load_yaml(skill_path)
    skill_map["skills"] = [
        {
            "id": "skill-a",
            "label": "Skill A",
            "status": "weak",
            "readiness": 25,
            "confidence": "low",
            "evidence": ["ev-new"],
        },
        {
            "id": "skill-b",
            "label": "Skill B",
            "status": "pending",
            "readiness": 0,
            "confidence": "low",
            "evidence": [],
        },
    ]
    save_yaml(skill_path, skill_map)
    return target


def append_evidence(instance: Path, evidence_id: str, skill_id: str) -> None:
    path = instance / "state" / "EVIDENCE_LOG.md"
    text = path.read_text(encoding="utf-8")
    text += (
        f"\n- **Evidence ID:** {evidence_id}\n"
        "- **Date:** 2026-07-12\n"
        "- **Target ID:** fixture-target\n"
        f"- **Skill ID:** {skill_id}\n"
        "- **Question ID:** Q-FIXTURE-001\n"
        "- **Question summary:** Fixture question.\n"
        "- **Learner answer summary:** Fixture answer.\n"
        "- **Verdict:** partial\n"
        "- **Explanation:** Fixture evidence.\n"
        "- **Confidence:** low\n"
    )
    path.write_text(text, encoding="utf-8")


def test_validator_requires_selector(instance: Path) -> None:
    result = run([sys.executable, "scripts/validate_touched_state.py"], instance, check=False)
    assert result.returncode != 0


def test_validator_uses_canonical_evidence_before_compaction(instance: Path) -> None:
    append_evidence(instance, "ev-new", "skill-a")
    result = run(
        [
            sys.executable,
            "scripts/validate_touched_state.py",
            "--skill-id",
            "skill-a",
            "--evidence-id",
            "ev-new",
        ],
        instance,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cross_skill_reference_fails(instance: Path) -> None:
    result = run(
        [
            sys.executable,
            "scripts/validate_touched_state.py",
            "--skill-id",
            "skill-b",
            "--evidence-id",
            "ev-new",
        ],
        instance,
        check=False,
    )
    assert result.returncode != 0
    assert "belongs to skill 'skill-a'" in result.stdout


def test_duplicate_evidence_fails(instance: Path) -> None:
    append_evidence(instance, "ev-new", "skill-a")
    result = run(
        [sys.executable, "scripts/validate_touched_state.py", "--evidence-id", "ev-new"],
        instance,
        check=False,
    )
    assert result.returncode != 0
    assert "duplicate evidence ID" in result.stdout


def test_selector_is_read_only(instance: Path) -> None:
    review_path = instance / "reviews" / "REVIEW_STATE.yaml"
    state = load_yaml(review_path)
    state["review_items"] = [
        {
            "id": "rev-read-only",
            "skill_id": "skill-a",
            "evidence_id": "ev-selector",
            "target_id": "fixture-target",
            "due_at": "2026-07-11T10:00:00+00:00",
            "interval_days": 1,
            "status": "scheduled",
        }
    ]
    save_yaml(review_path, state)
    before = review_path.read_bytes()
    result = run(
        [
            sys.executable,
            "scripts/select_next_study_action.py",
            "--now",
            "2026-07-12T12:00:00+00:00",
        ],
        instance,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert review_path.read_bytes() == before
    assert "review first" in result.stdout.lower()


def test_schedule_uses_positive_explicit_learning_step(instance: Path) -> None:
    result = run(
        [
            sys.executable,
            "scripts/schedule_review.py",
            "--skill-id",
            "skill-a",
            "--evidence-id",
            "ev-new",
            "--target-id",
            "fixture-target",
            "--grade",
            "wrong",
            "--confidence",
            "low",
            "--now",
            "2026-07-12T12:00:00+00:00",
        ],
        instance,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    item = load_yaml(instance / "reviews" / "REVIEW_STATE.yaml")["review_items"][-1]
    assert float(item["interval_days"]) > 0
    assert item["learning_step"] == {"value": 10, "unit": "minutes"}

    before_count = len(
        load_yaml(instance / "reviews" / "REVIEW_STATE.yaml")["review_items"]
    )
    repeated = run(
        [
            sys.executable,
            "scripts/schedule_review.py",
            "--skill-id",
            "skill-a",
            "--evidence-id",
            "ev-new",
            "--target-id",
            "fixture-target",
            "--grade",
            "wrong",
            "--confidence",
            "low",
            "--now",
            "2026-07-12T12:00:00+00:00",
        ],
        instance,
        check=False,
    )
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    after_count = len(
        load_yaml(instance / "reviews" / "REVIEW_STATE.yaml")["review_items"]
    )
    assert after_count == before_count
    assert "already scheduled" in repeated.stdout


def test_duplicate_review_fails(instance: Path) -> None:
    path = instance / "reviews" / "REVIEW_STATE.yaml"
    state = load_yaml(path)
    duplicate = dict(state["review_items"][-1])
    state["review_items"].append(duplicate)
    save_yaml(path, state)
    review_id = str(duplicate["id"])
    result = run(
        [sys.executable, "scripts/validate_touched_state.py", "--review-id", review_id],
        instance,
        check=False,
    )
    assert result.returncode != 0
    assert "duplicate review ID" in result.stdout


def test_duplicate_activity_fails(instance: Path) -> None:
    path = instance / "activities" / "ACTIVITY_LOG.md"
    text = path.read_text(encoding="utf-8")
    entry = (
        "\n- **Activity ID:** act-duplicate\n"
        "- **Timestamp:** 2026-07-12T12:00:00+00:00\n"
        "- **Type:** paper_exercise\n"
    )
    path.write_text(text + entry + entry, encoding="utf-8")
    result = run(
        [
            sys.executable,
            "scripts/validate_touched_state.py",
            "--activity-id",
            "act-duplicate",
        ],
        instance,
        check=False,
    )
    assert result.returncode != 0
    assert "duplicate activity ID" in result.stdout


def test_review_failure_propagates(instance: Path) -> None:
    activity_path = instance / "state" / "ACTIVITY_STATE.yaml"
    state = load_yaml(activity_path)
    state["active_activity"] = {
        "id": "act-failure",
        "type": "paper_exercise",
        "target_id": "fixture-target",
        "skill_id": "skill-a",
        "status": "proposed",
        "reason": "Fixture",
        "expected_evidence": ["typed answer"],
    }
    save_yaml(activity_path, state)
    tracked_paths = [
        activity_path,
        instance / "activities" / "ACTIVITY_LOG.md",
        instance / "state" / "EVIDENCE_LOG.md",
        instance / "state" / "SKILL_MAP.yaml",
        instance / "reviews" / "REVIEW_STATE.yaml",
    ]
    before = {path: path.read_bytes() for path in tracked_paths}
    (instance / "scripts" / "schedule_review.py").write_text(
        "import sys\nraise SystemExit(9)\n",
        encoding="utf-8",
    )
    result = run(
        [
            sys.executable,
            "scripts/record_activity_result.py",
            "--activity-id",
            "act-failure",
            "--result",
            "partial",
            "--evidence-id",
            "ev-schedule-failure",
        ],
        instance,
        check=False,
    )
    assert result.returncode == 9, result.stdout + result.stderr
    assert {path: path.read_bytes() for path in tracked_paths} == before


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="studydd-fast-path-") as tmp:
        instance = create_instance(tmp)
        test_validator_requires_selector(instance)
        test_validator_uses_canonical_evidence_before_compaction(instance)
        test_cross_skill_reference_fails(instance)
        test_duplicate_evidence_fails(instance)

    with tempfile.TemporaryDirectory(prefix="studydd-selector-") as tmp:
        instance = create_instance(tmp, "Selector")
        append_evidence(instance, "ev-new", "skill-a")
        test_selector_is_read_only(instance)
        test_schedule_uses_positive_explicit_learning_step(instance)
        test_duplicate_review_fails(instance)
        test_duplicate_activity_fails(instance)

    with tempfile.TemporaryDirectory(prefix="studydd-review-failure-") as tmp:
        instance = create_instance(tmp, "ReviewFailure")
        test_review_failure_propagates(instance)

    print("Fast-path integrity tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
