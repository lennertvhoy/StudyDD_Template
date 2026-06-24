#!/usr/bin/env python3
"""Tiny StudyDD state validator.

Supports the agent workflow by checking that required files exist,
YAML parses, and required keys are present.

If PyYAML is not installed, YAML parsing is skipped and a note is printed.
Install PyYAML for full validation:
    pip install pyyaml
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ROOT_FILES = [
    "README.md",
    "AGENTS.md",
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
    "state/NEXT_STUDY_ACTIONS.md",
    "state/STUDY_BACKLOG.md",
    "state/SESSION_LOG.md",
    "state/EVIDENCE_LOG.md",
    "state/SKILL_MAP.yaml",
]

REQUIRED_PROTOCOL_FILES = [
    "protocols/TUTOR_PROTOCOL.md",
    "protocols/SESSION_TEMPLATE.md",
]

REQUIRED_PROMPT_FILES = [
    "PROMPTS/coding_agent_start_prompt.md",
    "PROMPTS/ai_tutor_prompt.md",
    "PROMPTS/study_session_prompt.md",
    "PROMPTS/exam_drill_prompt.md",
    "PROMPTS/reflection_prompt.md",
    "PROMPTS/update_state_prompt.md",
    "PROMPTS/interview_prep_prompt.md",
]

REQUIRED_AI103_EXAMPLE_FILES = [
    "EXAMPLES/ai-103-example/state/STUDY_STATUS.md",
    "EXAMPLES/ai-103-example/state/STUDY_STATE.yaml",
    "EXAMPLES/ai-103-example/state/NEXT_STUDY_ACTIONS.md",
    "EXAMPLES/ai-103-example/state/SKILL_MAP.yaml",
    "EXAMPLES/ai-103-example/state/SESSION_LOG_EXAMPLE.md",
]

REQUIRED_INTERVIEW_EXAMPLE_FILES = [
    "EXAMPLES/product-engineer-interview-example/state/STUDY_STATUS.md",
    "EXAMPLES/product-engineer-interview-example/state/STUDY_STATE.yaml",
    "EXAMPLES/product-engineer-interview-example/state/NEXT_STUDY_ACTIONS.md",
    "EXAMPLES/product-engineer-interview-example/state/SKILL_MAP.yaml",
    "EXAMPLES/product-engineer-interview-example/state/SESSION_LOG_EXAMPLE.md",
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
    + REQUIRED_PROTOCOL_FILES
    + REQUIRED_PROMPT_FILES
    + REQUIRED_AI103_EXAMPLE_FILES
    + REQUIRED_INTERVIEW_EXAMPLE_FILES
    + REQUIRED_GITHUB_TEMPLATES
)

YAML_FILES = [
    "state/STUDY_STATE.yaml",
    "state/SKILL_MAP.yaml",
    "EXAMPLES/ai-103-example/state/STUDY_STATE.yaml",
    "EXAMPLES/ai-103-example/state/SKILL_MAP.yaml",
    "EXAMPLES/product-engineer-interview-example/state/STUDY_STATE.yaml",
    "EXAMPLES/product-engineer-interview-example/state/SKILL_MAP.yaml",
]

REQUIRED_STUDY_STATE_KEYS = [
    "learner",
    "study_target",
    "skills",
    "active_focus",
    "session_history",
    "rules",
    "metadata",
]

REQUIRED_SKILL_MAP_KEYS = [
    "skills",
    "metadata",
]


def check_files() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")
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


def main() -> int:
    print("StudyDD validation")
    print("==================")

    errors = check_files()
    errors.extend(check_yaml())

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  - {err}")
        print("\nValidation failed.")
        return 1

    print("\nAll required files present.")
    print("YAML validation passed.")
    print("StudyDD state looks healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
