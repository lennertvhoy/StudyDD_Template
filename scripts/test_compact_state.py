#!/usr/bin/env python3
"""Test StudyDD state compaction.

Creates a temporary learner instance, adds fake evidence and session entries,
runs scripts/compact_state.py, and asserts the derived summaries are correct.
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
    print("StudyDD compact state test")
    print("==========================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    with tempfile.TemporaryDirectory(prefix="studydd-compact-") as tmp:
        target = Path(tmp) / "Study_Compact"
        remote = "https://github.com/example/Study_Compact.git"

        result = run(
            [sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote],
            ROOT,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            return 1

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = yaml.safe_load(mode_path.read_text(encoding="utf-8")) or {}
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        mode_data["public_safe"] = "false_or_review_required"
        mode_path.write_text(yaml.safe_dump(mode_data, sort_keys=False), encoding="utf-8")

        study_state_path = target / "state" / "STUDY_STATE.yaml"
        study_state = yaml.safe_load(study_state_path.read_text(encoding="utf-8")) or {}
        study_state["learner"]["name"] = "Compact Test Learner"
        study_state["active_target_id"] = "compact-target"
        study_state["active_focus"]["current_topic"] = "keyword vs vector retrieval"
        study_state_path.write_text(yaml.safe_dump(study_state, sort_keys=False), encoding="utf-8")

        target_dir = target / "targets" / "compact-target"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "TARGET.yaml").write_text(
            "---\n"
            "id: compact-target\n"
            "type: skill\n"
            "title: Compact test target\n"
            "description: Temporary target for compact state test.\n",
            encoding="utf-8",
        )

        evidence_path = target / "state" / "EVIDENCE_LOG.md"
        evidence_text = evidence_path.read_text(encoding="utf-8")
        evidence_entry = (
            "\n- **Evidence ID:** ev_compact_001\n"
            "- **Date:** 2026-06-24\n"
            "- **Target ID:** compact-target\n"
            "- **Skill ID:** compact-search-basics\n"
            "- **Question ID:** Q-COMPACT-001\n"
            "- **Question summary:** Explain keyword vs vector search.\n"
            "- **Learner answer summary:** Correctly distinguished term matching from semantic similarity.\n"
            "- **Verdict:** correct\n"
            "- **Explanation:** Initial answer was complete and concrete.\n"
            "- **Confidence:** medium\n"
        )
        evidence_path.write_text(evidence_text + evidence_entry, encoding="utf-8")

        session_path = target / "sessions" / "SESSION_LOG.md"
        session_text = session_path.read_text(encoding="utf-8")
        session_entry = (
            "\n- **Date:** 2026-06-24\n"
            "- **Target ID:** compact-target\n"
            "- **Focus:** keyword vs vector search\n"
            "- **Questions asked:** Q-COMPACT-001\n"
            "- **Result summary:** Learner answered correctly.\n"
            "- **Evidence added:** ev_compact_001\n"
            "- **Reviews added:** none\n"
            "- **State changes:** Added skill compact-search-basics, readiness 55, status practiced.\n"
            "- **Next action proposed:** Answer the next diagnostic question.\n"
        )
        session_text = session_text.replace(
            "## Sessions\n\nNone yet.",
            "## Sessions" + session_entry,
        )
        session_path.write_text(session_text, encoding="utf-8")

        print("Running compact_state.py")
        compact = run([sys.executable, "scripts/compact_state.py"], target, check=False)
        print(compact.stdout)
        if compact.returncode != 0:
            print(compact.stderr)
            return 1

        current_context_path = target / "state" / "CURRENT_CONTEXT.md"
        evidence_index_path = target / "state" / "EVIDENCE_INDEX.yaml"
        session_summaries_path = target / "sessions" / "SESSION_SUMMARIES.md"

        assert current_context_path.is_file(), "Missing state/CURRENT_CONTEXT.md"
        assert evidence_index_path.is_file(), "Missing state/EVIDENCE_INDEX.yaml"
        assert session_summaries_path.is_file(), "Missing sessions/SESSION_SUMMARIES.md"

        context_text = current_context_path.read_text(encoding="utf-8")
        assert "## Active target" in context_text
        assert "## Reviews" in context_text
        assert "## Weak skills" in context_text
        assert "## Next action" in context_text
        assert "compact-target" in context_text

        evidence_index = yaml.safe_load(evidence_index_path.read_text(encoding="utf-8")) or {}
        assert evidence_index.get("count") == 1, f"Expected 1 evidence item, got {evidence_index.get('count')}"
        items = evidence_index.get("items") or []
        assert any(item.get("evidence_id") == "ev_compact_001" for item in items), "ev_compact_001 not in evidence index"

        summaries_text = session_summaries_path.read_text(encoding="utf-8")
        assert "**Total sessions:** 1" in summaries_text
        assert "compact-target" in summaries_text
        assert "No sessions recorded yet." not in summaries_text

        print("Running validator")
        val = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
        print(val.stdout)
        if val.returncode != 0:
            print(val.stderr)
            return 1

        print("Compact state test passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
