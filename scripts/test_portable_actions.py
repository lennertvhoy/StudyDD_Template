from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_plan_next_session_is_typed_and_read_only(tmp_path: Path) -> None:
    state = tmp_path / "state"
    state.mkdir()
    (state / "STUDY_STATE.yaml").write_text("active_target_id: ''\n", encoding="utf-8")
    (state / "SKILL_MAP.yaml").write_text("skills: []\n", encoding="utf-8")
    (state / "ACTIVITY_STATE.yaml").write_text("recent_activities: []\n", encoding="utf-8")
    (tmp_path / "reviews").mkdir()
    (tmp_path / "reviews/REVIEW_STATE.yaml").write_text("review_items: []\n", encoding="utf-8")
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources/SOURCE_STATE.yaml").write_text("sources: []\n", encoding="utf-8")
    (tmp_path / "activities").mkdir()
    (tmp_path / "activities/ACTIVITY_TEMPLATES.yaml").write_text("templates: []\n", encoding="utf-8")
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    result = subprocess.run(["python3", str(ROOT / "scripts/portable_actions.py"), "--root", str(tmp_path), "--inputs", json.dumps({"timeAvailableMinutes": 25})], capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    assert payload["formatVersion"] == "studydd.action-result/v1"
    assert payload["actionId"] == "studydd.plan-next-session/v1"
    assert payload["stateChangeProposals"] == []
    assert before == sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))


def test_proposal_apply_requires_instance_mode_and_preserves_activity_identity(tmp_path: Path) -> None:
    target = tmp_path / "instance"
    subprocess.run(["python3", str(ROOT / "scripts/create_instance.py"), "--target", str(target), "--remote", "https://github.com/example/StudyDD_PortableActions.git"], capture_output=True, text=True, check=True)
    descriptor_path = target / "instance.yaml"
    descriptor = yaml.safe_load(descriptor_path.read_text(encoding="utf-8")) or {}
    descriptor.setdefault("spec", {})["mode"] = "learner_instance"
    descriptor["spec"]["personalized"] = True
    descriptor["spec"]["publicSafe"] = False
    descriptor_path.write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
    mode = target / "state/STUDYDD_MODE.yaml"
    mode_data = yaml.safe_load(mode.read_text(encoding="utf-8")) or {}
    mode_data["mode"] = "learner_instance"
    mode_data["personalized"] = True
    mode_data["public_safe"] = "false_or_review_required"
    mode.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")
    study_path = target / "state/STUDY_STATE.yaml"
    study = yaml.safe_load(study_path.read_text(encoding="utf-8")) or {}
    study.setdefault("learner", {})["name"] = "Synthetic Owner"
    study["active_target_id"] = "portable-target"
    study_path.write_text(yaml.safe_dump(study, sort_keys=False), encoding="utf-8")
    target_dir = target / "targets/portable-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "TARGET.yaml").write_text("id: portable-target\ntitle: Portable target\nstudy_skill: it_certification\nvolatility: low\n", encoding="utf-8")
    skill_map_path = target / "state/SKILL_MAP.yaml"
    skill_map = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
    skill_map["skills"] = [{"id": "portable-skill", "label": "Portable skill", "status": "pending", "readiness": 0, "confidence": "low", "evidence": []}]
    skill_map_path.write_text(yaml.safe_dump(skill_map, sort_keys=False), encoding="utf-8")
    planned = subprocess.run(
        ["python3", str(target / "scripts/portable_actions.py"), "--root", str(target), "--inputs", json.dumps({"includeFastDrillProposal": True})],
        capture_output=True, text=True, check=True,
    )
    proposal = json.loads(planned.stdout)["stateChangeProposals"][0]
    applied = subprocess.run(
        ["python3", str(target / "scripts/portable_actions.py"), "--root", str(target), "--apply-proposal"],
        input=json.dumps(proposal), capture_output=True, text=True, check=True,
    )
    receipt = json.loads(applied.stdout)
    assert receipt["validation"] == "passed"
    state = (target / "state/ACTIVITY_STATE.yaml").read_text(encoding="utf-8")
    assert proposal["operations"][0]["activity"]["id"] in state
