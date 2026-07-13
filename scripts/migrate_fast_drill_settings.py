#!/usr/bin/env python3
"""Normalize legacy Fast Drill settings into the learner profile boundary."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml


LEGACY_PATHS = (Path("state/FAST_DRILL_SETTINGS.yaml"), Path(".fast_drill/settings.yaml"))
CANONICAL_PATH = Path("state/LEARNER_PROFILE.yaml")


class FastDrillMigrationError(ValueError):
    """A settings migration cannot safely determine one value."""


def _read(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise FastDrillMigrationError(f"settings path is not a regular file: {path}")
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise FastDrillMigrationError(f"settings file must contain a mapping: {path}")
    return value


def _value(data: dict[str, Any], path: Path) -> bool | None:
    raw = data.get("fast_drill_mode")
    if raw is None and isinstance(data.get("learner_preferences"), dict):
        raw = data["learner_preferences"].get("fast_drill_mode")
    if raw is None:
        return None
    if not isinstance(raw, bool):
        raise FastDrillMigrationError(f"fast_drill_mode must be boolean: {path}")
    return raw


def normalize_fast_drill_settings(root: Path | str) -> dict[str, Any]:
    """Move one unambiguous legacy value into the canonical learner profile.

    Missing values are a deterministic no-op. Equal values from both legacy
    locations are accepted. Contradictory values fail before any write.
    """

    root = Path(root)
    canonical_path = root / CANONICAL_PATH
    canonical = _read(canonical_path) or {}
    canonical_value = _value(canonical, CANONICAL_PATH)
    values: list[tuple[str, bool]] = []
    for relative in LEGACY_PATHS:
        data = _read(root / relative)
        if data is not None:
            value = _value(data, relative)
            if value is not None:
                values.append((relative.as_posix(), value))
    distinct = {value for _, value in values}
    if len(distinct) > 1 or (canonical_value is not None and distinct and canonical_value not in distinct):
        raise FastDrillMigrationError("contradictory Fast Drill settings; explicit resolution is required")
    chosen = canonical_value if canonical_value is not None else (next(iter(distinct)) if distinct else None)
    if chosen is None:
        return {"status": "not_applicable", "changed": False, "value": None}
    if canonical_value == chosen:
        return {"status": "already_migrated", "changed": False, "value": chosen}
    canonical.setdefault("learner_preferences", {})["fast_drill_mode"] = chosen
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".learner-profile-", dir=canonical_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.safe_dump(canonical, handle, sort_keys=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, canonical_path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return {"status": "migrated", "changed": True, "value": chosen}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(normalize_fast_drill_settings(args.root))
