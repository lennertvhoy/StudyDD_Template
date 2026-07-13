#!/usr/bin/env python3
"""Create a deterministic StudyDD learner instance from the public template.

Usage:
    python3 scripts/create_instance.py \
        --target ../Study_MyTarget \
        --remote https://github.com/example/Study_MyTarget.git
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

AGENT_NAME = "StudyDD Agent"
AGENT_EMAIL = "studydd-agent@example.invalid"
TEMPLATE_ORIGIN = "https://github.com/lennertvhoy/StudyDD_Template.git"

# Optional cross-repository seam.  StudyDD does not implement StatePort's
# lifecycle parser.  When a lifecycle lane is present, it may expose
# ``scripts/lifecycle_adapter.py`` or ``scripts/generate_compatibility_views.py``
# with these callables:
#
#   materialize_instance(template_root, instance_root, *, mode,
#                        source_identity)
#   generate_compatibility_views(template_root, instance_root, *, mode,
#                                source_identity)
#
# The hooks own manifest/ownership interpretation and may write the canonical
# lock and generated views.  This creator only supplies paths and provenance.
# Until that API lands, the local fallback below keeps the existing bootstrap
# flow working without reimplementing StatePort parsing.
LIFECYCLE_ADAPTER_MODULES = (
    "lifecycle_adapter.py",
    "generate_compatibility_views.py",
)


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"  cwd: {cwd}")
        print(f"  stderr: {result.stderr.strip()}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def is_non_empty_dir(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.is_dir():
        return False
    for child in path.iterdir():
        if child.name != ".git":
            return True
    return False


def get_template_version_and_commit(yaml: object, root: Path = ROOT) -> tuple[str, str]:
    version_path = root / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    data = yaml.safe_load(version_path.read_text(encoding="utf-8")) or {}
    version = data.get("template_version", "unknown")

    commit = ""
    try:
        commit = run(["git", "rev-parse", "HEAD"], root, check=False).stdout.strip()
    except Exception:
        pass
    return version, commit


def _git_commit_and_clean(root: Path) -> tuple[str, bool]:
    """Return a commit only when the local source tree is clean enough to trust."""
    commit_result = run(["git", "rev-parse", "HEAD"], root, check=False)
    status_result = run(["git", "status", "--porcelain"], root, check=False)
    commit = commit_result.stdout.strip() if commit_result.returncode == 0 else ""
    clean = status_result.returncode == 0 and not status_result.stdout.strip()
    return (commit if clean else ""), clean


def _source_digest(root: Path) -> str:
    """Hash source bytes and relative names without parsing lifecycle files."""
    digest = hashlib.sha256()
    ignored_dirs = {".git", ".studydd", "__pycache__", ".pytest_cache", ".venv"}
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in ignored_dirs for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    )
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def _source_identity(root: Path, template_version: str) -> dict[str, Any]:
    commit, clean = _git_commit_and_clean(root)
    return {
        "kind": "local_template",
        "origin": TEMPLATE_ORIGIN,
        "version": template_version,
        "commit": commit or None,
        "digest": _source_digest(root),
        "commit_verified": bool(commit and clean),
    }


def _load_optional_hook(name: str) -> Callable[..., Any] | None:
    """Load a lifecycle hook by convention, returning None when unavailable."""
    for module_name in LIFECYCLE_ADAPTER_MODULES:
        path = ROOT / "scripts" / module_name
        if not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        spec = importlib.util.spec_from_file_location(
            f"studydd_lifecycle_{path.stem}", path
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            # Loading an optional hook must not mutate the source checkout by
            # creating __pycache__ entries. The template is an immutable input
            # to instantiation and regeneration.
            previous = sys.dont_write_bytecode
            sys.dont_write_bytecode = True
            try:
                spec.loader.exec_module(module)
            finally:
                sys.dont_write_bytecode = previous
        except Exception as exc:  # pragma: no cover - integration seam
            raise RuntimeError(f"could not load lifecycle hook {path}: {exc}") from exc
        hook = getattr(module, name, None)
        if callable(hook):
            return hook
    return None


def _call_hook(
    hook: Callable[..., Any],
    template: Path,
    target: Path,
    *,
    mode: str,
    source_identity: Mapping[str, Any],
) -> Any:
    """Call the documented hook while tolerating a narrower additive seam."""
    values = {
        "template_root": template,
        "instance_root": target,
        "template_path": template,
        "instance_path": target,
        "mode": mode,
        "source_identity": dict(source_identity),
    }
    parameters = inspect.signature(hook).parameters
    accepts_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    kwargs = values if accepts_kwargs else {
        key: value for key, value in values.items() if key in parameters
    }
    positional = []
    if not kwargs and len(parameters) >= 2:
        positional = [template, target]
    return hook(*positional, **kwargs)


def _write_instance_descriptor(
    target: Path, source_identity: Mapping[str, Any], *, mode: str
) -> None:
    """Create/update only the small lifecycle descriptor, never learner state."""
    descriptor_path = target / "instance.yaml"
    if descriptor_path.exists():
        try:
            data = yaml_safe_load(descriptor_path)
        except Exception:
            # A template-owned descriptor may be validated by the lifecycle
            # adapter. Do not replace an existing file we cannot safely read.
            return
        if not isinstance(data, dict):
            return
    else:
        data = {
            "apiVersion": "studydd.stateport.io/v1alpha1",
            "kind": "Instance",
            "metadata": {
                "id": "bootstrap",
                "name": "StudyDD bootstrap instance",
            },
            "spec": {},
        }
    spec = data.setdefault("spec", {})
    if not isinstance(spec, dict):
        return
    spec["mode"] = mode
    spec["template"] = {
        "id": "studydd",
        "origin": source_identity["origin"],
        "version": source_identity["version"],
        "commit": source_identity["commit"],
        "digest": source_identity["digest"],
    }
    spec["personalized"] = False
    metadata = data.setdefault("metadata", {})
    if isinstance(metadata, dict) and mode != "template":
        metadata["id"] = "studydd-bootstrap"
        metadata["name"] = "StudyDD bootstrap instance"
    _write_yaml(descriptor_path, data)


def _write_instance_lock(
    target: Path, source_identity: Mapping[str, Any], *, mode: str
) -> None:
    """Record exact local source identity in the instance-owned lifecycle lock."""
    lock_path = target / ".statedd" / "lock.yaml"
    if lock_path.is_symlink():
        raise RuntimeError("lifecycle lock must not be a symlink")
    try:
        data = yaml_safe_load(lock_path)
    except OSError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    data["formatVersion"] = "statedd.lock/v1"
    data["instanceId"] = "studydd-bootstrap"
    template = data.setdefault("template", {})
    if not isinstance(template, dict):
        template = {}
        data["template"] = template
    template.update(
        {
            "id": "studydd",
            "version": source_identity["version"],
            "sourceRevision": source_identity["digest"],
            "sourceCommit": source_identity["commit"] or "",
            "sourcePath": source_identity["origin"],
            "manifestFormatVersion": "statedd.template-manifest/v2",
            "stateddSpecVersion": "statedd-template-v5",
            "instanceSchemaVersion": "studydd.instance-layout/v1",
            "selectedModules": [
                "studydd.core",
                "studydd.activities",
                "studydd.source-freshness",
            ],
        }
    )
    instance = data.setdefault("instance", {})
    if not isinstance(instance, dict):
        instance = {}
        data["instance"] = instance
    instance.update(
        {
            "mode": mode,
            "createdFromTemplateVersion": source_identity["version"],
            "createdFromTemplateCommit": source_identity["commit"] or "",
            "lastTemplateUpgradeVersion": source_identity["version"],
            "lastTemplateUpgradeCommit": source_identity["commit"] or "",
        }
    )
    instance.setdefault("upgradeHistory", [])
    data.setdefault("files", [
        {
            "path": ".statedd/lock.yaml",
            "owner": "generated",
            "merge": "replace",
            "required": True,
            "sensitivity": "internal",
            "sourceHash": None,
            "materializedHash": None,
        }
    ])
    _write_yaml(lock_path, data)


def yaml_safe_load(path: Path) -> Any:
    """Load one descriptor using the existing PyYAML dependency."""
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_yaml(path: Path, data: Mapping[str, Any]) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(dict(data), sort_keys=False), encoding="utf-8")


def _legacy_compatibility_view(
    target: Path, source_identity: Mapping[str, Any], *, mode: str
) -> None:
    """Update legacy views only when no lifecycle generator owns them yet."""
    mode_path = target / "state" / "STUDYDD_MODE.yaml"
    mode_data = yaml_safe_load(mode_path)
    if isinstance(mode_data, dict):
        mode_data["mode"] = mode
        mode_data["template_origin"] = TEMPLATE_ORIGIN
        mode_data["personalized"] = False
        mode_data["public_safe"] = "false_or_review_required"
        _write_yaml(mode_path, mode_data)

    version_path = target / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    version_data = yaml_safe_load(version_path)
    if isinstance(version_data, dict):
        version_data["instance_created_from_template_source"] = dict(source_identity)
        _write_yaml(version_path, version_data)


def _run_lifecycle_hooks(
    template: Path,
    target: Path,
    source_identity: Mapping[str, Any],
    *,
    mode: str,
) -> bool:
    """Delegate ownership/materialisation and generated views when available."""
    materializer = _load_optional_hook("materialize_instance")
    if materializer is not None:
        _call_hook(
            materializer,
            template,
            target,
            mode=mode,
            source_identity=source_identity,
        )

    generator = _load_optional_hook("generate_compatibility_views")
    mode_path = target / "state" / "STUDYDD_MODE.yaml"
    version_path = target / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
    mode_before = mode_path.read_bytes()
    generated_version_before = version_path.read_bytes()
    if generator is not None:
        _call_hook(
            generator,
            template,
            target,
            mode=mode,
            source_identity=source_identity,
        )
    mode_after = mode_path.read_bytes()
    generated_version_after = version_path.read_bytes()
    if generator is None:
        _legacy_compatibility_view(target, source_identity, mode=mode)
    else:
        # Fill only views the optional generator did not produce. This keeps
        # generated output authoritative while retaining compatibility with a
        # partially landed lane-D implementation.
        if mode_before == mode_after:
            mode_data = yaml_safe_load(mode_path)
            if isinstance(mode_data, dict):
                mode_data["mode"] = mode
                mode_data["template_origin"] = TEMPLATE_ORIGIN
                mode_data["personalized"] = False
                mode_data["public_safe"] = "false_or_review_required"
                _write_yaml(mode_path, mode_data)
        if generated_version_before == generated_version_after:
            version_data = yaml_safe_load(version_path)
            if isinstance(version_data, dict):
                version_data["instance_created_from_template_source"] = dict(source_identity)
                _write_yaml(version_path, version_data)
    return materializer is not None or generator is not None


def _validate_instance(target: Path) -> None:
    result = run([sys.executable, "scripts/check_studydd.py"], target, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("StudyDD validation failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a StudyDD learner instance")
    parser.add_argument("--target", required=True, help="Target directory for the instance")
    parser.add_argument("--remote", help="Git remote URL for the instance")
    parser.add_argument(
        "--template",
        help="Local template root for regeneration (creation always uses this template repo)",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate lifecycle-owned outputs in an existing instance",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    remote = args.remote
    template_root = Path(args.template).resolve() if args.template else ROOT

    print("StudyDD create-instance")
    print("=======================")

    try:
        import yaml
    except ImportError:  # pragma: no cover
        print("Error: PyYAML is required.")
        return 1

    # 1. Verify the selected source is the public template. Regeneration is
    # intentionally explicit about its source; it never fetches or resolves a
    # remote/registry reference.
    source_mode_path = template_root / "state" / "STUDYDD_MODE.yaml"
    if not source_mode_path.is_file():
        print(f"Error: template mode marker is missing: {source_mode_path}")
        return 1
    source_mode_data = yaml.safe_load(source_mode_path.read_text(encoding="utf-8")) or {}
    if source_mode_data.get("mode") != "template":
        print(
            "Error: selected source is not in template mode "
            f"(mode={source_mode_data.get('mode')})."
        )
        return 1

    remotes = run(["git", "remote", "-v"], template_root, check=False).stdout
    if "StudyDD_Template" not in remotes:
        print("Error: selected source does not appear to be the StudyDD_Template remote.")
        return 1

    if args.regenerate:
        if remote:
            print("Note: --remote is ignored during regeneration; the existing instance remote is preserved.")
        if not target.is_dir() or not (target / "state" / "STUDYDD_MODE.yaml").is_file():
            print(f"Error: regeneration target is not a StudyDD instance: {target}")
            return 1
        current_mode = yaml_safe_load(target / "state" / "STUDYDD_MODE.yaml").get("mode")
        if current_mode == "template":
            print("Error: refusing to regenerate a template repository.")
            return 1
        template_version, _ = get_template_version_and_commit(yaml, template_root)
        source_identity = _source_identity(template_root, template_version)
        print(f"Regenerating lifecycle-owned outputs in {target}")
        _write_instance_descriptor(target, source_identity, mode=current_mode or "bootstrap")
        _write_instance_lock(target, source_identity, mode=current_mode or "bootstrap")
        _run_lifecycle_hooks(
            template_root,
            target,
            source_identity,
            mode=current_mode or "bootstrap",
        )
        try:
            _validate_instance(target)
        except RuntimeError:
            return 1
        print("Regeneration complete; instance-owned files were left in place.")
        return 0

    if not remote:
        print("Error: --remote is required when creating a new instance.")
        return 1

    # 2. Refuse to overwrite existing non-empty target.
    if target == template_root or target.is_relative_to(template_root):
        print("Error: target directory must be outside the template repository.")
        return 1
    if is_non_empty_dir(target):
        print(f"Error: target directory already exists and is not empty: {target}")
        return 1
    if target.exists() and target.is_file():
        print(f"Error: target path is a file: {target}")
        return 1
    if target.exists() and (target / ".git").exists():
        print(f"Error: target already contains Git metadata: {target / '.git'}")
        return 1

    # 3. Copy template excluding caches and git history.
    print(f"1. Copying template to {target}")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template_root,
        target,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
        ),
    )

    copied_git = target / ".git"
    if copied_git.exists():
        shutil.rmtree(copied_git)

    # 4. Initialize Git.
    print("2. Initializing Git")
    try:
        run(["git", "init", "-b", "main"], target)
    except subprocess.CalledProcessError:
        run(["git", "init"], target)
        try:
            run(["git", "checkout", "-b", "main"], target)
        except subprocess.CalledProcessError:
            run(["git", "branch", "-M", "main"], target)

    run(["git", "config", "user.name", AGENT_NAME], target)
    run(["git", "config", "user.email", AGENT_EMAIL], target)
    run(["git", "remote", "add", "origin", remote], target)

    # 5. Switch mode to bootstrap in the new instance. A lifecycle generator
    # owns the compatibility views and needs to see the copied generated
    # baseline so it can distinguish a stale view from a manual edit. The
    # legacy fallback still updates the old views directly when no generator
    # hook is available.
    print("3. Switching to bootstrap mode")
    generator_available = _load_optional_hook("generate_compatibility_views") is not None
    if not generator_available:
        target_mode_path = target / "state" / "STUDYDD_MODE.yaml"
        target_mode_data = yaml.safe_load(target_mode_path.read_text(encoding="utf-8")) or {}
        target_mode_data["mode"] = "bootstrap"
        target_mode_data["template_origin"] = TEMPLATE_ORIGIN
        target_mode_data["personalized"] = False
        target_mode_data["public_safe"] = "false_or_review_required"
        target_mode_path.write_text(yaml.safe_dump(target_mode_data, sort_keys=False), encoding="utf-8")

    # 6. Record source identity and initialize the small lifecycle descriptor.
    print("4. Recording template origin metadata")
    template_version, _ = get_template_version_and_commit(yaml, template_root)
    source_identity = _source_identity(template_root, template_version)
    template_commit = source_identity["commit"] or ""
    if not generator_available:
        version_path = target / "state" / "STUDYDD_TEMPLATE_VERSION.yaml"
        version_data = yaml.safe_load(version_path.read_text(encoding="utf-8")) or {}
        version_data["instance_created_from_template_version"] = template_version
        version_data["instance_created_from_template_commit"] = template_commit
        version_data["last_template_upgrade_version"] = template_version
        version_data["last_template_upgrade_commit"] = template_commit
        version_path.write_text(yaml.safe_dump(version_data, sort_keys=False), encoding="utf-8")

    _write_instance_descriptor(target, source_identity, mode="bootstrap")
    _write_instance_lock(target, source_identity, mode="bootstrap")

    # 7. Let the lifecycle lane materialize ownership/lock and generate views.
    print("5. Applying available lifecycle adapter and compatibility generator")
    adapter_available = _run_lifecycle_hooks(
        template_root,
        target,
        source_identity,
        mode="bootstrap",
    )
    if not adapter_available:
        print("No optional lifecycle adapter is present; using the bootstrap compatibility fallback.")

    # 8. Run bootstrap validation.
    print("6. Running bootstrap validation")
    try:
        _validate_instance(target)
    except RuntimeError:
        return 1
    print("Bootstrap validation passed.")

    # 9. Print next prompt.
    prompt_path = target / "PROMPTS" / "coding_agent_start_prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    print("\nNext step: open the new instance in your coding agent and paste the following prompt:")
    print(f"\n{prompt_text}\n")

    print(f"Instance created at: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
