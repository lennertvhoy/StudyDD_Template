#!/usr/bin/env python3
"""Generate deterministic StudyDD compatibility views.

The canonical lifecycle inputs are ``instance.yaml``, ``.statedd/lock.yaml``,
and the explicit StateDD manifest fragments.  The three files under
``state/`` remain generated, read-compatible views for existing StudyDD
consumers.

Rendering is pure and fully validated before any output is changed.  The
write phase stages every changed file first and then replaces the outputs as a
small transaction, preserving the instance-owned trees and files.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - repository requirements provide it.
    yaml = None  # type: ignore[assignment]


SCRIPT_PATH = "scripts/generate_compatibility_views.py"
SCHEMA_VERSION = "studydd.compatibility-view/v1"
VIEW_VERSION = 1
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

INSTANCE_PATH = Path("instance.yaml")
LOCK_PATH = Path(".statedd/lock.yaml")
MODE_VIEW = Path("state/STUDYDD_MODE.yaml")
VERSION_VIEW = Path("state/STUDYDD_TEMPLATE_VERSION.yaml")
MANIFEST_VIEW = Path("state/STATE_MANIFEST.yaml")
MANIFEST_BASE = Path("state/STATE_MANIFEST.template.yaml")
MANIFEST_OVERLAY = Path("state/STATE_MANIFEST.instance.yaml")
VIEW_PATHS = (MODE_VIEW, VERSION_VIEW, MANIFEST_VIEW)

MANIFEST_TOP_LEVEL_KEYS = {"manifest_version", "last_updated", "files", "extensions"}
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
MANIFEST_ENTRY_ORDER = (
    "role",
    "load_default",
    "protected",
    "indexed_by",
    "summarized_by",
    "generated_by",
    "gitignore",
    "owner",
    "boundary",
)

_HEADER_SCHEMA = "# Schema: "
_HEADER_SOURCE = "# Source digest: "
_HEADER_VIEW = "# View digest: "


class CompatibilityViewError(ValueError):
    """Raised when a canonical input is malformed, ambiguous, or unsafe."""


def _require_yaml() -> Any:
    if yaml is None:
        raise CompatibilityViewError("PyYAML is required to generate compatibility views")
    return yaml


def _load_mapping(path: Path) -> dict[str, Any]:
    parser = _require_yaml()
    try:
        value = parser.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, parser.YAMLError) as exc:
        raise CompatibilityViewError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompatibilityViewError(f"{path} must contain a YAML mapping")
    if any(not isinstance(key, str) for key in value):
        raise CompatibilityViewError(f"{path} must use string mapping keys")
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


def _stable_value(value: Any, *, source: Path, label: str) -> Any:
    """Return a recursively key-sorted copy while preserving list order."""
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise CompatibilityViewError(f"{source}: {label} must use string keys")
        return {
            key: _stable_value(value[key], source=source, label=f"{label}.{key}")
            for key in sorted(value)
        }
    if isinstance(value, list):
        return [
            _stable_value(item, source=source, label=f"{label}[{index}]")
            for index, item in enumerate(value)
        ]
    return copy.deepcopy(value)


def _portable_path(value: str, *, root: Path, label: str) -> str:
    """Normalize a path without allowing host-specific absolute paths out."""
    normalized = value.replace("\\", "/")
    if not normalized:
        return ""
    # URLs and other URI-like origins are identifiers, not filesystem paths.
    if "://" in normalized:
        return normalized
    if re.match(r"^[A-Za-z]:/", normalized) or normalized.startswith("/"):
        candidate = Path(normalized)
        try:
            return candidate.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            # An external checkout location is not portable.  The lock's
            # source digest and commit remain the portable identity.
            return ""
    return normalized


def _safe_relative_path(value: Any, *, source: Path, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompatibilityViewError(f"{source}: {label} must be a non-empty relative path")
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
        raise CompatibilityViewError(f"{source}: {label} must be relative")
    parts = tuple(part for part in normalized.split("/") if part not in ("", "."))
    if not parts or ".." in parts or any("\x00" in part for part in parts):
        raise CompatibilityViewError(f"{source}: {label} is unsafe")
    # Path is retained for the explicit platform-independent spelling check;
    # the returned form never depends on the host separator.
    del path
    return "/".join(parts)


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _digest_value(value: Any, *, root: Path, key: str = "") -> Any:
    """Normalize path-bearing source fields before hashing them."""
    path_keys = {"path", "sourcePath", "checkoutLocation", "template_source_path"}
    if isinstance(value, dict):
        return {
            name: _digest_value(value[name], root=root, key=name)
            for name in sorted(value)
        }
    if isinstance(value, list):
        return [_digest_value(item, root=root, key=key) for item in value]
    if isinstance(value, str) and key in path_keys:
        return _portable_path(value, root=root, label=key)
    return copy.deepcopy(value)


def _canonical_digest(values: list[tuple[str, Any]], *, source: Path, root: Path) -> str:
    """Hash normalized source values and names, independent of checkout path."""
    payload = [
        {
            "path": name,
            "value": _digest_value(_stable_value(value, source=source, label=name), root=root),
        }
        for name, value in sorted(values)
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def source_digest(root: Path) -> str:
    """Return the portable digest of all canonical compatibility inputs."""
    root = Path(root)
    inputs = [
        (INSTANCE_PATH.as_posix(), _load_mapping(root / INSTANCE_PATH)),
        (LOCK_PATH.as_posix(), _load_mapping(root / LOCK_PATH)),
        (MANIFEST_BASE.as_posix(), _load_mapping(root / MANIFEST_BASE)),
        (MANIFEST_OVERLAY.as_posix(), _load_mapping(root / MANIFEST_OVERLAY)),
    ]
    return _canonical_digest(inputs, source=Path("compatibility inputs"), root=root)


def _extensions(parent: dict[str, Any], *, path: Path, key: str) -> dict[str, Any]:
    value = parent.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise CompatibilityViewError(f"{path}: {key!r} must be a mapping when present")
    reserved = {"schema_version", "view_version", "source_digest", "generated_by", "files"}
    conflict = reserved.intersection(value)
    if conflict:
        raise CompatibilityViewError(
            f"{path}: {key!r} conflicts with generated field(s): {', '.join(sorted(conflict))}"
        )
    return _stable_value(value, source=path, label=key)


def _descriptor_view(data: dict[str, Any], path: Path) -> dict[str, Any]:
    spec = _required_mapping(data, "spec", path)
    mode = _required_string(spec, "mode", path)
    if mode not in {"template", "bootstrap", "learner_instance"}:
        raise CompatibilityViewError(f"{path}: unsupported mode {mode!r}")

    origins = []
    for key in ("templateOrigin", "templateRemote"):
        value = spec.get(key)
        if value is not None:
            if not isinstance(value, str):
                raise CompatibilityViewError(f"{path}: {key} must be a string")
            if value:
                origins.append((key, value))
    nested_template = spec.get("template")
    if nested_template is not None:
        if not isinstance(nested_template, dict):
            raise CompatibilityViewError(f"{path}: template must be a mapping")
        nested_origin = nested_template.get("origin")
        if nested_origin is not None:
            if not isinstance(nested_origin, str):
                raise CompatibilityViewError(f"{path}: template.origin must be a string")
            if nested_origin:
                origins.append(("template.origin", nested_origin))
    distinct_origins = {value for _, value in origins}
    if len(distinct_origins) > 1:
        raise CompatibilityViewError(f"{path}: conflicting template origin fields")
    origin = next(iter(distinct_origins), "")

    personalized = spec.get("personalized")
    public_safe = spec.get("publicSafe")
    if not isinstance(personalized, bool) or not isinstance(public_safe, bool):
        raise CompatibilityViewError(f"{path}: personalized and publicSafe must be booleans")

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
        view["modules"] = copy.deepcopy(modules)
    extensions = _extensions(spec, path=path, key="extensions")
    if extensions:
        view["extensions"] = extensions
    return view


def _lock_view(data: dict[str, Any], path: Path, *, root: Path) -> dict[str, Any]:
    template = _required_mapping(data, "template", path)
    instance = data.get("instance", {})
    if not isinstance(instance, dict):
        raise CompatibilityViewError(f"{path}: instance must be a mapping")
    version = _required_string(template, "version", path)
    release_status = _optional_string(template, "releaseStatus", path)
    source_revision = _optional_string(template, "sourceRevision", path)
    source_path = _optional_string(template, "sourcePath", path)
    source_commit = _optional_string(template, "sourceCommit", path)
    if source_commit and source_revision and source_commit == source_revision:
        # A commit and a digest are distinct identities. Equal values are
        # almost certainly a malformed lock and must not be guessed around.
        raise CompatibilityViewError(f"{path}: sourceCommit conflicts with sourceRevision")

    def instance_value(key: str) -> str:
        return _optional_string(instance, key, path)

    history = instance.get("upgradeHistory", [])
    if not isinstance(history, list):
        raise CompatibilityViewError(f"{path}: upgradeHistory must be a list")
    source_descriptor = template.get("source")
    if source_descriptor is not None and not isinstance(source_descriptor, dict):
        raise CompatibilityViewError(f"{path}: template.source must be a mapping")
    descriptor_digest = ""
    if isinstance(source_descriptor, dict):
        descriptor_digest = _optional_string(source_descriptor, "sourceDigest", path)
        if descriptor_digest and source_revision and descriptor_digest != source_revision:
            raise CompatibilityViewError(f"{path}: source digest conflicts with sourceRevision")

    created_version = instance_value("createdFromTemplateVersion")
    created_commit = instance_value("createdFromTemplateCommit")
    created_source = {
        "origin": _portable_path(source_path, root=root, label="sourcePath"),
        "version": created_version,
        "commit": created_commit,
        "digest": source_revision or descriptor_digest,
    }
    result = {
        "template_version": version,
        "template_commit": source_commit or source_revision,
        "template_source_digest": source_revision or descriptor_digest,
        "template_source_path": _portable_path(source_path, root=root, label="sourcePath"),
        "instance_created_from_template_version": created_version,
        "instance_created_from_template_commit": created_commit,
        "instance_created_from_template_source": created_source,
        "last_template_upgrade_version": instance_value("lastTemplateUpgradeVersion"),
        "last_template_upgrade_commit": instance_value("lastTemplateUpgradeCommit"),
        "upgrade_history": _stable_value(history, source=path, label="upgradeHistory"),
    }
    if release_status:
        result["release_status"] = release_status
    return result


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
    if "owner" in result and "boundary" in result and result["owner"] != result["boundary"]:
        raise CompatibilityViewError(f"{source}: files[{path!r}] owner/boundary conflict")
    return result


def _ordered_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(entry[key]) for key in MANIFEST_ENTRY_ORDER if key in entry}


def compose_manifest(
    base: dict[str, Any],
    overlay: dict[str, Any],
    *,
    base_path: Path,
    overlay_path: Path,
) -> dict[str, Any]:
    """Compose known manifest fields and preserve explicit instance extensions."""
    unknown_base = set(base) - MANIFEST_TOP_LEVEL_KEYS
    unknown_overlay = set(overlay) - {"files", "extensions"}
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

    all_files: dict[str, tuple[dict[str, Any], Path]] = {}
    for raw_path, raw_entry in base_files.items():
        path = _safe_relative_path(raw_path, source=base_path, label="file path")
        if path in all_files:
            raise CompatibilityViewError(f"{base_path}: duplicate normalized file path {path!r}")
        all_files[path] = (_validate_manifest_entry(path, raw_entry, source=base_path), base_path)
    normalized_overlay: dict[str, dict[str, Any]] = {}
    for raw_path, raw_entry in overlay_files.items():
        path = _safe_relative_path(raw_path, source=overlay_path, label="file path")
        if path in normalized_overlay:
            raise CompatibilityViewError(f"{overlay_path}: duplicate normalized file path {path!r}")
        normalized_overlay[path] = _validate_manifest_entry(path, raw_entry, source=overlay_path)

    for path in sorted(normalized_overlay):
        overlay_entry = normalized_overlay[path]
        if path in all_files:
            base_entry = all_files[path][0]
            for field, value in overlay_entry.items():
                if field in base_entry and base_entry[field] != value:
                    raise CompatibilityViewError(
                        f"{overlay_path}: conflicting override for files[{path!r}].{field}"
                    )
            merged = dict(base_entry)
            merged.update(overlay_entry)
            all_files[path] = (_ordered_entry(merged), overlay_path)
        else:
            required = {"role", "owner", "boundary"}
            missing = required - set(overlay_entry)
            if missing:
                raise CompatibilityViewError(
                    f"{overlay_path}: new files[{path!r}] missing key(s): {', '.join(sorted(missing))}"
                )
            all_files[path] = (_ordered_entry(overlay_entry), overlay_path)

    result["files"] = {path: _ordered_entry(all_files[path][0]) for path in sorted(all_files)}

    base_extensions = _extensions(base, path=base_path, key="extensions")
    overlay_extensions = _extensions(overlay, path=overlay_path, key="extensions")
    extensions = dict(base_extensions)
    for key in sorted(overlay_extensions):
        if key in extensions and extensions[key] != overlay_extensions[key]:
            raise CompatibilityViewError(f"{overlay_path}: conflicting extension {key!r}")
        extensions[key] = overlay_extensions[key]
    if extensions:
        result["extensions"] = {key: extensions[key] for key in sorted(extensions)}
    return result


def _dump_payload(value: dict[str, Any]) -> str:
    parser = _require_yaml()
    text = parser.safe_dump(
        value,
        sort_keys=False,
        allow_unicode=False,
        default_flow_style=False,
        width=4096,
    )
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


def _document(payload: dict[str, Any], *, authority: str) -> str:
    body = _dump_payload(payload)
    view_digest = _digest_bytes(body.encode("utf-8"))
    header = (
        "# GENERATED FILE — edit the declared authority and regenerate.\n"
        f"# Generator: {SCRIPT_PATH}\n"
        f"{_HEADER_SCHEMA}{SCHEMA_VERSION}\n"
        f"# View version: {VIEW_VERSION}\n"
        f"{_HEADER_SOURCE}{payload['source_digest']}\n"
        f"{_HEADER_VIEW}{view_digest}\n"
        f"# Authority: {authority}\n"
    )
    return header + body


def render_views(root: Path) -> dict[Path, str]:
    root = Path(root)
    descriptor = _load_mapping(root / INSTANCE_PATH)
    lock = _load_mapping(root / LOCK_PATH)
    base = _load_mapping(root / MANIFEST_BASE)
    overlay = _load_mapping(root / MANIFEST_OVERLAY)

    digest = source_digest(root)
    mode = _descriptor_view(descriptor, INSTANCE_PATH)
    mode = {"schema_version": SCHEMA_VERSION, "view_version": VIEW_VERSION, "source_digest": digest, **mode}
    version = _lock_view(lock, LOCK_PATH, root=root)
    version = {"schema_version": SCHEMA_VERSION, "view_version": VIEW_VERSION, "source_digest": digest, **version}
    manifest = compose_manifest(
        base,
        overlay,
        base_path=MANIFEST_BASE,
        overlay_path=MANIFEST_OVERLAY,
    )
    manifest = {"schema_version": SCHEMA_VERSION, "view_version": VIEW_VERSION, "source_digest": digest, **manifest}

    return {
        MODE_VIEW: _document(mode, authority="instance.yaml"),
        VERSION_VIEW: _document(version, authority=".statedd/lock.yaml"),
        MANIFEST_VIEW: _document(
            manifest,
            authority="state/STATE_MANIFEST.template.yaml + state/STATE_MANIFEST.instance.yaml",
        ),
    }


def _legacy_generated(current: str) -> bool:
    lines = current.splitlines()
    return (
        bool(lines)
        and lines[0].startswith("# GENERATED FILE")
        and any(line == f"# Generator: {SCRIPT_PATH}" for line in lines[:5])
        and not any(line.startswith(_HEADER_SCHEMA) for line in lines[:8])
    )


def _inspect_current(current: str, *, relative: Path) -> str:
    """Return ``missing``, ``unchanged``, or ``stale``; reject manual edits."""
    if not current:
        return "missing"
    lines = current.splitlines(keepends=True)
    if _legacy_generated(current):
        return "stale"
    if not lines or not lines[0].startswith("# GENERATED FILE"):
        raise CompatibilityViewError(f"{relative}: existing output is not a generated view")
    if len(lines) < 7 or lines[1].strip() != f"# Generator: {SCRIPT_PATH}":
        raise CompatibilityViewError(f"{relative}: generated header was manually edited")
    schema = next((line[len(_HEADER_SCHEMA):].strip() for line in lines if line.startswith(_HEADER_SCHEMA)), None)
    source = next((line[len(_HEADER_SOURCE):].strip() for line in lines if line.startswith(_HEADER_SOURCE)), None)
    view = next((line[len(_HEADER_VIEW):].strip() for line in lines if line.startswith(_HEADER_VIEW)), None)
    if schema != SCHEMA_VERSION or view is None or source is None:
        raise CompatibilityViewError(f"{relative}: unsupported or incomplete generated header")
    if not SHA256_RE.fullmatch(source) or not SHA256_RE.fullmatch(view):
        raise CompatibilityViewError(f"{relative}: generated digest is malformed")
    try:
        body_index = next(index for index, line in enumerate(lines) if line.startswith("# Authority: ")) + 1
    except StopIteration as exc:  # pragma: no cover - guarded above.
        raise CompatibilityViewError(f"{relative}: generated body is missing") from exc
    body = "".join(lines[body_index:])
    if _digest_bytes(body.encode("utf-8")) != view:
        raise CompatibilityViewError(f"{relative}: manual edit detected (view digest mismatch)")
    parsed = _require_yaml().safe_load(body)
    if not isinstance(parsed, dict) or parsed.get("schema_version") != SCHEMA_VERSION:
        raise CompatibilityViewError(f"{relative}: generated payload schema is invalid")
    if parsed.get("source_digest") != source:
        raise CompatibilityViewError(f"{relative}: header/payload source digest conflict")
    return "stale"


def _atomic_write(root: Path, rendered: dict[Path, str], changed: list[Path]) -> None:
    """Stage all bytes, then replace outputs with rollback on replacement failure."""
    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for relative in changed:
            target = root / relative
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise CompatibilityViewError(f"{relative}: output path is not a regular file")
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, raw_temp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
            staged[relative] = Path(raw_temp)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered[relative])
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists():
                os.chmod(staged[relative], target.stat().st_mode & 0o777)

        for relative in changed:
            target = root / relative
            temporary = staged[relative]
            if target.exists():
                fd, raw_backup = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".bak", dir=target.parent)
                os.close(fd)
                backup = Path(raw_backup)
                backup.unlink()
                backups[relative] = backup
                os.replace(target, backup)
            os.replace(temporary, target)
            replaced.append(relative)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
    except Exception:
        for relative in reversed(replaced):
            target = root / relative
            target.unlink(missing_ok=True)
            backup = backups.get(relative)
            if backup is not None and backup.exists():
                os.replace(backup, target)
        for relative, backup in backups.items():
            if relative not in replaced and backup.exists():
                os.replace(backup, root / relative)
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def write_views(root: Path, *, check: bool = False) -> list[Path]:
    rendered = render_views(Path(root))
    changed: list[Path] = []
    for relative in VIEW_PATHS:
        target = Path(root) / relative
        if target.is_symlink():
            raise CompatibilityViewError(f"{relative}: symlinked output is not safe")
        try:
            current = target.read_text(encoding="utf-8") if target.is_file() else ""
        except (OSError, UnicodeError) as exc:
            raise CompatibilityViewError(f"{relative}: could not inspect existing output: {exc}") from exc
        state = _inspect_current(current, relative=relative)
        if state == "missing" or current != rendered[relative]:
            changed.append(relative)
    if changed and not check:
        _atomic_write(Path(root), rendered, changed)
    return changed


def generate_compatibility_views(
    template_root: Path | str | None = None,
    instance_root: Path | str | None = None,
    *,
    root: Path | str | None = None,
    mode: str | None = None,
    source_identity: dict[str, Any] | None = None,
) -> list[Path]:
    """Hook used by ``create_instance.py`` and the standalone generator.

    ``template_root`` is intentionally not written.  The instance root is the
    transaction target; the source identity is already recorded in its lock.
    """
    del template_root, mode, source_identity
    target = instance_root if instance_root is not None else root
    if target is None:
        raise CompatibilityViewError("instance_root is required")
    return write_views(Path(target))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="fail if a view is stale")
    args = parser.parse_args(argv)
    try:
        changed = write_views(args.root.resolve(), check=args.check)
    except (CompatibilityViewError, OSError, yaml.YAMLError if yaml else Exception) as exc:
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
