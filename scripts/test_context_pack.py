#!/usr/bin/env python3
"""Test StudyDD context pack builder.

Creates a temporary learner instance, runs scripts/build_context_pack.py for
several tasks, and asserts inclusion/exclusion behavior.
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

    tmp = tempfile.mkdtemp(prefix="studydd-context-")
    target = Path(tmp) / "Study_Context"
    remote = "https://github.com/example/Study_Context.git"

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
    study_state["learner"]["name"] = "Context Test Learner"
    study_state["active_target_id"] = "context-target"
    study_state["active_focus"]["current_topic"] = "hybrid retrieval"
    study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

    target_dir = target / "targets" / "context-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "TARGET.yaml").write_text(
        "---\n"
        "id: context-target\n"
        "type: skill\n"
        "title: Context pack test target\n"
        "description: Temporary target for context pack test.\n"
        "study_skill: it_certification\n",
        encoding="utf-8",
    )

    skill_map_path = target / "state" / "SKILL_MAP.yaml"
    skill_map = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
    skill_map["skills"] = [
        {
            "id": "context-search-basics",
            "label": "Keyword vs vector search",
            "status": "weak",
            "readiness": 35,
            "confidence": "low",
            "evidence": ["ev_context_001"],
            "next_validation_question": "Q-CONTEXT-001",
        },
        {
            "id": "context-unrelated",
            "label": "Unrelated skill",
            "status": "pending",
            "readiness": 0,
            "confidence": "low",
            "evidence": [],
            "next_validation_question": "",
        },
    ]
    skill_map_path.write_text(yaml.safe_dump(skill_map, sort_keys=False), encoding="utf-8")

    evidence_path = target / "state" / "EVIDENCE_LOG.md"
    evidence_text = evidence_path.read_text(encoding="utf-8")
    evidence_entry = (
        "\n- **Evidence ID:** ev_context_001\n"
        "- **Date:** 2026-06-24\n"
        "- **Target ID:** context-target\n"
        "- **Skill ID:** context-search-basics\n"
        "- **Question ID:** Q-CONTEXT-001\n"
        "- **Question summary:** Explain keyword vs vector search.\n"
        "- **Learner answer summary:** Partial answer.\n"
        "- **Verdict:** partial\n"
        "- **Explanation:** Missing scenario.\n"
        "- **Confidence:** low\n"
    )
    evidence_path.write_text(evidence_text + evidence_entry, encoding="utf-8")

    # Add a due review for context-search-basics.
    review_state_path = target / "reviews" / "REVIEW_STATE.yaml"
    review_state = yaml.safe_load(review_state_path.read_text(encoding="utf-8")) or {}
    review_state["review_items"] = [
        {
            "id": "rev_context_001",
            "skill_id": "context-search-basics",
            "evidence_id": "ev_context_001",
            "target_id": "context-target",
            "due_at": "2026-06-24T09:00:00+00:00",
            "last_reviewed_at": None,
            "interval_days": 1,
            "stability": None,
            "difficulty": None,
            "lapses": 0,
            "priority": "normal",
            "status": "due",
            "source": "partial_answer",
            "override_count": 0,
        }
    ]
    review_state_path.write_text(yaml.safe_dump(review_state, sort_keys=False), encoding="utf-8")

    return target


def build_stale_source_instance() -> Path:
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="studydd-stale-source-")
    target = Path(tmp) / "Study_StaleSource"
    remote = "https://github.com/example/Study_StaleSource.git"

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
    study_state["learner"]["name"] = "Stale Source Test Learner"
    study_state["active_target_id"] = "stale-source-target"
    study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

    target_dir = target / "targets" / "stale-source-target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "TARGET.yaml").write_text(
        "---\n"
        "id: stale-source-target\n"
        "type: certification\n"
        "title: Stale source test target\n"
        "description: Temporary volatile target for stale source freshness test.\n"
        "volatility: volatile\n"
        "study_skill: it_certification\n",
        encoding="utf-8",
    )

    source_state = {
        "metadata": {"template_version": "0.9.0", "last_updated": "2026-06-27"},
        "sources": [
            {
                "id": "stale-docs",
                "authority": "official",
                "target_ids": ["stale-source-target"],
                "last_checked_at": "2026-01-01T00:00:00+00:00",
                "volatility": "volatile",
            }
        ],
    }
    (target / "sources" / "SOURCE_STATE.yaml").write_text(
        yaml.safe_dump(source_state, sort_keys=False), encoding="utf-8"
    )

    return target


def context_pack_text(target: Path, task: str) -> str:
    run([sys.executable, "scripts/compact_state.py"], target)
    result = run(
        [sys.executable, "scripts/build_context_pack.py", "--task", task],
        target,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, ["scripts/build_context_pack.py"])
    return (target / ".studydd" / "context_pack.md").read_text(encoding="utf-8")


def test_context_pack_includes_source_freshness_status() -> None:
    print("\nTest: start_session includes source freshness status")
    target = build_instance()
    text = context_pack_text(target, "start_session")
    assert "Source freshness:" in text
    assert "Status: not_required" in text


def test_context_pack_stays_generic_in_template_mode_no_active_target() -> None:
    print("\nTest: template mode context pack stays generic with no active target")
    run([sys.executable, "scripts/build_context_pack.py", "--task", "start_session"], ROOT)
    text = (ROOT / ".studydd" / "context_pack.md").read_text(encoding="utf-8")
    assert "- **Mode:** template" in text
    assert "- **Target ID:** none" in text
    assert "Source freshness:" in text
    assert "- Status: not_required" in text
    assert "**Recommended activity:** retrieval_question" in text
    assert "generic template fallback" in text
    assert "Study_Context" not in text, "Template pack must not leak temp instance learner name"
    assert "Context Test Learner" not in text, "Template pack must not leak learner name"


def test_context_pack_shows_stale_source_freshness_when_relevant() -> None:
    print("\nTest: context pack surfaces stale source freshness")
    stale_target = build_stale_source_instance()
    stale_text = context_pack_text(stale_target, "start_session")
    assert "**Recommended activity:** recent_info_check" in stale_text
    assert "Source freshness:" in stale_text
    assert "Status: stale" in stale_text
    assert "source_freshness_stale" in stale_text
    assert "source_metadata" in stale_text


def main() -> int:
    print("StudyDD context pack test")
    print("=========================")

    target = build_instance()

    print("\nTest: start_session includes canonical state and active study skill")
    text = context_pack_text(target, "start_session")
    assert "state/STUDY_STATE.yaml" in text
    assert "state/SKILL_MAP.yaml" in text
    assert "reviews/REVIEW_STATE.yaml" in text
    assert "targets/context-target/TARGET.yaml" in text
    assert "**Study skill:** it_certification" in text
    assert "study_skills/it_certification/SKILL.md" in text

    print("\nTest: start_session skips raw logs by default")
    assert "`state/EVIDENCE_LOG.md`" in text
    assert "raw audit log; indexed evidence is enough" in text
    assert "`sessions/SESSION_LOG.md`" in text
    assert "raw audit log; session summaries are enough" in text
    assert "`reviews/REVIEW_OVERRIDES.md`" in text
    assert "raw audit log; not needed for this task" in text

    print("\nTest: start_session includes due review")
    assert "rev_context_001" in text
    assert "context-search-basics" in text

    print("\nTest: start_session includes next activity recommendation reason")
    assert "## Next activity recommendation" in text
    assert "**Recommended activity:** spaced_review" in text
    assert "Rule: review-first doctrine" in text
    assert "**Expected evidence:** typed_answer, transcript, screenshot" in text

    test_context_pack_includes_source_freshness_status()
    test_context_pack_stays_generic_in_template_mode_no_active_target()
    test_context_pack_shows_stale_source_freshness_when_relevant()

    print("\nTest: audit includes raw log references")
    text = context_pack_text(target, "audit")
    assert "state/EVIDENCE_LOG.md" in text
    assert "sessions/SESSION_LOG.md" in text
    assert "reviews/REVIEW_OVERRIDES.md" in text

    print("\nTest: grade context includes relevant skill, not every skill")
    text = context_pack_text(target, "grade_answer")
    assert "context-search-basics" in text
    # The relevant-skills section should highlight the active/weak skill, not unrelated skills.
    relevant_section = text.split("## Relevant skills for this task", 1)[1].split("##", 1)[0]
    assert "context-search-basics" in relevant_section
    assert "context-unrelated" not in relevant_section

    print("\nTest: context pack is gitignored")
    gitignore = target / ".gitignore"
    assert gitignore.is_file()
    assert ".studydd/" in gitignore.read_text(encoding="utf-8")

    print("\nRunning validator")
    val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(val.stdout)
    if val.returncode != 0:
        print(val.stderr)
        return 1

    print("Context pack test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
