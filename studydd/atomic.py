"""Dependency-free atomic file replacement helpers."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Replace *path* with *text* using a temporary file in the same directory.

    Keeping the temporary file beside the destination makes ``os.replace`` an
    atomic rename on supported local filesystems. The original file remains in
    place if writing or flushing the temporary file fails.
    """

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary = Path(temporary_name)
    previous_mode = None
    try:
        previous_mode = stat.S_IMODE(destination.stat().st_mode)
    except OSError:
        pass
    try:
        with os.fdopen(descriptor, "w", encoding=encoding, newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if previous_mode is not None:
            os.chmod(temporary, previous_mode)
        os.replace(temporary, destination)
    except BaseException:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise
