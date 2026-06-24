#!/usr/bin/env python3
"""Test the public StudyDD demo replay.

Runs scripts/run_demo_replay.py and asserts the demo flow produces the
expected artifacts, transcript, and validation result.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def main() -> int:
    print("StudyDD demo replay test")
    print("========================")

    result = run([sys.executable, "scripts/run_demo_replay.py"], ROOT, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("Demo replay test failed: script returned non-zero.")
        return 1

    stdout = result.stdout

    required_transcript_fragments = [
        "StudyDD demo replay",
        "Created learner instance",
        "Initialized learner profile: Demo Learner",
        "Initialized target: AI Search Fundamentals Demo",
        "Active study skill: it_certification",
        "Built a context pack instead of loading every file",
        "Agent asked one question",
        "Learner answered",
        "Agent graded honestly: partial",
        "Evidence recorded: ev_demo_001",
        "Review scheduled",
        "Selector when review is due: review first",
        "Learner override recorded with reason",
        "Validation passed",
        "StudyDD checks source freshness before generating product-current questions",
        "The demo uses a demo official source marked fresh",
        "The agent does not search the web because the cached source is fresh enough",
        "If the source were stale, StudyDD would ask to refresh or choose a stable review instead",
        "StudyDD suggestion:",
        "You missed a scenario tradeoff. Next time, use a short comparison drill.",
        "Learner control:",
        "You can accept, modify, or override this.",
    ]

    missing = []
    for fragment in required_transcript_fragments:
        if fragment not in stdout:
            missing.append(fragment)

    if missing:
        print("Missing expected transcript fragments:")
        for fragment in missing:
            print(f"  - {fragment}")
        return 1

    print("Demo replay test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
