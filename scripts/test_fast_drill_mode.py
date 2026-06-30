#!/usr/bin/env python3
"""Tests for scripts/fast_drill_mode.py.

Covers checkpoint lifecycle, reconciliation, crash recovery, major-transition
detection, and template-mode refusal.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "scripts"
SCRIPT_NAME = "scripts/fast_drill_mode.py"

# Make the script importable as a module.
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import fast_drill_mode as fdm


def load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save_yaml(path: Path, data: dict) -> None:
    import yaml

    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def create_temp_instance(
    tmp: str,
    name: str,
    target_id: str,
    skills: list[dict] | None = None,
    review_items: list[dict] | None = None,
) -> Path:
    target = Path(tmp) / f"StudyDD_{name}"
    remote = f"https://github.com/example/StudyDD_{name}.git"
    run(
        [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote],
        cwd=ROOT,
    )

    mode_path = target / "state" / "STUDYDD_MODE.yaml"
    mode_data = load_yaml(mode_path)
    mode_data["mode"] = "learner_instance"
    mode_data["personalized"] = True
    mode_data["public_safe"] = "false_or_review_required"
    save_yaml(mode_path, mode_data)

    study_state = load_yaml(target / "state" / "STUDY_STATE.yaml")
    study_state["learner"]["name"] = f"{name} Test Learner"
    study_state["active_target_id"] = target_id
    save_yaml(target / "state" / "STUDY_STATE.yaml", study_state)

    (target / "targets" / target_id).mkdir(parents=True, exist_ok=True)
    (target / "targets" / target_id / "TARGET.yaml").write_text(
        f"---\nid: {target_id}\ntype: certification\nstudy_skill: generic\n",
        encoding="utf-8",
    )

    skill_map = load_yaml(target / "state" / "SKILL_MAP.yaml")
    skill_map["skills"] = skills or []
    save_yaml(target / "state" / "SKILL_MAP.yaml", skill_map)

    review_state = load_yaml(target / "reviews" / "REVIEW_STATE.yaml")
    review_state["review_items"] = review_items or []
    save_yaml(target / "reviews" / "REVIEW_STATE.yaml", review_state)

    # Ensure evidence log has the expected marker.
    ev_path = target / "state" / "EVIDENCE_LOG.md"
    if not ev_path.is_file():
        ev_path.write_text(
            "# Evidence Log\n\n## Evidence items\n\nNone yet.\n",
            encoding="utf-8",
        )

    return target


def test_fast_drill_enabled_default() -> None:
    # The public template enables fast drill mode as a generic default.
    assert fdm.fast_drill_enabled(ROOT) is True
    assert fdm.auto_state_update_during_drills(ROOT) is True


def test_start_and_append() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(
            tmp,
            "drill_start",
            "demo-target",
            skills=[{"id": "skill-a", "label": "Skill A", "status": "pending", "readiness": 0}],
        )
        rc = fdm.start_drill(
            session_id="S-001",
            target_id="demo-target",
            mode="normal",
            drill_type="retrieval_question",
            repo_root=instance,
        )
        assert rc == 0
        cp_path = instance / "state" / "ACTIVE_DRILL_SESSION.md"
        assert cp_path.is_file()

        rc = fdm.append_checkpoint(
            question_id="Q-001",
            skill_id="skill-a",
            concept="concept one",
            answer_summary="answered",
            verdict="correct",
            correction_summary="",
            confidence="medium",
            evidence_marker="E-001",
            repo_root=instance,
        )
        assert rc == 0

        checkpoint = fdm.load_checkpoint(instance)
        assert checkpoint["metadata"]["session_id"] == "S-001"
        assert len(checkpoint["entries"]) == 1
        assert checkpoint["entries"][0]["evidence_marker"] == "E-001"
        assert fdm.is_drill_active(instance) is True


def test_end_dry_run_then_apply() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(
            tmp,
            "drill_end",
            "demo-target",
            skills=[{"id": "skill-a", "label": "Skill A", "status": "pending", "readiness": 0}],
        )
        fdm.start_drill("S-002", "demo-target", repo_root=instance)
        fdm.append_checkpoint("Q-001", "skill-a", "c1", "ok", "correct", "", "medium", "E-001", repo_root=instance)
        fdm.append_checkpoint("Q-002", "skill-a", "c2", "partial ok", "partial", "", "low", "E-002", repo_root=instance)

        proposal, rc = fdm.end_drill(apply=False, repo_root=instance)
        assert rc == 0
        assert proposal is not None
        assert len(proposal["evidence_items"]) == 2
        assert (instance / "state" / "ACTIVE_DRILL_SESSION.md").is_file()

        proposal, rc = fdm.end_drill(apply=True, repo_root=instance)
        assert rc == 0
        cp_path = instance / "state" / "ACTIVE_DRILL_SESSION.md"
        assert not cp_path.is_file()

        skill_map = load_yaml(instance / "state" / "SKILL_MAP.yaml")
        skill = next(s for s in skill_map["skills"] if s["id"] == "skill-a")
        # Partial verdict on a low-readiness skill dominates; it is marked weak.
        assert skill["status"] == "weak"
        assert skill["readiness"] == 35
        assert "E-001" in skill["evidence"]
        assert "E-002" in skill["evidence"]

        ev_text = (instance / "state" / "EVIDENCE_LOG.md").read_text(encoding="utf-8")
        assert "E-001" in ev_text
        assert "E-002" in ev_text

        study_state = load_yaml(instance / "state" / "STUDY_STATE.yaml")
        assert study_state["active_focus"]["next_question"] == proposal["next_action"]

        next_text = (instance / "NEXT_ACTIONS.md").read_text(encoding="utf-8")
        assert proposal["next_action"] in next_text


def test_reconcile_prefers_weak_skill() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(
            tmp,
            "drill_weak",
            "demo-target",
            skills=[
                {"id": "skill-a", "label": "Skill A", "status": "practiced", "readiness": 55},
                {"id": "skill-b", "label": "Skill B", "status": "weak", "readiness": 25},
            ],
        )
        fdm.start_drill("S-003", "demo-target", repo_root=instance)
        fdm.append_checkpoint("Q-001", "skill-a", "c1", "ok", "correct", "", "medium", "E-001", repo_root=instance)
        proposal, rc = fdm.end_drill(apply=True, repo_root=instance)
        assert rc == 0
        assert "skill-b" in proposal["next_action"]


def test_reconcile_prefers_due_review() -> None:
    due_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(
            tmp,
            "drill_review",
            "demo-target",
            skills=[{"id": "skill-a", "label": "Skill A", "status": "practiced", "readiness": 55}],
            review_items=[{"id": "R-001", "skill_id": "skill-a", "due_at": due_at}],
        )
        fdm.start_drill("S-004", "demo-target", repo_root=instance)
        fdm.append_checkpoint("Q-001", "skill-a", "c1", "ok", "correct", "", "medium", "E-001", repo_root=instance)
        proposal, rc = fdm.end_drill(apply=True, repo_root=instance)
        assert rc == 0
        assert "R-001" in proposal["next_action"]


def test_recover_recommends_resume_or_reconcile() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(tmp, "drill_recover", "demo-target")
        fdm.start_drill("S-005", "demo-target", repo_root=instance)
        result, rc = fdm.recover_drill(instance)
        assert rc == 0
        assert result is not None
        assert result["recommendation"] == "resume"

        # Simulate an old checkpoint by rewriting started_at.
        cp_path = instance / "state" / "ACTIVE_DRILL_SESSION.md"
        old = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
        text = cp_path.read_text(encoding="utf-8")
        text = text.replace(result["checkpoint"]["metadata"]["started_at"], old)
        cp_path.write_text(text, encoding="utf-8")
        result, rc = fdm.recover_drill(instance)
        assert result is not None
        assert result["recommendation"] == "reconcile"


def test_requires_immediate_reconciliation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = create_temp_instance(
            tmp,
            "drill_transition",
            "demo-target",
            skills=[{"id": "skill-a", "label": "Skill A", "status": "weak", "readiness": 25}],
        )
        assert fdm.requires_immediate_reconciliation(
            {"skill_id": "skill-a", "verdict": "correct"}, repo_root=instance
        )
        assert not fdm.requires_immediate_reconciliation(
            {"skill_id": "skill-a", "verdict": "partial"}, repo_root=instance
        )


def test_template_mode_refuses_checkpoint() -> None:
    result = subprocess.run(
        [sys.executable, SCRIPT_NAME, "start", "--session-id", "S-T", "--target-id", "t"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "template" in (result.stdout + result.stderr).lower()


def test_cli_demo_runs_in_template_mode() -> None:
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT_NAME,
            "start",
            "--session-id",
            "S-DEMO",
            "--target-id",
            "demo-target",
            "--demo",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    cp_path = ROOT / "state" / "ACTIVE_DRILL_SESSION.md"
    assert cp_path.is_file()
    # Clean up so the template validator does not see the checkpoint.
    cp_path.unlink()


if __name__ == "__main__":
    tests = [func for name, func in list(globals().items()) if name.startswith("test_") and callable(func)]
    for func in tests:
        print(f"Running {func.__name__}...")
        func()
    print("All fast-drill-mode tests passed.")
