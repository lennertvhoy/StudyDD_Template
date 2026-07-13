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
        "schema_version": generator.SCHEMA_VERSION,
        "view_version": generator.VIEW_VERSION,
        "source_digest": mode["source_digest"],
        "mode": "template",
        "template_remote": "https://github.com/lennertvhoy/StudyDD_Template.git",
        "personalized": False,
        "public_safe": True,
        "modules": [
            "studydd.core",
            "studydd.activities",
            "studydd.source-freshness",
        ],
    }
    assert version["template_version"] == "0.11.0"
    assert version["template_commit"] == ""
    assert version["template_source_digest"] == ""
    assert version["template_source_path"] == ""
    assert manifest["generated_by"] == generator.SCRIPT_PATH
    assert manifest["files"]["state/LEARNER_PROFILE.yaml"]["owner"] == "instance"
    assert manifest["files"]["state/LEARNER_PROFILE.yaml"]["boundary"] == "instance"
    for relative, content in first.items():
        assert content.endswith("\n")
        assert "\r" not in content
        assert f"# Schema: {generator.SCHEMA_VERSION}\n" in content
        assert f"# Source digest: {yaml.safe_load(content)['source_digest']}\n" in content

    paths = list(manifest["files"])
    assert paths == sorted(paths)


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


def test_extensions_are_preserved_and_paths_are_portable() -> None:
    generator = load_generator()
    import yaml

    with tempfile.TemporaryDirectory(prefix="studydd-compatibility-extension-") as raw:
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

        descriptor = yaml.safe_load((root / "instance.yaml").read_text(encoding="utf-8"))
        descriptor["spec"]["extensions"] = {"com.example.study": {"enabled": True}}
        (root / "instance.yaml").write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
        lock = yaml.safe_load((root / ".statedd/lock.yaml").read_text(encoding="utf-8"))
        lock["template"]["sourcePath"] = str(root / ".." / "external-template")
        (root / ".statedd/lock.yaml").write_text(yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")
        overlay = yaml.safe_load((root / "state/STATE_MANIFEST.instance.yaml").read_text(encoding="utf-8"))
        overlay["extensions"] = {"com.example.instance": {"keep": "yes"}}
        (root / "state/STATE_MANIFEST.instance.yaml").write_text(
            yaml.safe_dump(overlay, sort_keys=False), encoding="utf-8"
        )

        generator.write_views(root)
        mode = yaml.safe_load((root / generator.MODE_VIEW).read_text(encoding="utf-8"))
        version = yaml.safe_load((root / generator.VERSION_VIEW).read_text(encoding="utf-8"))
        manifest = yaml.safe_load((root / generator.MANIFEST_VIEW).read_text(encoding="utf-8"))
        assert mode["extensions"]["com.example.study"]["enabled"] is True
        assert manifest["extensions"]["com.example.instance"]["keep"] == "yes"
        assert version["template_source_path"] == ""
        assert not version["template_source_path"].startswith("/")
        assert generator.source_digest(root).startswith("sha256:")


def test_manual_edit_and_extension_conflict_fail_closed_without_partial_output() -> None:
    generator = load_generator()
    import yaml

    with tempfile.TemporaryDirectory(prefix="studydd-compatibility-safety-") as raw:
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

        generator.write_views(root)
        before = {relative: (root / relative).read_bytes() for relative in generator.VIEW_PATHS}
        mode_path = root / generator.MODE_VIEW
        mode_path.write_bytes(mode_path.read_bytes() + b"# manual edit\n")
        try:
            generator.write_views(root)
        except generator.CompatibilityViewError as exc:
            assert "manual edit" in str(exc)
        else:
            raise AssertionError("manual generated-view edit was accepted")
        assert (root / generator.VERSION_VIEW).read_bytes() == before[generator.VERSION_VIEW]
        assert (root / generator.MANIFEST_VIEW).read_bytes() == before[generator.MANIFEST_VIEW]

        overlay_path = root / "state/STATE_MANIFEST.instance.yaml"
        overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
        overlay["extensions"] = {"schema_version": "instance override"}
        overlay_path.write_text(yaml.safe_dump(overlay, sort_keys=False), encoding="utf-8")
        for relative, content in before.items():
            (root / relative).write_bytes(content)
        try:
            generator.write_views(root)
        except generator.CompatibilityViewError as exc:
            assert "conflicts with generated field" in str(exc)
        else:
            raise AssertionError("extension conflict was accepted")
        assert {relative: (root / relative).read_bytes() for relative in generator.VIEW_PATHS} == before


def test_regeneration_is_idempotent_and_replacement_rolls_back() -> None:
    generator = load_generator()
    import yaml

    with tempfile.TemporaryDirectory(prefix="studydd-compatibility-transaction-") as raw:
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
        first = generator.write_views(root)
        assert len(first) == 3
        snapshot = {relative: (root / relative).read_bytes() for relative in generator.VIEW_PATHS}
        assert generator.write_views(root) == []
        assert {relative: (root / relative).read_bytes() for relative in generator.VIEW_PATHS} == snapshot

        descriptor_path = root / "instance.yaml"
        descriptor = yaml.safe_load(descriptor_path.read_text(encoding="utf-8"))
        descriptor["spec"]["mode"] = "bootstrap"
        descriptor_path.write_text(yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8")
        real_replace = generator.os.replace
        calls = {"count": 0}

        def fail_once(source: str | bytes | Path, target: str | bytes | Path) -> None:
            calls["count"] += 1
            if calls["count"] == 4:
                raise OSError("synthetic transaction failure")
            real_replace(source, target)

        generator.os.replace = fail_once
        try:
            try:
                generator.write_views(root)
            except OSError as exc:
                assert "synthetic transaction failure" in str(exc)
            else:
                raise AssertionError("synthetic replacement failure was not surfaced")
        finally:
            generator.os.replace = real_replace
        assert {relative: (root / relative).read_bytes() for relative in generator.VIEW_PATHS} == snapshot


def test_manifest_composition_is_explicit_and_rejects_unknown_keys() -> None:
    generator = load_generator()
    import yaml

    base = {
        "manifest_version": "1.0",
        "files": {"state/example.yaml": {"role": "canonical", "owner": "instance", "boundary": "instance"}},
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
        test_extensions_are_preserved_and_paths_are_portable,
        test_manual_edit_and_extension_conflict_fail_closed_without_partial_output,
        test_regeneration_is_idempotent_and_replacement_rolls_back,
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
