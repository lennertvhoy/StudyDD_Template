#!/usr/bin/env python3
"""Cross-file StudyDD consistency check.

Checks that skills duplicated between the root state and target folders do not
have contradictory readiness or status values.

Run from the repo root or any subdirectory.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(rel: str) -> dict | None:
    try:
        import yaml
    except ImportError:
        print("PyYAML not installed. Install with: pip install pyyaml")
        return None
    try:
        return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"Could not parse {rel}: {exc}")
        return None


def skill_map(rel: str) -> dict[str, dict]:
    data = load_yaml(rel)
    if not data:
        return {}
    return {s.get("id"): s for s in (data.get("skills") or []) if s.get("id")}


def main() -> int:
    print("StudyDD Consistency Check")
    print("=========================")

    root_skills = skill_map("state/SKILL_MAP.yaml")
    if root_skills is None:
        return 1

    errors: list[str] = []
    targets_dir = ROOT / "targets"
    if targets_dir.is_dir():
        for target_dir in targets_dir.iterdir():
            if not target_dir.is_dir() or target_dir.name.startswith("."):
                continue
            target_skill_path = target_dir / "state/SKILL_MAP.yaml"
            if not target_skill_path.is_file():
                continue
            target_skills = skill_map(str(target_skill_path.relative_to(ROOT)))
            if target_skills is None:
                continue

            for sid in set(root_skills) & set(target_skills):
                root = root_skills[sid]
                target = target_skills[sid]
                if root.get("status") != target.get("status"):
                    errors.append(
                        f"Skill '{sid}' status mismatch: root={root.get('status')} "
                        f"target/{target_dir.name}={target.get('status')}"
                    )
                if root.get("readiness") != target.get("readiness"):
                    errors.append(
                        f"Skill '{sid}' readiness mismatch: root={root.get('readiness')} "
                        f"target/{target_dir.name}={target.get('readiness')}"
                    )

    if errors:
        print("\nInconsistencies found:")
        for err in errors:
            print(f"  - {err}")
        print("\nConsistency check failed.")
        return 1

    print("\nNo contradictions found between root and target skill maps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
