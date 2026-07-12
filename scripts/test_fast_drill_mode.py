#!/usr/bin/env python3
"""Synthetic contract tests for the generic Fast Drill checkpoint lane."""

from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import fast_drill_mode as fdm


def write_yaml(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def synthetic_instance(mode: str = "learner_instance") -> Path:
    root = Path(tempfile.mkdtemp(prefix="studydd-fast-drill-"))
    write_yaml(
        root / "instance.yaml",
        {
            "apiVersion": "studydd.studydd.io/v1",
            "kind": "StudyDDInstance",
            "metadata": {"id": "synthetic-fast-drill"},
            "spec": {"mode": mode, "personalized": mode == "learner_instance", "publicSafe": mode != "learner_instance"},
        },
    )
    write_yaml(
        root / "state/LEARNER_PROFILE.yaml",
        {"learner_preferences": {"fast_drill_mode": True, "auto_state_update_during_drills": True}},
    )
    write_yaml(
        root / "state/SKILL_MAP.yaml",
        {"skills": [{"id": "skill-a", "status": "pending", "readiness": 0, "confidence": "low", "evidence": []}]},
    )
    write_yaml(root / "state/STUDY_STATE.yaml", {"active_focus": {}, "metadata": {}})
    (root / "state/EVIDENCE_LOG.md").write_text(
        "# Evidence Log\n\n## Evidence items\n\nNone yet.\n", encoding="utf-8"
    )
    return root


def append_one(root: Path, *, marker: str = "ev-1") -> None:
    assert fdm.append_checkpoint(
        question_id="q-1",
        skill_id="skill-a",
        concept="typed concept",
        answer_summary="synthetic answer",
        verdict="correct",
        correction_summary="",
        confidence="medium",
        evidence_marker=marker,
        repo_root=root,
    ) == 0


def test_versioned_append_only_and_idempotent_append() -> None:
    root = synthetic_instance()
    assert fdm.start_drill("s-1", "target-1", repo_root=root) == 0
    checkpoint = root / fdm.CHECKPOINT_RELATIVE
    header_before = checkpoint.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    append_one(root)
    after_first = checkpoint.read_bytes()
    append_one(root)
    assert checkpoint.read_bytes() == after_first
    loaded = fdm.load_checkpoint(root)
    assert loaded.metadata["format"] == fdm.CHECKPOINT_FORMAT
    assert loaded.metadata["checkpoint_version"] == 2
    assert len(loaded.records) == 1
    assert checkpoint.read_text(encoding="utf-8").startswith(header_before)


def test_typed_operations_and_invalid_record_are_rejected() -> None:
    root = synthetic_instance()
    assert fdm.execute(fdm.StartOperation("s-typed", "target-1"), root) == 0
    bad = copy.copy(fdm.AppendAnswerOperation(
        "q-1", "skill-a", "concept", "answer", "not-a-verdict", "", "medium", "ev-typed"
    ))
    try:
        fdm.execute(bad, root)
    except fdm.CheckpointError:
        pass
    else:
        raise AssertionError("invalid typed verdict was accepted")


def test_template_and_bootstrap_refusal_does_not_touch_settings() -> None:
    for mode in ("template", "bootstrap"):
        root = synthetic_instance(mode)
        profile = root / "state/LEARNER_PROFILE.yaml"
        before = profile.read_bytes()
        assert fdm.start_drill("s-refuse", "target-1", repo_root=root) == 2
        assert profile.read_bytes() == before
        assert not (root / fdm.CHECKPOINT_RELATIVE).exists()


def test_transactional_reconciliation_recovers_after_synthetic_crash() -> None:
    root = synthetic_instance()
    assert fdm.start_drill("s-crash", "target-1", repo_root=root) == 0
    append_one(root, marker="ev-crash")
    before_profile = (root / "state/LEARNER_PROFILE.yaml").read_bytes()
    try:
        fdm.end_drill(apply=True, repo_root=root, crash_after=1)
    except fdm.SimulatedCrash:
        pass
    else:
        raise AssertionError("synthetic crash did not interrupt reconciliation")

    assert (root / fdm.CHECKPOINT_RELATIVE).exists()
    report, code = fdm.recover_drill(root, apply=True)
    assert code == 0
    assert report and report["recommendation"] == "reconciled_transaction"
    assert not (root / fdm.CHECKPOINT_RELATIVE).exists()
    evidence = (root / "state/EVIDENCE_LOG.md").read_text(encoding="utf-8")
    assert evidence.count("**Evidence ID:** ev-crash") == 1
    skills = yaml.safe_load((root / "state/SKILL_MAP.yaml").read_text(encoding="utf-8"))
    assert skills["skills"][0]["status"] == "practiced"
    assert (root / "state/LEARNER_PROFILE.yaml").read_bytes() == before_profile
    # Re-running end and recover are successful no-ops.
    assert fdm.end_drill(apply=True, repo_root=root)[1] == 0
    report, code = fdm.recover_drill(root, apply=True)
    assert code == 0 and report == {"recommendation": "none", "count": 0}


def test_end_without_apply_is_a_proposal_only() -> None:
    root = synthetic_instance()
    assert fdm.start_drill("s-proposal", "target-1", repo_root=root) == 0
    append_one(root, marker="ev-proposal")
    evidence_before = (root / "state/EVIDENCE_LOG.md").read_bytes()
    proposal, code = fdm.end_drill(repo_root=root)
    assert code == 0 and proposal is not None
    assert (root / "state/EVIDENCE_LOG.md").read_bytes() == evidence_before
    assert (root / fdm.CHECKPOINT_RELATIVE).exists()


def main() -> int:
    test_versioned_append_only_and_idempotent_append()
    test_typed_operations_and_invalid_record_are_rejected()
    test_template_and_bootstrap_refusal_does_not_touch_settings()
    test_transactional_reconciliation_recovers_after_synthetic_crash()
    test_end_without_apply_is_a_proposal_only()
    print("Fast Drill checkpoint contract tests passed.")
    print("- versioned hash-linked append-only records")
    print("- typed operation validation and settings authority")
    print("- template/bootstrap refusal")
    print("- crash-interrupted transactional reconciliation and idempotent recovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
