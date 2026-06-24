#!/usr/bin/env python3
"""StudyDD repo health and educational-drift validator.

Supports the agent workflow by checking that required files exist,
YAML parses, required keys are present, and common educational drift
is caught before it harms the learner.

If PyYAML is not installed, YAML parsing is skipped and a note is printed.
Install PyYAML for full validation:
    pip install pyyaml
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ROOT_FILES = [
    "README.md",
    "AGENTS.md",
    "NEXT_ACTIONS.md",
    "LICENSE.md",
    "CONTRIBUTING.md",
]

REQUIRED_DOC_FILES = [
    "docs/agent-native-quickstart.md",
    "docs/how-to-use-with-codex.md",
    "docs/how-to-use-with-kimi-code.md",
    "docs/how-to-use-with-claude-code.md",
    "docs/how-to-use-with-cursor.md",
    "docs/studydd-principles.md",
    "docs/inspect-and-override-state.md",
]

REQUIRED_STATE_FILES = [
    "state/STUDY_STATUS.md",
    "state/STUDY_STATE.yaml",
    "state/STUDY_BACKLOG.md",
    "state/EVIDENCE_LOG.md",
    "state/SKILL_MAP.yaml",
]

REQUIRED_TARGET_FILES = [
    "targets/README.md",
]

REQUIRED_REVIEW_FILES = [
    "reviews/README.md",
    "reviews/REVIEW_QUEUE.md",
]

REQUIRED_SESSION_FILES = [
    "sessions/README.md",
    "sessions/SESSION_LOG.md",
]

REQUIRED_SOURCE_FILES = [
    "sources/README.md",
    "sources/SOURCE_INDEX.md",
]

REQUIRED_PROTOCOL_FILES = [
    "protocols/TUTOR_PROTOCOL.md",
    "protocols/SESSION_TEMPLATE.md",
    "protocols/START_SESSION.md",
    "protocols/SELECT_NEXT_ACTION.md",
    "protocols/ASK_QUESTION.md",
    "protocols/GRADE_ANSWER.md",
    "protocols/UPDATE_STATE.md",
    "protocols/SCHEDULE_REVIEW.md",
    "protocols/CLOSE_SESSION.md",
    "protocols/SOURCE_TRUST.md",
    "protocols/READINESS_POLICY.md",
    "protocols/QUESTION_QUALITY.md",
    "protocols/MISTAKE_TAXONOMY.md",
    "protocols/LOW_ENERGY_MODE.md",
]

REQUIRED_PROMPT_FILES = [
    "PROMPTS/coding_agent_start_prompt.md",
    "PROMPTS/ai_tutor_prompt.md",
    "PROMPTS/study_session_prompt.md",
    "PROMPTS/exam_drill_prompt.md",
    "PROMPTS/reflection_prompt.md",
    "PROMPTS/update_state_prompt.md",
    "PROMPTS/interview_prep_prompt.md",
    "PROMPTS/grade_and_update_state_prompt.md",
    "PROMPTS/repair_state_prompt.md",
    "PROMPTS/add_target_prompt.md",
    "PROMPTS/refresh_source_map_prompt.md",
    "PROMPTS/checkpoint_session_prompt.md",
    "PROMPTS/close_session_prompt.md",
]

REQUIRED_SCRIPT_FILES = [
    "scripts/check_studydd.py",
    "scripts/agent_preflight.py",
    "scripts/agent_consistency_check.py",
    "scripts/agent_evidence_check.py",
]

REQUIRED_AI103_EXAMPLE_FILES = [
    "EXAMPLES/ai-103-example/NEXT_ACTIONS.md",
    "EXAMPLES/ai-103-example/state/STUDY_STATUS.md",
    "EXAMPLES/ai-103-example/state/STUDY_STATE.yaml",
    "EXAMPLES/ai-103-example/state/SKILL_MAP.yaml",
    "EXAMPLES/ai-103-example/reviews/REVIEW_QUEUE.md",
    "EXAMPLES/ai-103-example/sessions/SESSION_LOG.md",
    "EXAMPLES/ai-103-example/sources/SOURCE_INDEX.md",
    "EXAMPLES/ai-103-example/targets/ai-103/TARGET.yaml",
]

REQUIRED_INTERVIEW_EXAMPLE_FILES = [
]

REQUIRED_GITHUB_TEMPLATES = [
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/pull_request_template.md",
]

REQUIRED_FILES = (
    REQUIRED_ROOT_FILES
    + REQUIRED_DOC_FILES
    + REQUIRED_STATE_FILES
    + REQUIRED_TARGET_FILES
    + REQUIRED_REVIEW_FILES
    + REQUIRED_SESSION_FILES
    + REQUIRED_SOURCE_FILES
    + REQUIRED_PROTOCOL_FILES
    + REQUIRED_PROMPT_FILES
    + REQUIRED_SCRIPT_FILES
    + REQUIRED_AI103_EXAMPLE_FILES
    + REQUIRED_INTERVIEW_EXAMPLE_FILES
    + REQUIRED_GITHUB_TEMPLATES
)

YAML_FILES = [
    "state/STUDY_STATE.yaml",
    "state/SKILL_MAP.yaml",
    "EXAMPLES/ai-103-example/state/STUDY_STATE.yaml",
    "EXAMPLES/ai-103-example/state/SKILL_MAP.yaml",
    "EXAMPLES/ai-103-example/targets/ai-103/TARGET.yaml",
]

REQUIRED_STUDY_STATE_KEYS = [
    "learner",
    "active_target_id",
    "targets",
    "study_target",
    "skills",
    "active_focus",
    "review",
    "sources",
    "session_history",
    "workflow",
    "rules",
    "metadata",
]

REQUIRED_SKILL_MAP_KEYS = [
    "skills",
    "metadata",
]

# Constructed from parts so the literal forbidden string does not appear in source.
FORBIDDEN_BRAND_RE = re.compile("Skill" + "Signal", re.IGNORECASE)


def check_files() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")
    return errors


def check_target_folders() -> list[str]:
    errors: list[str] = []
    targets_dir = ROOT / "targets"
    if not targets_dir.is_dir():
        errors.append("Missing required directory: targets")
        return errors

    for child in sorted(targets_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not (child / "TARGET.yaml").is_file():
            errors.append(f"Target folder missing TARGET.yaml: targets/{child.name}")
    return errors


def check_yaml() -> list[str]:
    errors: list[str] = []
    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Note: PyYAML not installed. Skipping YAML parse checks.")
        print("      Install with: pip install pyyaml")
        return errors

    for rel in YAML_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"Missing YAML file: {rel}")
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:  # pragma: no cover
            errors.append(f"YAML parse error in {rel}: {exc}")
            continue

        if data is None:
            errors.append(f"YAML file is empty or invalid: {rel}")
            continue

        if rel.endswith("STUDY_STATE.yaml"):
            for key in REQUIRED_STUDY_STATE_KEYS:
                if key not in data:
                    errors.append(f"Missing key '{key}' in {rel}")
        elif rel.endswith("SKILL_MAP.yaml"):
            for key in REQUIRED_SKILL_MAP_KEYS:
                if key not in data:
                    errors.append(f"Missing key '{key}' in {rel}")

    return errors


def check_no_forbidden_brand() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_dir():
            if path.name in {".git", ".venv", "node_modules", "__pycache__"}:
                continue
            continue
        # Skip the enforcement script itself and other agent scripts.
        try:
            if path.relative_to(ROOT).parts[0] == "scripts":
                continue
        except (ValueError, IndexError):
            pass
        if path.suffix not in {".md", ".yaml", ".yml", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if FORBIDDEN_BRAND_RE.search(text):
            rel = path.relative_to(ROOT)
            errors.append(f"Forbidden external brand mention in {rel}")
    return errors


def check_active_target(yaml: object) -> list[str]:
    errors: list[str] = []
    if yaml is None:
        return errors

    study_state_path = ROOT / "state/STUDY_STATE.yaml"
    try:
        data = yaml.safe_load(study_state_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not read state/STUDY_STATE.yaml for active target check: {exc}")
        return errors

    active_target_id = data.get("active_target_id")
    if not active_target_id:
        # Public template is allowed to have no active target.
        return errors

    target_dir = ROOT / "targets" / active_target_id
    target_yaml = target_dir / "TARGET.yaml"
    if not target_yaml.is_file():
        errors.append(
            f"Active target '{active_target_id}' missing TARGET.yaml at targets/{active_target_id}/TARGET.yaml"
        )

    return errors


def check_next_actions() -> list[str]:
    errors: list[str] = []
    next_actions_path = ROOT / "NEXT_ACTIONS.md"
    if not next_actions_path.is_file():
        errors.append("Missing NEXT_ACTIONS.md")
        return errors

    text = next_actions_path.read_text(encoding="utf-8")
    if "## Current next action" not in text:
        errors.append("NEXT_ACTIONS.md missing '## Current next action' section")
    return errors


def check_review_queue() -> list[str]:
    errors: list[str] = []
    queue_path = ROOT / "reviews/REVIEW_QUEUE.md"
    if not queue_path.is_file():
        errors.append("Missing reviews/REVIEW_QUEUE.md")
        return errors

    text = queue_path.read_text(encoding="utf-8")
    for section in ("## Due now", "## Scheduled", "## Review item format"):
        if section not in text:
            errors.append(f"reviews/REVIEW_QUEUE.md missing section '{section}'")
    return errors


def check_session_log() -> list[str]:
    errors: list[str] = []
    log_path = ROOT / "sessions/SESSION_LOG.md"
    if not log_path.is_file():
        errors.append("Missing sessions/SESSION_LOG.md")
        return errors

    text = log_path.read_text(encoding="utf-8")
    if "## Format" not in text and "## Sessions" not in text:
        errors.append("sessions/SESSION_LOG.md missing expected structure")
    return errors


def check_readiness_and_evidence(yaml: object) -> list[str]:
    errors: list[str] = []
    if yaml is None:
        return errors

    skill_map_path = ROOT / "state/SKILL_MAP.yaml"
    try:
        data = yaml.safe_load(skill_map_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not read state/SKILL_MAP.yaml for readiness check: {exc}")
        return errors

    skills = data.get("skills") or []
    for skill in skills:
        sid = skill.get("id", "<unknown>")
        readiness = skill.get("readiness")
        status = skill.get("status")
        evidence = skill.get("evidence") or []

        if readiness is not None:
            try:
                readiness_val = int(readiness)
            except (TypeError, ValueError):
                errors.append(
                    f"Skill '{sid}' has non-integer readiness value: {readiness}"
                )
                continue
            if not 0 <= readiness_val <= 100:
                errors.append(
                    f"Skill '{sid}' readiness out of range (0-100): {readiness_val}"
                )

        if status in ("practiced", "confirmed") and not evidence:
            errors.append(
                f"Skill '{sid}' status '{status}' has no evidence references"
            )

        if readiness is not None:
            try:
                if int(readiness) >= 70 and not evidence:
                    errors.append(
                        f"Skill '{sid}' readiness {readiness} has no evidence references"
                    )
            except (TypeError, ValueError):
                pass

    return errors


def check_active_target_source(yaml: object) -> list[str]:
    errors: list[str] = []
    if yaml is None:
        return errors

    study_state_path = ROOT / "state/STUDY_STATE.yaml"
    source_index_path = ROOT / "sources/SOURCE_INDEX.md"

    try:
        data = yaml.safe_load(study_state_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        errors.append(f"Could not read state/STUDY_STATE.yaml for source check: {exc}")
        return errors

    active_target_id = data.get("active_target_id")
    if not active_target_id:
        return errors

    target_yaml_path = ROOT / "targets" / active_target_id / "TARGET.yaml"
    try:
        target_data = yaml.safe_load(target_yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        # Missing target file is reported by check_active_target.
        return errors

    target_type = target_data.get("type", "").lower()
    if target_type != "certification":
        return errors

    if not source_index_path.is_file():
        errors.append("Active certification target requires sources/SOURCE_INDEX.md")
        return errors

    text = source_index_path.read_text(encoding="utf-8")
    has_official = bool(re.search(r"\*\*Type:\*\*\s*official", text, re.IGNORECASE))
    has_high = bool(re.search(r"\*\*Authority:\*\*\s*high", text, re.IGNORECASE))
    if not (has_official or has_high):
        errors.append(
            f"Active certification target '{active_target_id}' requires at least one official or high-authority source in sources/SOURCE_INDEX.md"
        )

    return errors


def check_source_freshness() -> list[str]:
    errors: list[str] = []
    source_index_path = ROOT / "sources/SOURCE_INDEX.md"
    if not source_index_path.is_file():
        return errors

    text = source_index_path.read_text(encoding="utf-8")
    entries = re.split(r"\n- \*\*Source ID:\*\*", text)
    for entry in entries[1:]:
        if "**Type:**" not in entry:
            continue
        source_id_match = re.search(r"^\s*(\S+)", entry)
        source_id = source_id_match.group(1) if source_id_match else "<unknown>"
        if "**Last checked:**" not in entry:
            errors.append(
                f"Source '{source_id}' in sources/SOURCE_INDEX.md missing 'Last checked'"
            )

    return errors


def check_state_target_consistency(yaml: object) -> list[str]:
    errors: list[str] = []
    if yaml is None:
        return errors

    root_skill_path = ROOT / "state/SKILL_MAP.yaml"
    try:
        root_data = yaml.safe_load(root_skill_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return errors

    root_skills = {s.get("id"): s for s in (root_data.get("skills") or []) if s.get("id")}

    for target_dir in (ROOT / "targets").iterdir():
        if not target_dir.is_dir() or target_dir.name.startswith("."):
            continue
        target_state_path = target_dir / "state/SKILL_MAP.yaml"
        if not target_state_path.is_file():
            continue
        try:
            target_data = yaml.safe_load(target_state_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            errors.append(
                f"Could not parse {target_state_path.relative_to(ROOT)}: {exc}"
            )
            continue

        target_skills = {s.get("id"): s for s in (target_data.get("skills") or []) if s.get("id")}
        for sid in set(root_skills) & set(target_skills):
            root_status = root_skills[sid].get("status")
            target_status = target_skills[sid].get("status")
            root_readiness = root_skills[sid].get("readiness")
            target_readiness = target_skills[sid].get("readiness")
            if root_status and target_status and root_status != target_status:
                errors.append(
                    f"Skill '{sid}' status differs between root ({root_status}) and target/{target_dir.name} ({target_status})"
                )
            if root_readiness is not None and target_readiness is not None:
                try:
                    if int(root_readiness) != int(target_readiness):
                        errors.append(
                            f"Skill '{sid}' readiness differs between root ({root_readiness}) and target/{target_dir.name} ({target_readiness})"
                        )
                except (TypeError, ValueError):
                    pass

    return errors


def main() -> int:
    print("StudyDD validation")
    print("==================")

    errors = check_files()
    errors.extend(check_target_folders())
    errors.extend(check_yaml())
    errors.extend(check_no_forbidden_brand())
    errors.extend(check_next_actions())
    errors.extend(check_review_queue())
    errors.extend(check_session_log())

    try:
        import yaml
    except ImportError:  # pragma: no cover
        yaml = None

    if yaml is not None:
        errors.extend(check_active_target(yaml))
        errors.extend(check_readiness_and_evidence(yaml))
        errors.extend(check_active_target_source(yaml))
        errors.extend(check_source_freshness())
        errors.extend(check_state_target_consistency(yaml))
    else:
        print("\nNote: PyYAML not installed. Skipping state-aware checks.")
        print("      Install with: pip install pyyaml")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  - {err}")
        print("\nValidation failed.")
        return 1

    print("\nAll required files present.")
    print("YAML validation passed.")
    print("No forbidden mentions found.")
    print("StudyDD state looks healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
