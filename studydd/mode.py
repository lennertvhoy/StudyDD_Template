"""Executable repository mode and remote preconditions."""

from __future__ import annotations

import re
import subprocess
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

try:
    from enum import StrEnum
except ImportError:  # Python 3.10 compatibility.
    class StrEnum(str, Enum):
        pass

TEMPLATE_REMOTE = "https://github.com/lennertvhoy/StudyDD_Template.git"
MODE_FILE = Path("state") / "STUDYDD_MODE.yaml"


class RepoMode(StrEnum):
    TEMPLATE = "template"
    BOOTSTRAP = "bootstrap"
    LEARNER_INSTANCE = "learner_instance"


class ModeViolation(RuntimeError):
    """A stable, user-safe precondition failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _mode_value(text: str) -> str | None:
    match = re.search(
        r"(?m)^\s*mode\s*:\s*(?:['\"]([^'\"]+)['\"]|([^#\s]+))",
        text,
    )
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip()


def load_repo_mode(repo_root: Path) -> RepoMode:
    """Load and validate only the repository's mode marker."""
    path = Path(repo_root) / MODE_FILE
    if not path.is_file():
        raise ModeViolation("MODE_FILE_MISSING", f"Missing mode file: {MODE_FILE.as_posix()}.")
    try:
        raw = _mode_value(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ModeViolation("MODE_FILE_MISSING", f"Could not read {MODE_FILE.as_posix()}: {exc}.") from exc

    try:
        return RepoMode(raw or "")
    except ValueError as exc:
        value = raw if raw is not None else "(missing)"
        raise ModeViolation("MODE_INVALID", f"Unsupported repository mode: {value!r}.") from exc


def normalized_remote(value: str) -> str:
    """Normalize transport and cosmetic Git URL differences only."""
    raw = value.strip()
    if not raw:
        return ""

    if raw.startswith("git@") and ":" in raw:
        host, path = raw[4:].split(":", 1)
    else:
        parsed = urlparse(raw)
        if parsed.scheme and parsed.netloc:
            host = parsed.hostname or parsed.netloc
            path = parsed.path
        else:
            return raw.rstrip("/").removesuffix(".git").lower()

    path = path.strip().strip("/")
    if path.lower().endswith(".git"):
        path = path[:-4]
    return f"{host.lower()}/{path.lower()}"


def _origin_remote(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().splitlines()[0]

    fallback = subprocess.run(
        ["git", "remote", "-v"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    for line in fallback.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            return parts[1]
    return ""


def validate_mode_remote(repo_root: Path, mode: RepoMode) -> None:
    """Require a mode-compatible origin remote."""
    remote = _origin_remote(Path(repo_root))
    if not remote:
        raise ModeViolation("REMOTE_MISSING", "No Git remote is configured for this repository.")

    actual = normalized_remote(remote)
    template = normalized_remote(TEMPLATE_REMOTE)
    if mode is RepoMode.TEMPLATE and actual != template:
        raise ModeViolation(
            "MODE_REMOTE_MISMATCH",
            "Template mode requires the exact StudyState Template compatibility remote.",
        )
    if mode is not RepoMode.TEMPLATE and actual == template:
        raise ModeViolation("MODE_REMOTE_MISMATCH", "Bootstrap and learner-instance modes require a non-template remote.")


def require_mode(repo_root: Path, *allowed: RepoMode, operation: str) -> RepoMode:
    """Validate mode/remote compatibility and authorize one operation."""
    mode = load_repo_mode(Path(repo_root))
    validate_mode_remote(Path(repo_root), mode)
    if mode not in allowed:
        if mode is RepoMode.TEMPLATE and RepoMode.TEMPLATE not in allowed:
            raise ModeViolation(
                "INSTANCE_REQUIRED",
                f"Cannot {operation} in template mode. Create a learner instance with "
                "scripts/create_instance.py (mode: learner_instance); see protocols/INSTANTIATE_TEMPLATE.md.",
            )
        allowed_text = ", ".join(item.value for item in allowed) or "no modes"
        raise ModeViolation(
            "MODE_INVALID",
            f"Cannot {operation} in repository mode '{mode.value}'; allowed modes: {allowed_text}.",
        )
    return mode
