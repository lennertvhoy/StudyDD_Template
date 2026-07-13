#!/usr/bin/env python3
"""Versioned, append-only Fast Drill checkpoints for StudyDD.

The checkpoint is an instance runtime boundary.  It is deliberately separate
from canonical learner state while a drill is in progress.  Reconciliation is
restartable: a small ignored transaction journal stages canonical writes and
can safely finish after a process crash.

This module does not choose questions or route on question text.  It records
typed answer operations and applies only the explicit state effects described
by the checkpoint contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any, Literal, Union

try:
    import yaml
except ImportError:  # pragma: no cover - requirements.txt supplies PyYAML.
    yaml = None  # type: ignore[assignment]

try:
    from .studydd_runtime import RuntimeBoundaryError, require_learner_instance, transition_lock
except ImportError:  # pragma: no cover - direct CLI execution.
    from studydd_runtime import RuntimeBoundaryError, require_learner_instance, transition_lock


ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_RELATIVE = Path("state/ACTIVE_DRILL_SESSION.md")
TRANSACTION_RELATIVE = Path(".fast_drill")
CHECKPOINT_FORMAT = "studydd.fast-drill-checkpoint/v2"
TRANSACTION_FORMAT = "studydd.fast-drill-transaction/v1"
CHECKPOINT_VERSION = 2
RECORD_VERSION = 1
RECOVERY_AGE_HOURS = 4

VerdictValue = Literal["correct", "partial", "incorrect", "unclear", "override"]
ConfidenceValue = Literal["high", "medium", "low"]


class CheckpointError(RuntimeError):
    """A checkpoint or reconciliation contract violation."""


class ModeRefused(CheckpointError):
    """The operation was requested outside a learner instance."""


class SimulatedCrash(CheckpointError):
    """Test-only interruption used to prove restartable reconciliation."""


class Verdict(str, Enum):
    CORRECT = "correct"
    PARTIAL = "partial"
    INCORRECT = "incorrect"
    UNCLEAR = "unclear"
    OVERRIDE = "override"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OperationKind(str, Enum):
    START = "start"
    APPEND_ANSWER = "append_answer"
    RECOVER = "recover"
    END = "end"


@dataclass(frozen=True)
class FastDrillSettings:
    """Read-only settings from the instance-owned learner profile."""

    fast_drill_mode: bool = False
    auto_state_update_during_drills: bool = False
    authority_path: str = "state/LEARNER_PROFILE.yaml"


@dataclass(frozen=True)
class AnswerRecord:
    """One immutable, hash-linked answer record in the checkpoint."""

    sequence: int
    record_id: str
    recorded_at: str
    question_id: str
    skill_id: str
    concept: str
    answer_summary: str
    verdict: Verdict
    correction_summary: str
    confidence: Confidence
    evidence_marker: str
    previous_hash: str
    record_hash: str

    @classmethod
    def from_mapping(cls, value: Any) -> "AnswerRecord":
        if not isinstance(value, dict):
            raise CheckpointError("answer record must be a mapping")
        if value.get("type") != "answer" or value.get("record_version") != RECORD_VERSION:
            raise CheckpointError("answer record has an unsupported type or version")

        def required_string(key: str, *, allow_empty: bool = False) -> str:
            item = value.get(key)
            if not isinstance(item, str) or (not allow_empty and not item.strip()):
                raise CheckpointError(f"answer record field {key!r} must be a string")
            if len(item) > 4000:
                raise CheckpointError(f"answer record field {key!r} is too long")
            return item

        sequence = value.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            raise CheckpointError("answer record sequence must be a positive integer")
        try:
            verdict = Verdict(required_string("verdict"))
            confidence = Confidence(required_string("confidence"))
        except ValueError as exc:
            raise CheckpointError(str(exc)) from exc

        record = cls(
            sequence=sequence,
            record_id=required_string("record_id"),
            recorded_at=required_string("recorded_at"),
            question_id=required_string("question_id"),
            skill_id=required_string("skill_id"),
            concept=required_string("concept"),
            answer_summary=required_string("answer_summary", allow_empty=True),
            verdict=verdict,
            correction_summary=required_string("correction_summary", allow_empty=True),
            confidence=confidence,
            evidence_marker=required_string("evidence_marker"),
            previous_hash=required_string("previous_hash"),
            record_hash=required_string("record_hash"),
        )
        expected = record.calculate_hash()
        if record.record_hash != expected:
            raise CheckpointError(
                f"answer record {record.record_id!r} has an invalid hash"
            )
        return record

    def payload(self) -> dict[str, Any]:
        return {
            "type": "answer",
            "record_version": RECORD_VERSION,
            "sequence": self.sequence,
            "record_id": self.record_id,
            "recorded_at": self.recorded_at,
            "question_id": self.question_id,
            "skill_id": self.skill_id,
            "concept": self.concept,
            "answer_summary": self.answer_summary,
            "verdict": self.verdict.value,
            "correction_summary": self.correction_summary,
            "confidence": self.confidence.value,
            "evidence_marker": self.evidence_marker,
            "previous_hash": self.previous_hash,
        }

    def calculate_hash(self) -> str:
        encoded = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def to_mapping(self) -> dict[str, Any]:
        value = self.payload()
        value["record_hash"] = self.record_hash
        return value


@dataclass(frozen=True)
class Checkpoint:
    metadata: dict[str, Any]
    records: tuple[AnswerRecord, ...]

    def digest(self) -> str:
        return sha256_bytes(render_checkpoint(self).encode("utf-8"))


@dataclass(frozen=True)
class StartOperation:
    session_id: str
    target_id: str
    mode: str = "normal"
    drill_type: str = "retrieval_question"
    source_ref: str = ""


@dataclass(frozen=True)
class AppendAnswerOperation:
    question_id: str
    skill_id: str
    concept: str
    answer_summary: str
    verdict: VerdictValue
    correction_summary: str
    confidence: ConfidenceValue
    evidence_marker: str
    record_id: str | None = None


@dataclass(frozen=True)
class RecoverOperation:
    apply: bool = False


@dataclass(frozen=True)
class EndOperation:
    apply: bool = False


CheckpointOperation = Union[
    StartOperation,
    AppendAnswerOperation,
    RecoverOperation,
    EndOperation,
]


@dataclass(frozen=True)
class Reconciliation:
    session_id: str
    target_id: str
    drill_type: str
    records: tuple[AnswerRecord, ...]
    evidence_items: tuple[dict[str, str], ...]
    skill_updates: dict[str, dict[str, Any]]
    study_state: dict[str, Any]


def _require_yaml() -> Any:
    if yaml is None:
        raise CheckpointError("PyYAML is required")
    return yaml


def _root(repo_root: Path | str | None) -> Path:
    return Path(repo_root).resolve() if repo_root else ROOT


def checkpoint_path(repo_root: Path | str | None = None) -> Path:
    return _root(repo_root) / CHECKPOINT_RELATIVE


def transaction_root(repo_root: Path | str | None = None) -> Path:
    root = _root(repo_root)
    path = root / TRANSACTION_RELATIVE
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise CheckpointError("Fast Drill transaction root is not a real directory")
    return path


def _load_yaml(path: Path) -> dict[str, Any]:
    parser = _require_yaml()
    if not path.is_file():
        return {}
    try:
        value = parser.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, parser.YAMLError) as exc:
        raise CheckpointError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckpointError(f"{path} must contain a mapping")
    return value


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    _write_atomic(
        path,
        (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8"),
    )


def _sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes()) if path.is_file() else sha256_bytes(b"")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _required_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise CheckpointError(f"{label} must be a non-empty string of at most 200 characters")
    return value


def _require_learner_instance(root: Path) -> None:
    try:
        require_learner_instance(root)
    except RuntimeBoundaryError as exc:
        raise ModeRefused(str(exc)) from exc


def load_settings(repo_root: Path | str | None = None) -> FastDrillSettings:
    """Read settings without ever writing the instance-owned profile."""
    root = _root(repo_root)
    profile = _load_yaml(root / "state/LEARNER_PROFILE.yaml")
    preferences = profile.get("learner_preferences")
    if not isinstance(preferences, dict):
        preferences = {}
    return FastDrillSettings(
        fast_drill_mode=preferences.get("fast_drill_mode") is True,
        auto_state_update_during_drills=(
            preferences.get("auto_state_update_during_drills") is True
        ),
    )


def fast_drill_enabled(repo_root: Path | str | None = None) -> bool:
    return load_settings(repo_root).fast_drill_mode


def auto_state_update_during_drills(repo_root: Path | str | None = None) -> bool:
    return load_settings(repo_root).auto_state_update_during_drills


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _checkpoint_metadata(operation: StartOperation) -> dict[str, Any]:
    return {
        "format": CHECKPOINT_FORMAT,
        "checkpoint_version": CHECKPOINT_VERSION,
        "record_schema_version": RECORD_VERSION,
        "session_id": _required_id(operation.session_id, "session_id"),
        "target_id": _required_id(operation.target_id, "target_id"),
        "mode": _required_id(operation.mode, "mode"),
        "drill_type": _required_id(operation.drill_type, "drill_type"),
        "started_at": now_iso(),
        "source_ref": operation.source_ref or "",
    }


def _genesis_hash(metadata: dict[str, Any]) -> str:
    value = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(("genesis:" + value).encode("utf-8"))


def render_checkpoint(checkpoint: Checkpoint) -> str:
    parser = _require_yaml()
    header = "---\n" + parser.safe_dump(checkpoint.metadata, sort_keys=False) + "---\n"
    records = "".join(
        json.dumps(record.to_mapping(), sort_keys=True, separators=(",", ":")) + "\n"
        for record in checkpoint.records
    )
    return header + records


def load_checkpoint(repo_root: Path | str | None = None) -> Checkpoint:
    path = checkpoint_path(repo_root)
    if not path.is_file():
        raise CheckpointError(f"no active checkpoint at {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckpointError(f"could not read checkpoint: {exc}") from exc
    if not raw.startswith("---\n"):
        raise CheckpointError("checkpoint must start with YAML front matter")
    separator = raw.find("\n---\n", 4)
    if separator < 0:
        raise CheckpointError("checkpoint YAML front matter is not closed")
    parser = _require_yaml()
    metadata = parser.safe_load(raw[4:separator]) or {}
    if not isinstance(metadata, dict):
        raise CheckpointError("checkpoint front matter must be a mapping")
    if metadata.get("format") != CHECKPOINT_FORMAT:
        raise CheckpointError("unsupported checkpoint format")
    if metadata.get("checkpoint_version") != CHECKPOINT_VERSION:
        raise CheckpointError("unsupported checkpoint version")
    if metadata.get("record_schema_version") != RECORD_VERSION:
        raise CheckpointError("unsupported answer record schema version")
    for key in ("session_id", "target_id", "mode", "drill_type", "started_at"):
        _required_id(metadata.get(key), key)

    records: list[AnswerRecord] = []
    expected_sequence = 1
    expected_previous = _genesis_hash(metadata)
    seen_ids: set[str] = set()
    seen_markers: set[str] = set()
    record_text = raw[separator + len("\n---\n") :]
    for line_number, line in enumerate(record_text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CheckpointError(f"invalid answer JSON on line {line_number}: {exc}") from exc
        record = AnswerRecord.from_mapping(value)
        if record.sequence != expected_sequence:
            raise CheckpointError("answer record sequence is not contiguous")
        if record.previous_hash != expected_previous:
            raise CheckpointError("answer record hash chain is broken")
        if record.record_id in seen_ids or record.evidence_marker in seen_markers:
            raise CheckpointError("answer record IDs and evidence markers must be unique")
        records.append(record)
        seen_ids.add(record.record_id)
        seen_markers.add(record.evidence_marker)
        expected_sequence += 1
        expected_previous = record.record_hash
    return Checkpoint(metadata=metadata, records=tuple(records))


def is_drill_active(repo_root: Path | str | None = None) -> bool:
    return checkpoint_path(repo_root).is_file()


def start_drill(
    session_id: str,
    target_id: str,
    mode: str = "normal",
    drill_type: str = "retrieval_question",
    source_ref: str = "",
    repo_root: Path | str | None = None,
) -> int:
    operation = StartOperation(session_id, target_id, mode, drill_type, source_ref)
    try:
        return execute(operation, repo_root=repo_root)
    except ModeRefused as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


def _start(operation: StartOperation, root: Path) -> None:
    with transition_lock(root):
        _require_learner_instance(root)
        if not fast_drill_enabled(root):
            raise CheckpointError(
                "fast_drill_mode is not enabled in the instance-owned learner profile"
            )
        path = checkpoint_path(root)
        if path.exists():
            raise CheckpointError("an active checkpoint already exists; recover or end it first")
        metadata = _checkpoint_metadata(operation)
        content = render_checkpoint(Checkpoint(metadata=metadata, records=()))
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            _fsync_directory(path.parent)
        except FileExistsError as exc:
            raise CheckpointError("an active checkpoint already exists") from exc


def append_checkpoint(
    question_id: str,
    skill_id: str,
    concept: str,
    answer_summary: str,
    verdict: VerdictValue,
    correction_summary: str,
    confidence: ConfidenceValue,
    evidence_marker: str,
    repo_root: Path | str | None = None,
    record_id: str | None = None,
) -> int:
    operation = AppendAnswerOperation(
        question_id=question_id,
        skill_id=skill_id,
        concept=concept,
        answer_summary=answer_summary,
        verdict=verdict,
        correction_summary=correction_summary,
        confidence=confidence,
        evidence_marker=evidence_marker,
        record_id=record_id,
    )
    try:
        return execute(operation, repo_root=repo_root)
    except ModeRefused as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


def _append(operation: AppendAnswerOperation, root: Path) -> None:
    with transition_lock(root):
        _require_learner_instance(root)
        checkpoint = load_checkpoint(root)
        record_id = operation.record_id or operation.evidence_marker
        _required_id(record_id, "record_id")
        _required_id(operation.question_id, "question_id")
        _required_id(operation.skill_id, "skill_id")
        _required_id(operation.concept, "concept")
        _required_id(operation.evidence_marker, "evidence_marker")
        try:
            verdict = Verdict(operation.verdict)
            confidence = Confidence(operation.confidence)
        except ValueError as exc:
            raise CheckpointError(str(exc)) from exc

        for existing in checkpoint.records:
            if existing.record_id == record_id:
                same_content = (
                    existing.question_id == operation.question_id
                    and existing.skill_id == operation.skill_id
                    and existing.concept == operation.concept
                    and existing.answer_summary == operation.answer_summary
                    and existing.verdict == verdict
                    and existing.correction_summary == operation.correction_summary
                    and existing.confidence == confidence
                    and existing.evidence_marker == operation.evidence_marker
                )
                if not same_content:
                    raise CheckpointError("record_id already exists with different content")
                return
            if existing.evidence_marker == operation.evidence_marker:
                raise CheckpointError("evidence_marker already exists with different content")

        sequence = len(checkpoint.records) + 1
        record = _make_record(checkpoint, operation, record_id, verdict, confidence, sequence)
        line = json.dumps(record.to_mapping(), sort_keys=True, separators=(",", ":")) + "\n"
        path = checkpoint_path(root)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())


def _make_record(
    checkpoint: Checkpoint,
    operation: AppendAnswerOperation,
    record_id: str,
    verdict: Verdict,
    confidence: Confidence,
    sequence: int,
) -> AnswerRecord:
    previous_hash = (
        checkpoint.records[-1].record_hash
        if checkpoint.records
        else _genesis_hash(checkpoint.metadata)
    )
    record = AnswerRecord(
        sequence=sequence,
        record_id=record_id,
        recorded_at=now_iso(),
        question_id=operation.question_id,
        skill_id=operation.skill_id,
        concept=operation.concept,
        answer_summary=operation.answer_summary,
        verdict=verdict,
        correction_summary=operation.correction_summary,
        confidence=confidence,
        evidence_marker=operation.evidence_marker,
        previous_hash=previous_hash,
        record_hash="",
    )
    return AnswerRecord(**{**asdict(record), "record_hash": record.calculate_hash()})


def _evidence_items(checkpoint: Checkpoint) -> tuple[dict[str, str], ...]:
    target_id = str(checkpoint.metadata["target_id"])
    session_id = str(checkpoint.metadata["session_id"])
    return tuple(
        {
            "evidence_id": record.evidence_marker,
            "session_id": session_id,
            "record_id": record.record_id,
            "date": record.recorded_at[:10],
            "target_id": target_id,
            "skill_id": record.skill_id,
            "question_id": record.question_id,
            "question_summary": record.concept,
            "learner_answer_summary": record.answer_summary,
            "verdict": record.verdict.value,
            "explanation": (
                "Fast Drill checkpoint record. Correction: "
                + (record.correction_summary or "none")
            ),
            "confidence": record.confidence.value,
        }
        for record in checkpoint.records
    )


def _skill_updates(root: Path, records: tuple[AnswerRecord, ...]) -> dict[str, dict[str, Any]]:
    skill_map = _load_yaml(root / "state/SKILL_MAP.yaml")
    skills = skill_map.get("skills") or []
    by_id = {skill.get("id"): skill for skill in skills if isinstance(skill, dict)}
    grouped: dict[str, list[AnswerRecord]] = {}
    for record in records:
        grouped.setdefault(record.skill_id, []).append(record)

    updates: dict[str, dict[str, Any]] = {}
    for skill_id, entries in grouped.items():
        skill = by_id.get(skill_id)
        if skill is None:
            continue
        current = int(skill.get("readiness") or 0)
        verdicts = {record.verdict for record in entries}
        repaired = any(record.correction_summary for record in entries)
        if Verdict.INCORRECT in verdicts or Verdict.UNCLEAR in verdicts:
            status, readiness, confidence = "weak", min(current, 30), "low"
        elif Verdict.PARTIAL in verdicts:
            status = "weak" if current < 40 else "practiced"
            readiness, confidence = min(max(current, 35), 50), "low"
        elif Verdict.CORRECT in verdicts:
            status, readiness, confidence = "practiced", min(max(current, 50), 55), "medium"
        else:
            continue
        if repaired:
            status, readiness = "practiced" if status != "weak" else status, min(readiness, 55)
        evidence = list(skill.get("evidence") or [])
        for record in entries:
            if record.evidence_marker not in evidence:
                evidence.append(record.evidence_marker)
        updates[skill_id] = {
            "status": status,
            "readiness": readiness,
            "confidence": confidence,
            "evidence": evidence,
        }
    return updates


def build_reconciliation(repo_root: Path | str | None = None) -> Reconciliation:
    root = _root(repo_root)
    checkpoint = load_checkpoint(root)
    if not checkpoint.records:
        raise CheckpointError("cannot reconcile an empty checkpoint")
    study_state = _load_yaml(root / "state/STUDY_STATE.yaml")
    focus = dict(study_state.get("active_focus") or {})
    focus["current_topic"] = checkpoint.metadata["drill_type"]
    focus["reason"] = f"Fast Drill checkpoint reconciled: {checkpoint.metadata['session_id']}"
    study_update = {
        "active_focus": focus,
        "metadata": {
            **dict(study_state.get("metadata") or {}),
            "last_updated": now_iso(),
        },
    }
    return Reconciliation(
        session_id=str(checkpoint.metadata["session_id"]),
        target_id=str(checkpoint.metadata["target_id"]),
        drill_type=str(checkpoint.metadata["drill_type"]),
        records=checkpoint.records,
        evidence_items=_evidence_items(checkpoint),
        skill_updates=_skill_updates(root, checkpoint.records),
        study_state=study_update,
    )


def _evidence_entry(item: dict[str, str]) -> str:
    return (
        f"\n- **Evidence ID:** {item['evidence_id']}\n"
        f"- **Fast Drill session ID:** {item['session_id']}\n"
        f"- **Fast Drill record ID:** {item['record_id']}\n"
        f"- **Date:** {item['date']}\n"
        f"- **Target ID:** {item['target_id']}\n"
        f"- **Skill ID:** {item['skill_id']}\n"
        f"- **Question ID:** {item['question_id']}\n"
        f"- **Question summary:** {item['question_summary']}\n"
        f"- **Learner answer summary:** {item['learner_answer_summary']}\n"
        f"- **Verdict:** {item['verdict']}\n"
        f"- **Explanation:** {item['explanation']}\n"
        f"- **Confidence:** {item['confidence']}\n"
    )


def _evidence_suffix(path: Path, items: tuple[dict[str, str], ...]) -> bytes:
    existing = path.read_text(encoding="utf-8") if path.is_file() else "# Evidence Log\n\n## Evidence items\n\nNone yet.\n"
    suffix_parts: list[str] = []
    for item in items:
        marker = f"- **Evidence ID:** {item['evidence_id']}"
        if marker in existing:
            continue
        suffix_parts.append(_evidence_entry(item))
    return "".join(suffix_parts).encode("utf-8")


def _audit_entry(checkpoint: Checkpoint, *, kind: str) -> str:
    session_id = str(checkpoint.metadata["session_id"])
    target_id = str(checkpoint.metadata["target_id"])
    evidence_ids = ", ".join(record.evidence_marker for record in checkpoint.records)
    record_ids = ", ".join(record.record_id for record in checkpoint.records)
    digest = checkpoint.digest()
    if kind == "activity":
        return (
            f"\n- **Activity ID:** fast-drill-{session_id}\n"
            f"- **Timestamp:** {now_iso()}\n"
            f"- **Type:** {checkpoint.metadata['drill_type']}\n"
            f"- **Target ID:** {target_id}\n"
            f"- **Status:** completed\n"
            f"- **Submitted evidence:** {evidence_ids}\n"
            f"- **Fast Drill session ID:** {session_id}\n"
            f"- **Fast Drill record IDs:** {record_ids}\n"
            f"- **Checkpoint digest:** {digest}\n"
        )
    return (
        f"\n- **Date:** {now_iso()[:10]}\n"
        f"- **Target ID:** {target_id}\n"
        f"- **Focus:** Fast Drill {session_id}\n"
        f"- **Questions asked:** {', '.join(record.question_id for record in checkpoint.records)}\n"
        f"- **Evidence added:** {evidence_ids}\n"
        f"- **State changes:** SKILL_MAP.yaml and STUDY_STATE.yaml reconciled\n"
        f"- **Fast Drill session ID:** {session_id}\n"
        f"- **Fast Drill record IDs:** {record_ids}\n"
        f"- **Checkpoint digest:** {digest}\n"
    )


def _audit_suffix(path: Path, checkpoint: Checkpoint, *, kind: str) -> bytes:
    if kind == "activity":
        default = "# Activity Log\n\n## Activities\n\nNone yet.\n"
        marker = f"**Activity ID:** fast-drill-{checkpoint.metadata['session_id']}"
    else:
        default = "# Session Log\n"
        marker = f"**Fast Drill session ID:** {checkpoint.metadata['session_id']}"
    existing = path.read_text(encoding="utf-8") if path.is_file() else default
    if marker in existing:
        return b""
    prefix = "" if path.is_file() else default
    return (prefix + _audit_entry(checkpoint, kind=kind)).encode("utf-8")


def _build_transaction(root: Path, reconciliation: Reconciliation, checkpoint: Checkpoint) -> dict[str, Any]:
    digest = checkpoint.digest()
    tx_dir = transaction_root(root) / digest[:24]
    if tx_dir.exists():
        return json.loads((tx_dir / "transaction.json").read_text(encoding="utf-8"))
    tx_dir.mkdir(parents=True, exist_ok=False)
    evidence_path = root / "state/EVIDENCE_LOG.md"
    evidence_before = evidence_path.read_bytes() if evidence_path.is_file() else b""
    suffix = _evidence_suffix(evidence_path, reconciliation.evidence_items)
    evidence_after = evidence_before + suffix
    activity_path = root / "activities/ACTIVITY_LOG.md"
    activity_before = activity_path.read_bytes() if activity_path.is_file() else b""
    activity_suffix = _audit_suffix(activity_path, checkpoint, kind="activity")
    activity_after = activity_before + activity_suffix
    session_path = root / "sessions/SESSION_LOG.md"
    session_before = session_path.read_bytes() if session_path.is_file() else b""
    session_suffix = _audit_suffix(session_path, checkpoint, kind="session")
    session_after = session_before + session_suffix
    skill_path = root / "state/SKILL_MAP.yaml"
    study_path = root / "state/STUDY_STATE.yaml"
    skill_data = _load_yaml(skill_path)
    for skill in skill_data.get("skills") or []:
        update = reconciliation.skill_updates.get(skill.get("id"))
        if update:
            skill.update(update)
    skill_data.setdefault("metadata", {})["last_updated"] = now_iso()
    study_data = _load_yaml(study_path)
    study_data.update(reconciliation.study_state)
    stage_skill = tx_dir / "SKILL_MAP.yaml.stage"
    stage_study = tx_dir / "STUDY_STATE.yaml.stage"
    stage_evidence = tx_dir / "EVIDENCE_LOG.md.append"
    stage_activity = tx_dir / "ACTIVITY_LOG.md.append"
    stage_session = tx_dir / "SESSION_LOG.md.append"
    _write_atomic(stage_skill, _require_yaml().safe_dump(skill_data, sort_keys=False).encode("utf-8"))
    _write_atomic(stage_study, _require_yaml().safe_dump(study_data, sort_keys=False).encode("utf-8"))
    _write_atomic(stage_evidence, suffix)
    _write_atomic(stage_activity, activity_suffix)
    _write_atomic(stage_session, session_suffix)
    manifest = {
        "format": TRANSACTION_FORMAT,
        "transaction_id": digest[:24],
        "checkpoint_digest": digest,
        "session_id": reconciliation.session_id,
        "phase": "prepared",
        "files": {
            "evidence": {
                "path": "state/EVIDENCE_LOG.md",
                "kind": "append",
                "before_hash": sha256_bytes(evidence_before),
                "after_hash": sha256_bytes(evidence_after),
                "stage": stage_evidence.name,
            },
            "activity": {
                "path": "activities/ACTIVITY_LOG.md",
                "kind": "append",
                "before_hash": sha256_bytes(activity_before),
                "after_hash": sha256_bytes(activity_after),
                "stage": stage_activity.name,
            },
            "session": {
                "path": "sessions/SESSION_LOG.md",
                "kind": "append",
                "before_hash": sha256_bytes(session_before),
                "after_hash": sha256_bytes(session_after),
                "stage": stage_session.name,
            },
            "skill_map": {
                "path": "state/SKILL_MAP.yaml",
                "kind": "replace",
                "before_hash": _sha256_file(skill_path),
                "after_hash": sha256_bytes(stage_skill.read_bytes()),
                "stage": stage_skill.name,
            },
            "study_state": {
                "path": "state/STUDY_STATE.yaml",
                "kind": "replace",
                "before_hash": _sha256_file(study_path),
                "after_hash": sha256_bytes(stage_study.read_bytes()),
                "stage": stage_study.name,
            },
        },
    }
    _write_json_atomic(tx_dir / "transaction.json", manifest)
    return manifest


def _load_transactions(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    directory = transaction_root(root)
    if not directory.is_dir():
        return []
    result: list[tuple[Path, dict[str, Any]]] = []
    for tx_dir in sorted(directory.iterdir()):
        manifest_path = tx_dir / "transaction.json"
        if tx_dir.is_symlink() or not tx_dir.is_dir() or manifest_path.is_symlink() or not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("format") != TRANSACTION_FORMAT:
            raise CheckpointError("unsupported Fast Drill transaction format")
        _validate_transaction_manifest(root, tx_dir, manifest)
        result.append((tx_dir, manifest))
    return result


_TRANSACTION_TARGETS = {
    "state/EVIDENCE_LOG.md",
    "activities/ACTIVITY_LOG.md",
    "sessions/SESSION_LOG.md",
    "state/SKILL_MAP.yaml",
    "state/STUDY_STATE.yaml",
}


def _safe_transaction_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise CheckpointError(f"{label} is not a safe relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise CheckpointError(f"{label} is not a safe relative path")
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise CheckpointError(f"{label} traverses a symlink")
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise CheckpointError(f"{label} escapes the learner instance")
    return candidate


def _validate_transaction_manifest(root: Path, tx_dir: Path, manifest: dict[str, Any]) -> None:
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise CheckpointError("Fast Drill transaction files are missing")
    for entry in files.values():
        if not isinstance(entry, dict):
            raise CheckpointError("Fast Drill transaction entry is invalid")
        target = _safe_transaction_path(root, entry.get("path"), "transaction target")
        if entry["path"] not in _TRANSACTION_TARGETS:
            raise CheckpointError("Fast Drill transaction target is outside the canonical write set")
        stage = _safe_transaction_path(tx_dir, entry.get("stage"), "transaction stage")
        if stage.parent != tx_dir or stage.is_symlink() or not stage.is_file():
            raise CheckpointError("Fast Drill transaction stage is unsafe")
        if entry.get("kind") not in {"append", "replace"}:
            raise CheckpointError("Fast Drill transaction operation is unsupported")
        for hash_name in ("before_hash", "after_hash"):
            value = entry.get(hash_name)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise CheckpointError(f"Fast Drill transaction {hash_name} is invalid")
        if target.is_symlink():
            raise CheckpointError("Fast Drill transaction target is a symlink")


def _commit_transaction(root: Path, tx_dir: Path, manifest: dict[str, Any], crash_after: int | None = None) -> None:
    _validate_transaction_manifest(root, tx_dir, manifest)
    manifest["phase"] = "committing"
    _write_json_atomic(tx_dir / "transaction.json", manifest)
    applied = 0
    for name, entry in manifest["files"].items():
        path = root / entry["path"]
        current_hash = _sha256_file(path)
        if current_hash == entry["after_hash"]:
            continue
        if current_hash != entry["before_hash"]:
            raise CheckpointError(f"transaction conflict at {entry['path']}")
        if entry["kind"] == "append":
            suffix = (tx_dir / entry["stage"]).read_bytes()
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("ab") as handle:
                handle.write(suffix)
                handle.flush()
                os.fsync(handle.fileno())
            _fsync_directory(path.parent)
        elif entry["kind"] == "replace":
            _write_atomic(path, (tx_dir / entry["stage"]).read_bytes())
        else:
            raise CheckpointError(f"unknown transaction operation {entry['kind']!r}")
        applied += 1
        if crash_after is not None and applied >= crash_after:
            raise SimulatedCrash("synthetic crash during transactional reconciliation")
    manifest["phase"] = "committed"
    _write_json_atomic(tx_dir / "transaction.json", manifest)


def _finish_transaction(root: Path, tx_dir: Path, manifest: dict[str, Any]) -> None:
    active = checkpoint_path(root)
    if active.is_file() and sha256_bytes(active.read_bytes()) == manifest["checkpoint_digest"]:
        active.unlink()
        _fsync_directory(active.parent)
    shutil.rmtree(tx_dir)
    _fsync_directory(tx_dir.parent)


def _reconcile_transaction(root: Path, manifest: dict[str, Any], tx_dir: Path, crash_after: int | None = None) -> None:
    _commit_transaction(root, tx_dir, manifest, crash_after=crash_after)
    _finish_transaction(root, tx_dir, manifest)


def end_drill(
    apply: bool = False,
    repo_root: Path | str | None = None,
    *,
    crash_after: int | None = None,
) -> tuple[Reconciliation | None, int]:
    root = _root(repo_root)
    with transition_lock(root):
        return _end_drill_locked(apply=apply, repo_root=root, crash_after=crash_after)


def _end_drill_locked(
    apply: bool = False,
    repo_root: Path | str | None = None,
    *,
    crash_after: int | None = None,
) -> tuple[Reconciliation | None, int]:
    root = _root(repo_root)
    _require_learner_instance(root)
    transactions = _load_transactions(root)
    active = checkpoint_path(root)
    if not active.is_file():
        if not transactions:
            return None, 0
        if not apply:
            return None, 0
        for tx_dir, manifest in transactions:
            _reconcile_transaction(root, manifest, tx_dir, crash_after=crash_after)
        return None, 0
    checkpoint = load_checkpoint(root)
    if not checkpoint.records:
        raise CheckpointError("cannot end an empty checkpoint")
    if not apply:
        return build_reconciliation(root), 0
    matching = [
        (tx_dir, manifest)
        for tx_dir, manifest in transactions
        if manifest.get("checkpoint_digest") == checkpoint.digest()
    ]
    if matching:
        tx_dir, manifest = matching[0]
        _reconcile_transaction(root, manifest, tx_dir, crash_after=crash_after)
    else:
        reconciliation = build_reconciliation(root)
        manifest = _build_transaction(root, reconciliation, checkpoint)
        tx_dir = transaction_root(root) / manifest["transaction_id"]
        _reconcile_transaction(root, manifest, tx_dir, crash_after=crash_after)
    return reconciliation if "reconciliation" in locals() else None, 0


def _checkpoint_age_hours(checkpoint: Checkpoint) -> float | None:
    try:
        started = datetime.fromisoformat(str(checkpoint.metadata["started_at"]))
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - started).total_seconds() / 3600)
    except (TypeError, ValueError):
        return None


def recover_drill(
    repo_root: Path | str | None = None,
    *,
    apply: bool = False,
) -> tuple[dict[str, Any] | None, int]:
    root = _root(repo_root)
    with transition_lock(root):
        return _recover_drill_locked(root, apply=apply)


def _recover_drill_locked(
    repo_root: Path | str | None = None,
    *,
    apply: bool = False,
) -> tuple[dict[str, Any] | None, int]:
    root = _root(repo_root)
    _require_learner_instance(root)
    transactions = _load_transactions(root)
    if transactions:
        if apply:
            for tx_dir, manifest in transactions:
                _reconcile_transaction(root, manifest, tx_dir)
            return {"recommendation": "reconciled_transaction", "count": len(transactions)}, 0
        return {"recommendation": "resume_transaction", "count": len(transactions)}, 0
    if not checkpoint_path(root).is_file():
        return {"recommendation": "none", "count": 0}, 0
    checkpoint = load_checkpoint(root)
    age = _checkpoint_age_hours(checkpoint)
    recommendation = "resume" if age is not None and age <= RECOVERY_AGE_HOURS else "reconcile"
    return {
        "recommendation": recommendation,
        "session_id": checkpoint.metadata["session_id"],
        "entries": len(checkpoint.records),
        "age_hours": age,
    }, 0


def _print_reconciliation(value: Reconciliation) -> None:
    print(f"Session: {value.session_id}")
    print(f"Answer records: {len(value.records)}")
    print(f"Evidence records to reconcile: {len(value.evidence_items)}")
    print(f"Skills with conservative updates: {len(value.skill_updates)}")
    print("Question selection/routing is outside Fast Drill.")


def execute(operation: CheckpointOperation, repo_root: Path | str | None = None) -> int:
    root = _root(repo_root)
    try:
        if isinstance(operation, StartOperation):
            _start(operation, root)
            return 0
        if isinstance(operation, AppendAnswerOperation):
            _append(operation, root)
            return 0
        if isinstance(operation, EndOperation):
            proposal, code = end_drill(operation.apply, root)
            if proposal is not None and not operation.apply:
                _print_reconciliation(proposal)
            return code
        if isinstance(operation, RecoverOperation):
            report, code = recover_drill(root, apply=operation.apply)
            if report:
                print(json.dumps(report, sort_keys=True))
            return code
        raise CheckpointError(f"unsupported operation type: {type(operation).__name__}")
    except ModeRefused:
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--session-id", required=True)
    start.add_argument("--target-id", required=True)
    start.add_argument("--mode", default="normal")
    start.add_argument("--drill-type", default="retrieval_question")
    start.add_argument("--source-ref", default="")
    append = sub.add_parser("append")
    append.add_argument("--record-id")
    append.add_argument("--question-id", required=True)
    append.add_argument("--skill-id", required=True)
    append.add_argument("--concept", required=True)
    append.add_argument("--answer-summary", required=True)
    append.add_argument("--verdict", required=True, choices=[item.value for item in Verdict])
    append.add_argument("--correction-summary", default="")
    append.add_argument("--confidence", required=True, choices=[item.value for item in Confidence])
    append.add_argument("--evidence-marker", required=True)
    sub.add_parser("status")
    end = sub.add_parser("end")
    end.add_argument("--apply", action="store_true")
    recover = sub.add_parser("recover")
    recover.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            return execute(StartOperation(args.session_id, args.target_id, args.mode, args.drill_type, args.source_ref))
        if args.command == "append":
            return execute(AppendAnswerOperation(
                args.question_id, args.skill_id, args.concept, args.answer_summary,
                args.verdict, args.correction_summary, args.confidence,
                args.evidence_marker, args.record_id,
            ))
        if args.command == "status":
            if not is_drill_active():
                print("No active drill checkpoint.")
                return 0
            checkpoint = load_checkpoint()
            print(f"Active drill: {checkpoint.metadata['session_id']} ({len(checkpoint.records)} answers)")
            return 0
        if args.command == "end":
            return execute(EndOperation(args.apply))
        if args.command == "recover":
            return execute(RecoverOperation(args.apply))
    except CheckpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, ModeRefused) else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
