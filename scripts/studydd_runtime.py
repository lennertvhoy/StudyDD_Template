#!/usr/bin/env python3
"""Shared runtime guards for StudyDD state transitions.

The StateDD instance descriptor is authoritative.  Generated compatibility
views are checked as a safety boundary, but never selected as a competing
source of lifecycle truth.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows uses the explicit error.
    fcntl = None  # type: ignore[assignment]

try:
    import yaml
except ImportError:  # pragma: no cover - requirements.txt supplies PyYAML.
    yaml = None  # type: ignore[assignment]


VALID_MODES = {"template", "bootstrap", "learner_instance"}


class RuntimeBoundaryError(ValueError):
    """A runtime operation crossed a repository boundary unsafely."""


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeBoundaryError("PyYAML is required")
    if not path.is_file():
        raise RuntimeBoundaryError(f"required lifecycle file is missing: {path}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeBoundaryError(f"could not read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeBoundaryError(f"{path} must contain a mapping")
    return value


def repository_mode(repo_root: Path | str) -> str:
    """Return the descriptor mode and fail closed on a stale view."""

    root = Path(repo_root).resolve()
    descriptor = _load_yaml(root / "instance.yaml")
    spec = descriptor.get("spec")
    if not isinstance(spec, dict) or spec.get("mode") not in VALID_MODES:
        raise RuntimeBoundaryError(
            "instance.yaml spec.mode must be template, bootstrap, or learner_instance"
        )
    mode = str(spec["mode"])

    compatibility_path = root / "state/STUDYDD_MODE.yaml"
    if compatibility_path.is_file():
        compatibility = _load_yaml(compatibility_path)
        compatibility_mode = compatibility.get("mode")
        if compatibility_mode != mode:
            raise RuntimeBoundaryError(
                "instance.yaml spec.mode disagrees with generated "
                "state/STUDYDD_MODE.yaml; regenerate compatibility views before writing"
            )
    return mode


def require_learner_instance(repo_root: Path | str) -> None:
    mode = repository_mode(repo_root)
    if mode != "learner_instance":
        raise RuntimeBoundaryError(
            f"state transition refused in {mode} mode; learner_instance is required"
        )


@contextlib.contextmanager
def transition_lock(repo_root: Path | str) -> Iterator[None]:
    """Serialize state transitions across threads and processes on POSIX."""

    if fcntl is None:  # pragma: no cover - the supported runtime is POSIX.
        raise RuntimeBoundaryError("POSIX file locking is required for state transitions")
    root = Path(repo_root).resolve()
    lock_path = root / ".studydd" / "transition.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def content_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
