from __future__ import annotations

import json
import subprocess
from pathlib import Path


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
