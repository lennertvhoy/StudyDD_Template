#!/usr/bin/env python3
"""Generate deterministic StudyDD compatibility views.

The canonical lifecycle inputs are ``instance.yaml`` and
``.statedd/lock.yaml``. Existing StudyDD tools still consume the three files
under ``state/``; this script keeps those paths as generated, read-compatible
views.

Composition is deliberately narrow. The manifest base and overlay accept only
known top-level and file-entry keys, and each entry is composed by explicit
field assignment. This module never performs a generic recursive YAML merge.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - repository requirements provide it.
    yaml = None  # type: ignore[assignment]


SCRIPT_PATH = "scripts/generate_compatibility_views.py"
INSTANCE_PATH = Path("instance.yaml")
LOCK_PATH = Path(".statedd/lock.yaml")
MODE_VIEW = Path("state/STUDYDD_MODE.yaml")
VERSION_VIEW = Path("state/STUDYDD_TEMPLATE_VERSION.yaml")
MANIFEST_VIEW = Path("state/STATE_MANIFEST.yaml")
MANIFEST_BASE = Path("state/STATE_MANIFEST.template.yaml")
MANIFEST_OVERLAY = Path("state/STATE_MANIFEST.instance.yaml")

MANIFEST_TOP_LEVEL_KEYS = {"manifest_version", "last_updated", "files"}
MANIFEST_ENTRY_KEYS = {
    "role",
    "load_default",
    "protected",
    "indexed_by",
    "summarized_by",
    "generated_by",
    "gitignore",
    "owner",
    "boundary",
}
MANIFEST_BOUNDARIES = {"template", "instance", "generated"}
MANIFEST_OWNERS = MANIFEST_BOUNDARIES


class CompatibilityViewError(ValueError):
    """Raised when a canonical input is malformed or ambiguous."""


def _require_yaml() -> Any:
    if yaml is None:
        raise CompatibilityViewError("PyYAML is required to generate compatibility views")
    return yaml


def _load_mapping(path: Path) -> dict[str, Any]:
    parser = _require_yaml()
    try:
        value = parser.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, parser.YAMLError) as exc:
        raise CompatibilityViewError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompatibilityViewError(f"{path} must contain a YAML mapping")
    return value


def _required_mapping(parent: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise CompatibilityViewError(f"{path}: {key!r} must be a mapping")
    return value


def _required_string(parent: dict[str, Any], key: str, path: Path) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CompatibilityViewError(f"{path}: {key!r} must be a non-empty string")
    return value


def _optional_string(parent: dict[str, Any], key: str, path: Path) -> str:
    value = parent.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise CompatibilityViewError(f"{path}: {key!r} must be a string when present")
    return value


def _descriptor_view(data: dict[str, Any], path: Path) -> dict[str, Any]:
    spec = _required_mapping(data, "spec", path)
    mode = _required_string(spec, "mode", path)
    if mode not in {"template", "bootstrap", "learner_instance"}:
        raise CompatibilityViewError(f"{path}: unsupported mode {mode!r}")
    origin = spec.get("templateOrigin", spec.get("templateRemote", ""))
    if not isinstance(origin, str):
        raise CompatibilityViewError(f"{path}: templateOrigin must be a string")
    personalized = spec.get("personalized")
    public_safe = spec.get("publicSafe")
    if not isinstance(personalized, bool) or not isinstance(public_safe, bool):
        raise CompatibilityViewError(
            f"{path}: personalized and publicSafe must be booleans"
        )

    view: dict[str, Any] = {
        "mode": mode,
        "template_remote": origin,
        "personalized": personalized,
        "public_safe": public_safe,
    }
    modules = spec.get("modules")
    if modules is not None:
        if not isinstance(modules, list) or not all(isinstance(item, str) for item in modules):
            raise CompatibilityViewError(f"{path}: modules must be a list of strings")
        # This is a declared compatibility field, not a merge target.
        view["modules"] = copy.deepcopy(modules)
    return view


def _lock_view(data: dict[str, Any], path: Path) -> dict[str, Any]:
    template = _required_mapping(data, "template", path)
    instance = data.get("instance", {})
    if not isinstance(instance, dict):
        raise CompatibilityViewError(f"{path}: instance must be a mapping")
    version = _required_string(template, "version", path)
    source_revision = _optional_string(template, "sourceRevision", path)
    source_path = _optional_string(template, "sourcePath", path)

    def instance_value(key: str) -> str:
        return _optional_string(instance, key, path)

    history = instance.get("upgradeHistory", [])
    if not isinstance(history, list):
        raise CompatibilityViewError(f"{path}: upgradeHistory must be a list")

    return {
        "template_version": version,
        "template_commit": _optional_string(template, "sourceCommit", path) or source_revision,
        "template_source_path": source_path,
        "instance_created_from_template_version": instance_value(
            "createdFromTemplateVersion"
        ),
        "instance_created_from_template_commit": instance_value(
            "createdFromTemplateCommit"
        ),
        "last_template_upgrade_version": instance_value("lastTemplateUpgradeVersion"),
        "last_template_upgrade_commit": instance_value("lastTemplateUpgradeCommit"),
        "upgrade_history": copy.deepcopy(history),
    }


def _validate_manifest_entry(path: str, entry: Any, *, source: Path) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise CompatibilityViewError(f"{source}: files[{path!r}] must be a mapping")
    unknown = set(entry) - MANIFEST_ENTRY_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise CompatibilityViewError(f"{source}: files[{path!r}] has unknown key(s): {names}")
    result = copy.deepcopy(entry)
    for field in ("owner", "boundary"):
        if field in result and result[field] not in MANIFEST_OWNERS:
            raise CompatibilityViewError(
                f"{source}: files[{path!r}].{field} has unsupported value {result[field]!r}"
            )
    return result


def compose_manifest(base: dict[str, Any], overlay: dict[str, Any], *, base_path: Path, overlay_path: Path) -> dict[str, Any]:
    """Compose the manifest using named fields only.

    The only supported composition is the manifest's scalar metadata plus a
    shallow, explicit merge of known file-entry fields. Nested values are not
    recursively merged.
    """
    unknown_base = set(base) - MANIFEST_TOP_LEVEL_KEYS
    unknown_overlay = set(overlay) - {"files"}
    if unknown_base:
        raise CompatibilityViewError(
            f"{base_path}: unknown top-level key(s): {', '.join(sorted(unknown_base))}"
        )
    if unknown_overlay:
        raise CompatibilityViewError(
            f"{overlay_path}: unknown top-level key(s): {', '.join(sorted(unknown_overlay))}"
        )
    base_files = base.get("files")
    overlay_files = overlay.get("files", {})
    if not isinstance(base_files, dict) or not isinstance(overlay_files, dict):
        raise CompatibilityViewError("manifest base and overlay files must be mappings")

    result: dict[str, Any] = {}
    for key in ("manifest_version", "last_updated"):
        if key in base:
            result[key] = copy.deepcopy(base[key])
    result["generated_by"] = SCRIPT_PATH
    result["files"] = {}

    for path in base_files:
        result["files"][path] = _validate_manifest_entry(
            path, base_files[path], source=base_path
        )
    for path in sorted(overlay_files):
        overlay_entry = _validate_manifest_entry(
            path, overlay_files[path], source=overlay_path
        )
        if path in result["files"]:
            entry = result["files"][path]
            for field in MANIFEST_ENTRY_KEYS:
                if field in overlay_entry:
                    entry[field] = overlay_entry[field]
        else:
            required = {"role", "owner", "boundary"}
            missing = required - set(overlay_entry)
            if missing:
                raise CompatibilityViewError(
                    f"{overlay_path}: new files[{path!r}] missing key(s): {', '.join(sorted(missing))}"
                )
            result["files"][path] = overlay_entry

    return result


def _dump(value: dict[str, Any], *, header: str) -> str:
    parser = _require_yaml()
    return header + parser.safe_dump(value, sort_keys=False, allow_unicode=False)


def render_views(root: Path) -> dict[Path, str]:
    descriptor_path = root / INSTANCE_PATH
    lock_path = root / LOCK_PATH
    base_path = root / MANIFEST_BASE
    overlay_path = root / MANIFEST_OVERLAY
    mode = _descriptor_view(_load_mapping(descriptor_path), INSTANCE_PATH)
    version = _lock_view(_load_mapping(lock_path), LOCK_PATH)
    manifest = compose_manifest(
        _load_mapping(base_path),
        _load_mapping(overlay_path),
        base_path=MANIFEST_BASE,
        overlay_path=MANIFEST_OVERLAY,
    )
    return {
        MODE_VIEW: _dump(
            mode,
            header=(
                "# GENERATED FILE — edit instance.yaml and regenerate.\n"
                f"# Generator: {SCRIPT_PATH}\n"
                "# Authority: instance.yaml\n"
            ),
        ),
        VERSION_VIEW: _dump(
            version,
            header=(
                "# GENERATED FILE — edit .statedd/lock.yaml and regenerate.\n"
                f"# Generator: {SCRIPT_PATH}\n"
                "# Authority: .statedd/lock.yaml\n"
            ),
        ),
        MANIFEST_VIEW: _dump(
            manifest,
            header=(
                "# GENERATED FILE — edit the template base or instance overlay and regenerate.\n"
                f"# Generator: {SCRIPT_PATH}\n"
                "# Authorities: state/STATE_MANIFEST.template.yaml + "
                "state/STATE_MANIFEST.instance.yaml\n"
            ),
        ),
    }


def write_views(root: Path, *, check: bool = False) -> list[Path]:
    rendered = render_views(root)
    changed: list[Path] = []
    for relative, content in rendered.items():
        target = root / relative
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current != content:
            changed.append(relative)
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="fail if a view is stale")
    args = parser.parse_args(argv)
    try:
        changed = write_views(args.root.resolve(), check=args.check)
    except (CompatibilityViewError, OSError) as exc:
        print(f"Compatibility view generation failed: {exc}", file=sys.stderr)
        return 1
    if args.check and changed:
        print("Stale compatibility view(s): " + ", ".join(path.as_posix() for path in changed))
        return 1
    if changed:
        action = "would update" if args.check else "updated"
        print(f"{action} compatibility view(s): " + ", ".join(path.as_posix() for path in changed))
    else:
        print("Compatibility views are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
