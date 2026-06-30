# Fast Drill Mode — StudyDD Speed Layer

> **Status:** design approved for implementation  
> **Scope:** repo-native optimization for active question drills  
> **Constraint:** no database, no daemon, no event bus  

## Purpose

Fast Drill Mode lets StudyDD run a dense sequence of retrieval questions without paying the full per-question cost of `compact_state.py`, `check_studydd.py`, and context-pack rebuilds. It is the default mode for active question drills when the learner profile enables it.

The key contract is: **canonical state may become stale during a drill, but evidence is never lossy.** Every answer leaves a cheap, durable, append-only trace before the agent moves on.

## When Fast Drill Mode Applies

Fast Drill Mode is appropriate when **all** of the following are true:

- The learner preference `fast_drill_mode` is `true`.
- The planned activity is a retrieval-question drill or spaced-repetition review drill.
- The session is not in recovery mode (recovery mode reads/explains, it does not test).
- No active checkpoint from a previous crashed drill is waiting for recovery.

It does **not** apply to:

- First session start / learner initialization.
- Practical labs, interview rehearsals, or presentation rehearsals.
- Deep-mode scenario exercises that require full context and audit.
- Any turn where a major state transition is detected (see below).

## Checkpoint File

A single active checkpoint file is the temporary source of truth:

```text
state/ACTIVE_DRILL_SESSION.md
```

This file is:

- **Instance-boundary** — learner-specific, empty in the public template.
- **Runtime-only** — regenerated at drill start, deleted at reconciliation.
- **Gitignored** — it must not be committed.
- **Append-only during the drill** — only new answer lines are appended.

Rationale for one file instead of a directory: fewer syscalls, trivial crash recovery, easy for agents and humans to inspect.

## Checkpoint Format

The checkpoint starts with a small YAML front matter block, followed by one NDJSON line per answer.

```markdown
---
session_id: "S-20260627-001"
target_id: "demo-ai-search-exam"
mode: "normal"
drill_type: "retrieval_question"
started_at: "2026-06-27T14:00:00+00:00"
source_ref: ""
---
{"ts":"2026-06-27T14:01:12+00:00","question_id":"Q-001","skill_id":"search-rag-basics","concept":"keyword vs vector search","answer_summary":"Correct distinction, no scenario","verdict":"partial","correction_summary":"Asked for concrete hybrid config","confidence":"medium","evidence_marker":"E-20260627-001"}
{"ts":"2026-06-27T14:03:44+00:00","question_id":"Q-002","skill_id":"search-rag-basics","concept":"hybrid retrieval config","answer_summary":"Index with text+vector fields","verdict":"correct","correction_summary":"","confidence":"medium","evidence_marker":"E-20260627-002"}
```

### Required fields per checkpoint line

| Field | Meaning |
|-------|---------|
| `ts` | ISO-8601 timestamp when the answer was graded |
| `question_id` | Session-local or global question ID |
| `skill_id` | Skill/concept being tested |
| `concept` | Short human-readable concept label |
| `answer_summary` | One-line summary of the learner's answer |
| `verdict` | `correct`, `partial`, `incorrect`, `unclear`, or `override` |
| `correction_summary` | Empty if no repair; otherwise the repair prompt/response summary |
| `confidence` | `high`, `medium`, or `low` |
| `evidence_marker` | Stable ID that will become the canonical evidence ID on reconciliation |

## Agent Rules During A Drill

1. **Start** the drill explicitly:
   ```bash
   python3 scripts/fast_drill_mode.py start \
     --session-id S-20260627-001 \
     --target-id demo-ai-search-exam \
     --mode normal \
     --drill-type retrieval_question
   ```
2. Ask exactly one question at a time; do not flood the chat.
3. After grading, **append one checkpoint line**:
   ```bash
   python3 scripts/fast_drill_mode.py append \
     --question-id Q-003 \
     --skill-id search-rag-basics \
     --concept "evaluating retrieval pipelines" \
     --answer-summary "Mentioned precision and recall" \
     --verdict correct \
     --confidence medium \
     --evidence-marker E-20260627-003
   ```
4. Do **not** run `compact_state.py`, `check_studydd.py`, or `build_context_pack.py` between questions.
5. Do **not** rewrite `state/EVIDENCE_LOG.md`, `state/SKILL_MAP.yaml`, `state/STUDY_STATE.yaml`, or `NEXT_ACTIONS.md` between questions.
6. Run targeted validation (`scripts/validate_touched_state.py`) **only** when a major transition is detected.
7. At session end, reconcile:
   ```bash
   python3 scripts/fast_drill_mode.py end --apply
   ```
8. After reconciliation, run the normal session-boundary pass:
   ```bash
   python3 scripts/compact_state.py
   python3 scripts/check_studydd.py
   ```

## Major State Transitions (Immediate Reconciliation)

Skip the fast path and reconcile immediately when any of the following happen during a drill:

- A skill moves from `weak` or `blocked` to `demonstrated`/`confirmed`.
- `current_readiness_estimate` or `readiness_confidence` changes materially (e.g., crosses 70 or a certification threshold).
- A source is promoted to `fresh`/`usable_for_questions: true` or demoted to `stale`/`unusable`.
- The validator reports a broken invariant, contradiction, or missing required file.
- The learner explicitly asks to end the drill or switch modes.

In these cases, run `scripts/fast_drill_mode.py end --apply` before continuing.

## Stale-State Contract

During a drill:

- `state/EVIDENCE_LOG.md`, `state/SKILL_MAP.yaml`, `state/STUDY_STATE.yaml`, and `NEXT_ACTIONS.md` may lag behind the learner's actual performance.
- `state/ACTIVE_DRILL_SESSION.md` is the temporary source of truth.
- The agent must still answer, grade, and explain from the checkpoint and its own context; it must not silently drop a graded answer.

After reconciliation:

- The checkpoint is deleted.
- Canonical state reflects all checkpoint lines.
- Derived summaries (`state/CURRENT_CONTEXT.md`, `state/EVIDENCE_INDEX.yaml`, `sessions/SESSION_SUMMARIES.md`) are rebuilt.

## Crash Recovery

If `state/ACTIVE_DRILL_SESSION.md` exists at agent startup, the agent must **not** start a new drill until the existing checkpoint is handled.

Recovery options, in order of preference:

1. **Resume** — if the session is recent (started within the last 4 hours) and the learner confirms, continue appending to the existing checkpoint.
2. **Reconcile** — if the learner is done or the session is older than 4 hours, run `end --apply` and let the canonical state catch up.
3. **Abort with audit** — if the checkpoint is corrupt or unrecoverable, log the event in `sessions/SESSION_LOG.md` and `state/EVIDENCE_LOG.md` as an abort, delete the checkpoint, and fall back to normal mode.

The 4-hour default is a practical heuristic, not a hard rule; the agent can adjust based on learner preference.

## Reconciliation Target Files

`scripts/fast_drill_mode.py end --apply` writes to:

- `state/EVIDENCE_LOG.md` — one evidence item per checkpoint line.
- `state/SKILL_MAP.yaml` — conservative readiness/status updates per skill.
- `state/STUDY_STATE.yaml` — active focus, session history, readiness estimate.
- `NEXT_ACTIONS.md` — one clear next action.

It does **not** rewrite raw audit logs or derived summaries directly; those are rebuilt by `compact_state.py` at the session boundary.

## Learner Preference Flags

Two flags in `state/LEARNER_PROFILE.yaml` control the mode:

```yaml
learner_preferences:
  fast_drill_mode: true
  auto_state_update_during_drills: true
```

- `fast_drill_mode` — enables the speed-layer behavior for question drills.
- `auto_state_update_during_drills` — when `true`, `end --apply` may write canonical state without a second confirmation; when `false`, the agent must show the reconciliation proposal and wait for learner confirmation.

Both are generic template defaults. Learner instances may override them.

## Script Interface

`scripts/fast_drill_mode.py` provides the low-level checkpoint operations. It is not an agent; it is a state helper.

```text
start    Create a new active checkpoint.
append   Append one graded-answer line.
status   Print whether a drill is active and how many answers are queued.
end      Reconcile the checkpoint. Use --apply to write canonical state.
recover  Inspect the active checkpoint and recommend resume/reconcile/abort.
```

Python API (for agent scripts and tests):

```python
from scripts.fast_drill_mode import start_drill, append_checkpoint, end_drill, load_checkpoint

start_drill(repo_root, session_id="S-001", target_id="demo", mode="normal", drill_type="retrieval_question")
append_checkpoint(repo_root, question_id="Q-1", skill_id="skill-1", concept="x", answer_summary="y", verdict="correct", correction_summary="", confidence="medium", evidence_marker="E-1")
proposal = end_drill(repo_root, apply=True)
```

## Minimalism Guardrails

The implementation must stay repo-native:

- No SQLite, no Redis, no external queue.
- No long-running process or daemon.
- No complex event bus.
- No new network dependencies.
- One active checkpoint per repo at a time.

If the design starts requiring any of the above, it has been overbuilt.

## Template vs Instance Boundary

- The public template keeps `fast_drill_mode: true` as a generic default and leaves `state/ACTIVE_DRILL_SESSION.md` absent.
- Learner instances populate their own checkpoint and skill map.
- The script refuses to reconcile an active checkpoint in template mode unless `--demo` is used for testing.

## Future Extensions (Out of Scope)

- Multi-session checkpoint history.
- Automatic mid-drill compaction.
- Per-skill checkpoint files.
- Real-time sync across devices.

These are intentionally excluded from the initial spec to preserve the "state can be stale, but not lossy" contract with minimal complexity.
