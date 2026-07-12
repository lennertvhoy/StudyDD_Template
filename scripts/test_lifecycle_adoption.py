#!/usr/bin/env python3
"""Prove the local StudyDD adoption path with a synthetic temporary instance."""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def snapshot(root: Path) -> dict[str, bytes]:
    ignored = {".git", "__pycache__", ".pytest_cache", ".studydd"}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not any(part in ignored for part in path.relative_to(root).parts)
    }


def stateport_command(stateport_root: Path, *args: str) -> list[str]:
    return [str(stateport_root / "stateport"), *args]


def write_stateport_descriptor(path: Path, template_path: Path) -> None:
    data: dict[str, Any] = {
        "apiVersion": "statedd.stateport.io/v1alpha1",
        "kind": "Instance",
        "metadata": {"id": "studydd-stateport-proof", "name": "Synthetic StatePort proof"},
        "spec": {
            "templateRef": {"id": "studydd", "path": str(template_path)},
            "status": "draft",
            "owner": {"name": "Synthetic Owner", "handle": "@synthetic"},
            "approvalPolicy": {"L2": "auto", "L3": "require_approval", "L4": "require_approval", "L5": "require_admin"},
            "gdpr": {"dataSubjectCategory": "synthetic", "pseudonymised": True, "dpiaRequired": False},
        },
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_stateport_lock(root: Path, source: Path, digest: str) -> None:
    manifest = yaml.safe_load((source / ".statedd/manifest.yaml").read_text(encoding="utf-8"))
    merge = {
        "replace_if_unmodified": "replace",
        "preserve": "preserve",
        "generated": "replace",
        "append_only": "append_only",
    }
    files = []
    for asset in manifest["assets"]:
        if asset["kind"] != "file":
            continue
        target = root / asset["path"]
        files.append(
            {
                "path": asset["path"],
                "owner": asset["owner"],
                "merge": merge[asset["updatePolicy"]],
                "required": asset["required"],
                "sensitivity": asset["sensitivity"],
                "sourceHash": sha256_file(source / asset["source"]) if asset.get("source") else None,
                "materializedHash": None if asset["owner"] == "generated" else sha256_file(target),
            }
        )
    lock = {
        "formatVersion": "statedd.lock/v1",
        "instanceId": "studydd-stateport-proof",
        "template": {
            "id": "studydd",
            "version": "0.10.0",
            "sourceRevision": digest,
            "sourcePath": str(source),
            "source": {
                "formatVersion": "statedd.source/v2",
                "kind": "local_development",
                "sourceClass": "canonical_source",
                "productionEligible": True,
                "checkoutLocation": str(source),
                "sourceDigest": digest,
                "resolvedCommit": None,
            },
        },
        "files": files,
    }
    # Use StatePort's own deterministic writer for this test-only lock. StudyDD
    # remains a consumer of the StatePort contract and does not copy its parser.
    stateport_root = Path(os.environ["STATEPORT_ROOT"])
    sys.path.insert(0, str(stateport_root / "packages/statedd-core/src"))
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        from statedd_core.lifecycle import _write_yaml

        _write_yaml(root / ".statedd/lock.yaml", lock)
    finally:
        sys.dont_write_bytecode = previous


def main() -> int:
    stateport_root = Path(os.environ.get("STATEPORT_ROOT", "")).resolve()
    if not stateport_root.is_dir() or not (stateport_root / "stateport").is_file():
        print("Set STATEPORT_ROOT to the StatePort checkout for this local proof.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="studydd-lifecycle-adoption-") as raw:
        workspace = Path(raw)
        source = workspace / "template"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        run(["git", "init", "-b", "main"], source)
        run(["git", "config", "user.name", "StudyDD proof"], source)
        run(["git", "config", "user.email", "studydd-proof@example.invalid"], source)
        run(["git", "remote", "add", "origin", "https://github.com/lennertvhoy/StudyDD_Template.git"], source)
        run(["git", "add", "."], source)
        run(["git", "commit", "-m", "synthetic StudyDD template"], source)
        source_before = snapshot(source)

        validated = run(stateport_command(stateport_root, "validate-external-template", str(source), "--json"), stateport_root)
        report = json.loads(validated.stdout)
        assert report["valid"] is True
        assert report["templateId"] == "studydd"
        assert report["sourceClass"] == "canonical_source"
        assert report["productionEligible"] is True
        assert report["manifestVersion"] == "statedd.template-manifest/v2"

        instance = workspace / "studydd-instance"
        run(
            [sys.executable, "scripts/create_instance.py", "--target", str(instance), "--remote", "https://github.com/example/SyntheticStudy.git"],
            source,
        )
        assert snapshot(source) == source_before
        mode = yaml.safe_load((instance / "state/STUDYDD_MODE.yaml").read_text(encoding="utf-8"))
        assert mode["mode"] == "bootstrap"
        profile = instance / "state/LEARNER_PROFILE.yaml"
        profile.write_text(profile.read_text(encoding="utf-8") + "\n# synthetic preference placeholder\n", encoding="utf-8")
        target = instance / "targets/synthetic-proof"
        target.mkdir(parents=True)
        (target / "TARGET.yaml").write_text(
            "id: synthetic-proof\ntype: skill\ntitle: Synthetic proof target\n"
            "description: Public-safe temporary lifecycle fixture.\n",
            encoding="utf-8",
        )
        profile_before_regeneration = profile.read_bytes()
        generated_before = snapshot(instance)
        run([sys.executable, "scripts/generate_compatibility_views.py", "--root", str(instance)], instance)
        generated_after_first = snapshot(instance)
        run([sys.executable, "scripts/generate_compatibility_views.py", "--root", str(instance), "--check"], instance)
        run([sys.executable, "scripts/generate_compatibility_views.py", "--root", str(instance)], instance)
        assert profile.read_bytes() == profile_before_regeneration
        assert (target / "TARGET.yaml").is_file()
        assert snapshot(instance) == generated_after_first
        assert generated_after_first != generated_before
        run([sys.executable, "scripts/check_studydd.py"], instance)
        lock = yaml.safe_load((instance / ".statedd/lock.yaml").read_text(encoding="utf-8"))
        assert lock["template"]["id"] == "studydd"
        assert lock["template"]["version"] == "0.10.0"
        assert lock["template"]["sourceRevision"].startswith("sha256:")
        assert lock["instance"]["mode"] == "bootstrap"

        # StatePort classification is proved against a StatePort-compatible
        # synthetic descriptor, while StudyDD retains authority over its own
        # domain instance descriptor and validator.
        stateport_instance = workspace / "stateport-instance"
        shutil.copytree(source, stateport_instance, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        write_stateport_descriptor(stateport_instance / "instance.yaml", source)
        write_stateport_lock(stateport_instance, source, report["digest"])
        state_profile = stateport_instance / "state/LEARNER_PROFILE.yaml"
        state_profile.write_text("synthetic: true\n", encoding="utf-8")
        overrides = run(stateport_command(stateport_root, "inspect-overrides", str(stateport_instance), str(source), "--json"), stateport_root)
        override_report = json.loads(overrides.stdout)
        changed = [item for item in override_report["files"] if item["path"] == "state/LEARNER_PROFILE.yaml"]
        assert changed and changed[0]["classification"] == "changed"
        protected = stateport_instance / ".gitignore"
        original = protected.read_bytes()
        protected.write_bytes(original + b"\n# synthetic protected-path probe\n")
        blocked = run(stateport_command(stateport_root, "inspect-overrides", str(stateport_instance), str(source), "--json"), stateport_root)
        blocked_report = json.loads(blocked.stdout)
        assert blocked_report["blocked"] is True
        assert any(item["path"] == ".gitignore" and item["classification"] == "overridden" for item in blocked_report["files"])
        protected.write_bytes(original)
        assert snapshot(source) == source_before

    print("StudyDD external-template adoption golden path passed.")
    print("- canonical template validated by StatePort v2")
    print("- synthetic bootstrap instance created without learner identity")
    print("- instance-owned changes survived deterministic regeneration")
    print("- StatePort classified instance state as changed and refused protected drift")
    print("- source template remained byte-for-byte unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
