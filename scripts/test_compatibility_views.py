#!/usr/bin/env python3
"""Focused tests for StudyDD ownership separation and compatibility views."""

from __future__ import annotations

import copy
import importlib.util
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "generate_compatibility_views.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_compatibility_views", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load compatibility-view generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_template_outputs_are_deterministic_and_public_safe() -> None:
    generator = load_generator()
    before = (ROOT / "state" / "LEARNER_PROFILE.yaml").read_bytes()
    first = generator.render_views(ROOT)
    second = generator.render_views(ROOT)
    assert first == second
    assert (ROOT / "state" / "LEARNER_PROFILE.yaml").read_bytes() == before

    import yaml

    mode = yaml.safe_load(first[generator.MODE_VIEW])
    version = yaml.safe_load(first[generator.VERSION_VIEW])
    manifest = yaml.safe_load(first[generator.MANIFEST_VIEW])
    assert mode == {
        "mode": "template",
        "template_remote": "https://github.com/lennertvhoy/StudyDD_Template.git",
        "personalized": False,
        "public_safe": True,
        "modules": [
            "studydd.core",
            "studydd.activities",
            "studydd.source-freshness",
            "studydd.fast-drill",
            "studydd.question-bank-engine",
            "studydd.integrations",
        ],
    }
    assert version["template_version"] == "0.10.0"
    assert version["template_commit"] == ""
    assert manifest["generated_by"] == generator.SCRIPT_PATH
    assert manifest["files"]["state/LEARNER_PROFILE.yaml"]["owner"] == "instance"
    assert manifest["files"]["state/LEARNER_PROFILE.yaml"]["boundary"] == "instance"


def test_instance_authority_changes_only_generated_views() -> None:
    generator = load_generator()
    import yaml

    with tempfile.TemporaryDirectory(prefix="studydd-compatibility-") as raw:
        root = Path(raw)
        for source in (
            "instance.yaml",
            ".statedd/lock.yaml",
            "state/STATE_MANIFEST.template.yaml",
            "state/STATE_MANIFEST.instance.yaml",
        ):
            target = root / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / source).read_bytes())
        profile = root / "state" / "LEARNER_PROFILE.yaml"
        profile.write_text("learner: generic\n", encoding="utf-8")
        profile_before = profile.read_bytes()

        descriptor = yaml.safe_load((root / "instance.yaml").read_text(encoding="utf-8"))
        descriptor["spec"].update(
            {
                "mode": "learner_instance",
                "personalized": True,
                "publicSafe": False,
                "templateOrigin": "https://github.com/example/private-study.git",
            }
        )
        (root / "instance.yaml").write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
        lock = yaml.safe_load((root / ".statedd/lock.yaml").read_text(encoding="utf-8"))
        lock["template"]["version"] = "0.11.0"
        lock["template"]["sourceRevision"] = "abc123"
        lock["instance"]["createdFromTemplateVersion"] = "0.10.0"
        (root / ".statedd/lock.yaml").write_text(yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")

        generator.write_views(root)
        mode = yaml.safe_load((root / generator.MODE_VIEW).read_text(encoding="utf-8"))
        version = yaml.safe_load((root / generator.VERSION_VIEW).read_text(encoding="utf-8"))
        assert mode["mode"] == "learner_instance"
        assert mode["template_remote"].endswith("private-study.git")
        assert version["template_version"] == "0.11.0"
        assert version["template_commit"] == "abc123"
        assert version["instance_created_from_template_version"] == "0.10.0"
        assert profile.read_bytes() == profile_before


def test_manifest_composition_is_explicit_and_rejects_unknown_keys() -> None:
    generator = load_generator()
    import yaml

    base = {
        "manifest_version": "1.0",
        "files": {"state/example.yaml": {"role": "canonical", "owner": "template", "boundary": "template"}},
    }
    overlay = {"files": {"state/example.yaml": {"owner": "instance", "boundary": "instance"}}}
    composed = generator.compose_manifest(
        copy.deepcopy(base), copy.deepcopy(overlay), base_path=Path("base"), overlay_path=Path("overlay")
    )
    assert composed["files"]["state/example.yaml"]["role"] == "canonical"
    assert composed["files"]["state/example.yaml"]["owner"] == "instance"
    assert "generated_by" in composed

    bad = {"files": {"state/example.yaml": {"nested": {"owner": "instance"}}}}
    try:
        generator.compose_manifest(base, bad, base_path=Path("base"), overlay_path=Path("overlay"))
    except generator.CompatibilityViewError as exc:
        assert "unknown key" in str(exc)
    else:
        raise AssertionError("generic nested overlay key was accepted")


def main() -> int:
    tests = [
        test_template_outputs_are_deterministic_and_public_safe,
        test_instance_authority_changes_only_generated_views,
        test_manifest_composition_is_explicit_and_rejects_unknown_keys,
    ]
    for test in tests:
        print(f"Running {test.__name__}...")
        test()
        print("  passed")
    print("Compatibility-view tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
