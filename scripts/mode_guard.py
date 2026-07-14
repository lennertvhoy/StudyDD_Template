"""CLI adapter for the shared StudyState mode precondition."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from studydd.mode import ModeViolation, RepoMode, require_mode


def require_learner_mode(
    repo_root: Path = ROOT,
    *,
    operation: str,
    learner_instance_only: bool = False,
) -> int:
    allowed = (RepoMode.LEARNER_INSTANCE,) if learner_instance_only else (
        RepoMode.BOOTSTRAP,
        RepoMode.LEARNER_INSTANCE,
    )
    try:
        require_mode(repo_root, *allowed, operation=operation)
    except ModeViolation as exc:
        print(f"Error [{exc.code}]: {exc}", file=sys.stderr)
        return 2
    return 0
