#!/usr/bin/env python3
"""Typed Fast Drill settings migration proof."""

from __future__ import annotations

import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.migrate_fast_drill_settings import FastDrillMigrationError, normalize_fast_drill_settings


def _root() -> Path:
    root = Path(tempfile.mkdtemp(prefix="studydd-fast-drill-migration-"))
    (root / "state").mkdir()
    (root / ".fast_drill").mkdir()
    (root / "state/LEARNER_PROFILE.yaml").write_text("learner_preferences: {}\n", encoding="utf-8")
    return root


def test_first_legacy_location_migrates_and_rerun_is_idempotent() -> None:
    root = _root()
    (root / "state/FAST_DRILL_SETTINGS.yaml").write_text("fast_drill_mode: true\n", encoding="utf-8")
    assert normalize_fast_drill_settings(root)["status"] == "migrated"
    before = (root / "state/LEARNER_PROFILE.yaml").read_bytes()
    assert normalize_fast_drill_settings(root)["status"] == "already_migrated"
    assert (root / "state/LEARNER_PROFILE.yaml").read_bytes() == before


def test_second_legacy_location_and_equal_values_are_accepted() -> None:
    root = _root()
    for path in (root / "state/FAST_DRILL_SETTINGS.yaml", root / ".fast_drill/settings.yaml"):
        path.write_text("fast_drill_mode: false\n", encoding="utf-8")
    assert normalize_fast_drill_settings(root)["value"] is False


def test_contradictory_and_missing_values_fail_closed_or_noop() -> None:
    root = _root()
    assert normalize_fast_drill_settings(root)["status"] == "not_applicable"
    (root / "state/FAST_DRILL_SETTINGS.yaml").write_text("fast_drill_mode: true\n", encoding="utf-8")
    (root / ".fast_drill/settings.yaml").write_text("fast_drill_mode: false\n", encoding="utf-8")
    before = (root / "state/LEARNER_PROFILE.yaml").read_bytes()
    try:
        normalize_fast_drill_settings(root)
    except FastDrillMigrationError as exc:
        assert "contradictory" in str(exc)
    else:
        raise AssertionError("contradictory Fast Drill values were accepted")
    assert (root / "state/LEARNER_PROFILE.yaml").read_bytes() == before


if __name__ == "__main__":
    test_first_legacy_location_migrates_and_rerun_is_idempotent()
    test_second_legacy_location_and_equal_values_are_accepted()
    test_contradictory_and_missing_values_fail_closed_or_noop()
    print("Fast Drill settings migration tests passed.")
