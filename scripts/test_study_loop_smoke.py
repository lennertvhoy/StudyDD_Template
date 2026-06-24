#!/usr/bin/env python3
"""Deterministic study-loop smoke test.

Creates a temporary learner instance, moves it through bootstrap to
learner_instance, simulates one question/answer/evidence/review/session cycle,
and validates the result.
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


def main() -> int:
    print("StudyDD study-loop smoke test")
    print("=============================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    with tempfile.TemporaryDirectory(prefix="studydd-study-loop-") as tmp:
        target = Path(tmp) / "Study_LoopSmoke"
        remote = "https://github.com/example/Study_LoopSmoke.git"

        result = run(
            [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote],
            ROOT,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return 1

        # Move from bootstrap to learner_instance with fake state.
        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        mode_data["public_safe"] = "false_or_review_required"
        mode_path.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")

        study_state_path = target / "state" / "STUDY_STATE.yaml"
        study_state = yaml.safe_load(study_state_path.read_text(encoding="utf-8")) or {}
        study_state["learner"]["name"] = "Loop Smoke Learner"
        study_state["active_target_id"] = "loop-smoke-target"
        study_state["active_focus"]["current_topic"] = "keyword vs vector retrieval"
        study_state["active_focus"]["next_question"] = "Q-LOOP-002"
        study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

        target_dir = target / "targets" / "loop-smoke-target"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "TARGET.yaml").write_text(
            "---\n"
            "id: loop-smoke-target\n"
            "type: skill\n"
            "title: Loop smoke target\n"
            "description: Temporary target for study-loop smoke test.\n",
            encoding="utf-8",
        )

        skill_map_path = target / "state" / "SKILL_MAP.yaml"
        skill_map = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
        skill_map["skills"] = [
            {
                "id": "loop-search-basics",
                "label": "Keyword vs vector search",
                "status": "practiced",
                "readiness": 55,
                "confidence": "medium",
                "evidence": ["Q-LOOP-001"],
                "next_validation_question": "Q-LOOP-002",
            }
        ]
        skill_map_path.write_text(yaml.safe_dump(skill_map, sort_keys=False), encoding="utf-8")

        questions_dir = target_dir / "questions"
        questions_dir.mkdir(parents=True, exist_ok=True)
        (questions_dir / "Q-LOOP-001.yaml").write_text(
            "---\n"
            "id: Q-LOOP-001\n"
            "target_id: loop-smoke-target\n"
            "skill_id: loop-search-basics\n"
            "cognitive_level: explain\n"
            "difficulty: 2\n"
            "source_ref: smoke-source\n"
            "public_prompt: Explain the difference between keyword and vector search.\n"
            "private_answer_key: |\n"
            "  Keyword search matches terms; vector search matches semantic similarity.\n"
            "rubric:\n"
            "  - Mentions term matching\n"
            "  - Mentions semantic similarity\n"
            "common_traps:\n"
            "  - Calling keyword search dumb\n"
            "transfer_probe: When would you combine them?\n"
            "last_used: 2026-06-24\n"
            "cooldown_days: 7\n",
            encoding="utf-8",
        )

        evidence_path = target / "state" / "EVIDENCE_LOG.md"
        evidence_text = evidence_path.read_text(encoding="utf-8")
        evidence_entry = (
            "\n- **Date:** 2026-06-24\n"
            "- **Target ID:** loop-smoke-target\n"
            "- **Skill ID:** loop-search-basics\n"
            "- **Question ID:** Q-LOOP-001\n"
            "- **Question summary:** Explain keyword vs vector search.\n"
            "- **Learner answer summary:** Correctly distinguished term matching from semantic similarity.\n"
            "- **Verdict:** correct\n"
            "- **Explanation:** Initial answer was complete and concrete.\n"
            "- **Confidence:** medium\n"
        )
        evidence_path.write_text(evidence_text + evidence_entry, encoding="utf-8")

        print("Scheduling review")
        sched = run(
            [
                sys.executable,
                "scripts/schedule_review.py",
                "--skill-id",
                "loop-search-basics",
                "--evidence-id",
                "Q-LOOP-001",
                "--target-id",
                "loop-smoke-target",
                "--grade",
                "partial",
                "--confidence",
                "low",
                "--now",
                "2026-06-24T10:00:00+00:00",
                "--prompt",
                "Describe a scenario where hybrid retrieval outperforms either alone.",
                "--source",
                "partial_answer",
            ],
            target,
            check=False,
        )
        print(sched.stdout)
        if sched.returncode != 0:
            print(sched.stderr)
            return 1

        review_state_path = target / "reviews" / "REVIEW_STATE.yaml"
        review_state = yaml.safe_load(review_state_path.read_text(encoding="utf-8")) or {}
        scheduled_items = review_state.get("review_items", [])
        assert scheduled_items, "No review item was scheduled"
        scheduled_review_id = scheduled_items[0]["id"]

        print("Selecting next action when review is overdue")
        selector = run(
            [
                sys.executable,
                "scripts/select_next_study_action.py",
                "--now",
                "2026-06-25T12:00:00+00:00",
            ],
            target,
            check=False,
        )
        print(selector.stdout)
        if selector.returncode != 0:
            print(selector.stderr)
            return 1
        if "review first" not in selector.stdout.lower():
            print("Selector did not recommend review first")
            return 1

        print("Recording override")
        review_state = yaml.safe_load(review_state_path.read_text(encoding="utf-8")) or {}
        for item in review_state.get("review_items", []):
            if item.get("skill_id") == "loop-search-basics":
                item["override_count"] = 1
        review_state_path.write_text(yaml.safe_dump(review_state, sort_keys=False), encoding="utf-8")

        overrides_path = target / "reviews" / "REVIEW_OVERRIDES.md"
        overrides_text = overrides_path.read_text(encoding="utf-8")
        override_entry = (
            "\n- **Timestamp:** 2026-06-25T12:05:00+00:00\n"
            f"- **Learner:** Loop Smoke Learner\n"
            f"- **Skipped review IDs:** {scheduled_review_id}\n"
            "- **Reason:** learner wanted to continue with new material\n"
            "- **Chosen action:** answer question Q-LOOP-002\n"
            "- **Agent recommendation:** review loop-search-basics first\n"
            "- **Next review recommendation:** reschedule the skipped review within 24 hours\n"
        )
        overrides_text = overrides_text.replace(
            "## Overrides\n\nNone yet.",
            "## Overrides" + override_entry,
        )
        overrides_path.write_text(overrides_text, encoding="utf-8")

        session_path = target / "sessions" / "SESSION_LOG.md"
        session_text = session_path.read_text(encoding="utf-8")
        session_entry = (
            "\n- **Date:** 2026-06-24\n"
            "- **Target ID:** loop-smoke-target\n"
            "- **Focus:** keyword vs vector search\n"
            "- **Questions asked:** Q-LOOP-001\n"
            "- **Result summary:** Learner answered correctly.\n"
            "- **Evidence added:** Q-LOOP-001\n"
            f"- **Reviews added:** {scheduled_review_id}\n"
            "- **State changes:** Added skill loop-search-basics, readiness 55, status practiced; scheduled review.\n"
            "- **Next action proposed:** Answer the next diagnostic question.\n"
        )
        session_text = session_text.replace(
            "## Sessions\n\nNone yet.",
            "## Sessions" + session_entry,
        )
        session_path.write_text(session_text, encoding="utf-8")

        next_path = target / "NEXT_ACTIONS.md"
        next_path.write_text(
            "# NEXT_ACTIONS — Active Queue\n\n"
            "> **Agent-maintained.** This is the single canonical next-action file for the repo.\n\n"
            "## Current next action\n\n"
            "Answer question Q-LOOP-002 for skill loop-search-basics to gather varied evidence.\n\n"
            "## Pending actions\n\n"
            "- Continue building varied evidence for loop-search-basics.\n\n"
            "## Recently completed\n\n"
            "- Q-LOOP-001 answered correctly.\n",
            encoding="utf-8",
        )

        print("Running full learner-instance validation")
        val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
        print(val.stdout)
        if val.returncode != 0:
            print(val.stderr)
            return 1

        skill_data = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
        assert any("Q-LOOP-001" in (s.get("evidence") or []) for s in skill_data.get("skills", [])), \
            "Skill evidence reference drift"
        assert "Q-LOOP-001" in evidence_path.read_text(encoding="utf-8"), "Evidence log missing Q-LOOP-001"
        review_queue_path = target / "reviews" / "REVIEW_QUEUE.md"
        assert scheduled_review_id in review_queue_path.read_text(encoding="utf-8"), "Review queue missing scheduled review"

        print("Study-loop smoke test passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
