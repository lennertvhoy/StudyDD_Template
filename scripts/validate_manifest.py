#!/usr/bin/env python3
"""Validate StudyDD's canonical StatePort lifecycle manifest.

This validator is deliberately narrow. It checks the declarative boundary
against the paths in origin/main; it does not resolve Git, fetch sources, or
execute module code.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - requirements.txt provides PyYAML
    yaml = None


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".statedd" / "manifest.yaml"
FORMAT = "statedd.template-manifest/v2"
LAYOUT_CONTRACT = "studydd.instance-layout/v1"
OWNERS = {"template", "instance", "generated"}
KINDS = {"file", "tree"}
PROVISION = {
    "copy_from_template",
    "create_if_missing",
    "generated_output",
    "composed_output",
    "append_only_state",
    "schema_migration_intent",
    "retire",
}
UPDATE = {
    "replace_if_unmodified",
    "preserve",
    "generated",
    "compose",
    "append_only",
    "schema_migrate",
    "retire",
}
SENSITIVITIES = {"public", "internal", "private", "secret"}
REQUIRED_ASSET_KEYS = {
    "id",
    "path",
    "kind",
    "owner",
    "role",
    "provisionPolicy",
    "updatePolicy",
    "required",
    "schema",
    "sensitivity",
    "selectingModules",
}


class ValidationError(ValueError):
    """A manifest boundary violation."""


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValidationError(f"{label} must be a safe relative path")
    return path.as_posix()


def _origin_paths(ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise ValidationError(f"cannot inspect canonical source ref {ref!r}: {result.stderr.strip()}")
    return {line for line in result.stdout.splitlines() if line}


def _covers(asset_path: str, candidate: str) -> bool:
    return candidate == asset_path or candidate.startswith(asset_path + "/")


def _validate_modules(data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[str]]:
    raw_modules = data.get("modules")
    if not isinstance(raw_modules, list) or not raw_modules:
        raise ValidationError("modules must be a non-empty list")
    modules: dict[str, dict[str, Any]] = {}
    for index, module in enumerate(raw_modules):
        if not isinstance(module, dict):
            raise ValidationError(f"modules[{index}] must be a mapping")
        module_id = module.get("id")
        if not isinstance(module_id, str) or not module_id:
            raise ValidationError(f"modules[{index}].id must be a non-empty string")
        if module_id in modules:
            raise ValidationError(f"duplicate module id: {module_id}")
        for key in ("dependencies", "conflicts", "capabilities", "assets"):
            value = module.get(key)
            if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
                raise ValidationError(f"modules[{index}].{key} must be a list of strings")
            if len(value) != len(set(value)):
                raise ValidationError(f"modules[{index}].{key} contains duplicates")
        tests = module.get("selfTests")
        if not isinstance(tests, list) or not tests:
            raise ValidationError(f"modules[{index}].selfTests must be non-empty")
        for test in tests:
            if not isinstance(test, dict) or not isinstance(test.get("id"), str) or not test["id"]:
                raise ValidationError(f"module {module_id!r} has an invalid self-test")
            command = test.get("command")
            if not isinstance(command, str) or not command.startswith("python3 "):
                raise ValidationError(f"module {module_id!r} self-tests must declare python3 commands")
            test_path = command.split()[1]
            if not (ROOT / test_path).is_file():
                raise ValidationError(f"module {module_id!r} self-test path is missing: {test_path}")
        modules[module_id] = module

    module_ids = set(modules)
    for module_id, module in modules.items():
        for relation in ("dependencies", "conflicts"):
            unknown = set(module[relation]) - module_ids
            if unknown:
                raise ValidationError(f"module {module_id!r} references unknown {relation}: {sorted(unknown)}")
    selected = data.get("selectedModules")
    if not isinstance(selected, list) or not selected or set(selected) - module_ids:
        raise ValidationError("selectedModules must list known modules")
    if len(selected) != len(set(selected)):
        raise ValidationError("selectedModules contains duplicates")
    return modules, set(selected)


def validate(data: dict[str, Any], origin_ref: str = "origin/main") -> list[str]:
    if data.get("formatVersion") != FORMAT:
        raise ValidationError(f"formatVersion must be {FORMAT!r}")
    if data.get("instanceLayoutContract") != LAYOUT_CONTRACT:
        raise ValidationError(f"instanceLayoutContract must be {LAYOUT_CONTRACT!r}")
    template = data.get("template")
    if not isinstance(template, dict):
        raise ValidationError("template must be a mapping")
    if template.get("id") != "studydd":
        raise ValidationError("template.id must be 'studydd'")
    if template.get("releaseVersion") != "0.10.0":
        raise ValidationError("releaseVersion must match origin/main's 0.10.0 template version")
    source = data.get("source")
    if not isinstance(source, dict) or source.get("class") != "canonical_source":
        raise ValidationError("source must identify a canonical_source")
    if source.get("productionEligible") is not True:
        raise ValidationError("canonical StudyDD source must be production eligible")
    if source.get("repository") != "https://github.com/lennertvhoy/StudyDD_Template.git":
        raise ValidationError("source.repository must be the canonical StudyDD template remote")
    if source.get("requestedRef") != "main" or source.get("resolvedCommit") is not None:
        raise ValidationError("manifest may request main but may not invent immutable commit metadata")
    modules, selected = _validate_modules(data)
    for module_id in selected:
        pending = list(modules[module_id]["dependencies"])
        seen: set[str] = set()
        while pending:
            dependency = pending.pop()
            if dependency in seen:
                continue
            seen.add(dependency)
            if dependency not in selected:
                raise ValidationError(f"selected module {module_id!r} omits dependency {dependency!r}")
            pending.extend(modules[dependency]["dependencies"])

    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValidationError("assets must be a non-empty list")
    asset_ids: set[str] = set()
    declared_paths: list[tuple[str, str]] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValidationError(f"assets[{index}] must be a mapping")
        missing = REQUIRED_ASSET_KEYS - set(asset)
        if missing:
            raise ValidationError(f"assets[{index}] is missing keys: {sorted(missing)}")
        asset_id = asset["id"]
        if not isinstance(asset_id, str) or not asset_id or asset_id in asset_ids:
            raise ValidationError(f"assets[{index}] has a duplicate or invalid id")
        asset_ids.add(asset_id)
        path = _relative_path(asset["path"], f"assets[{index}].path")
        kind = asset["kind"]
        if kind not in KINDS or asset["owner"] not in OWNERS:
            raise ValidationError(f"assets[{index}] has an invalid kind or owner")
        if asset["provisionPolicy"] not in PROVISION or asset["updatePolicy"] not in UPDATE:
            raise ValidationError(f"assets[{index}] has an invalid lifecycle policy")
        if not isinstance(asset["required"], bool) or asset["sensitivity"] not in SENSITIVITIES:
            raise ValidationError(f"assets[{index}] has invalid required/sensitivity fields")
        selectors = asset["selectingModules"]
        if not isinstance(selectors, list) or not selectors or set(selectors) - set(modules):
            raise ValidationError(f"assets[{index}].selectingModules is invalid")
        if asset["provisionPolicy"] == "copy_from_template":
            source_path = _relative_path(asset.get("source"), f"assets[{index}].source")
            if not (ROOT / source_path).is_file():
                raise ValidationError(f"copy source is missing: {source_path}")
        elif asset.get("source") is not None:
            raise ValidationError(f"assets[{index}].source is only valid for copy_from_template")
        if asset["provisionPolicy"] == "generated_output" and not isinstance(asset.get("generator"), str):
            raise ValidationError(f"generated asset {asset_id!r} must name a generator")
        if kind == "file" and any(path == prior for prior, _ in declared_paths):
            raise ValidationError(f"duplicate exact asset path: {path}")
        declared_paths.append((path, kind))

    for module_id, module in modules.items():
        unknown_assets = set(module["assets"]) - asset_ids
        if unknown_assets:
            raise ValidationError(f"module {module_id!r} references unknown assets: {sorted(unknown_assets)}")
        for asset_id in module["assets"]:
            asset = next(item for item in assets if item["id"] == asset_id)
            if module_id not in asset["selectingModules"]:
                raise ValidationError(f"asset {asset_id!r} omits reciprocal module {module_id!r}")

    origin_paths = _origin_paths(origin_ref)
    uncovered = sorted(
        path for path in origin_paths if not any(_covers(asset_path, path) for asset_path, _ in declared_paths)
    )
    if uncovered:
        raise ValidationError(f"origin/main paths are not classified: {uncovered}")
    for path, kind in declared_paths:
        if kind == "file" and path in origin_paths and not (ROOT / path).is_file():
            raise ValidationError(f"manifest file asset is missing from checkout: {path}")

    deferred = {"studydd.fast-drill", "studydd.question-bank-engine", "studydd.integrations"}
    if selected.intersection(deferred):
        raise ValidationError("incomplete deferred StudyDD modules must not be selected")
    return [
        f"validated {len(origin_paths)} origin/main paths",
        f"validated {len(assets)} manifest assets",
        f"validated {len(selected)} selected modules",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin-ref", default="origin/main")
    args = parser.parse_args()
    if yaml is None:
        print("PyYAML is required; install requirements.txt first", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
        messages = validate(data, origin_ref=args.origin_ref)
    except (OSError, ValidationError, yaml.YAMLError) as exc:
        print(f"manifest validation failed: {exc}", file=sys.stderr)
        return 1
    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
