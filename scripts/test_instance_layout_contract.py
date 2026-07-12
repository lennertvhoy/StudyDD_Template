#!/usr/bin/env python3
"""Focused regression tests for the public StudyDD instance-layout contract."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from scripts.check_studydd import (
    INSTANCE_LAYOUT_CONTRACT,
    _validate_instance_layout_contract,
    check_instance_layout_contract,
)


def main() -> int:
    path = ROOT / INSTANCE_LAYOUT_CONTRACT
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert not check_instance_layout_contract(yaml), "repository contract hook must pass"
    assert contract["contract_id"] == "studydd.instance-layout/v1"
    assert set(contract["modes"]) == {"template", "bootstrap", "learner_instance"}
    assert contract["validation"]["entry_point"] == "scripts/check_studydd.py"
    assert contract["modes"]["learner_instance"]["lock"]["path"] == ".statedd/lock.yaml"

    surface_ids = {surface["id"] for surface in contract["authority_surfaces"]}
    assert {"template_assets", "instance_state", "generated_views"} <= surface_ids
    assert {tree["id"] for tree in contract["dynamic_instance_trees"]} >= {"targets", "reviews", "sessions", "sources"}
    assert all(view["generator"] for view in contract["generated_views"])

    malformed = copy.deepcopy(contract)
    malformed["contract_id"] = "studydd.instance-layout/v0"
    assert _validate_instance_layout_contract(malformed)

    malformed = copy.deepcopy(contract)
    malformed["modes"]["template"]["lock"]["path"] = "state/LOCK.yaml"
    assert _validate_instance_layout_contract(malformed)

    malformed = copy.deepcopy(contract)
    malformed["validation"]["entry_point"] = "scripts/other_validator.py"
    assert _validate_instance_layout_contract(malformed)

    print("StudyDD instance-layout contract tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
