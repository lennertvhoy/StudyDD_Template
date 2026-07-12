# Dirty-path ownership classification

This classifies every path that was modified or untracked before preservation.
All paths were retained because they are generic and attributable to the
recovered hardening work. No unknown or learner-owned file was staged.

| Path | Recovered ownership | Preservation assessment |
|---|---|---|
| `.github/workflows/validate.yml` | TH-02 | Adds focused regression discovery; preserve WIP. |
| `AGENTS.md` | TH-01 | Documents template-engineering planning split; shared integration hotspot. |
| `EXAMPLES/python-fundamentals/targets/python-fundamentals/questions/Q-PY-003.yaml` | TH-02 question quality | Generic answer-key wording adjustment; preserve WIP. |
| `NEXT_ACTIONS.md` | TH-01 | Restores learner-instance seed semantics; shared integration hotspot. |
| `README.md` | TH-01 | Documents template learner-command refusal and template backlog. |
| `docs/question-bank-schema.md` | TH-02 question quality | Documents target scope and ambiguity metadata. |
| `docs/superpowers/specs/FAST_DRILL_MODE.md` | TH-02 fast-drill extension | Documents scope, ambiguity, and evidence fields. |
| `protocols/INSTANTIATE_TEMPLATE.md` | TH-01 | Documents refusal route and template-only backlog. |
| `protocols/QUESTION_QUALITY.md` | TH-02 question quality | Adds target ownership, ambiguity, and length-bias rules. |
| `protocols/SCHEDULE_REVIEW.md` | TH-02 | Resolves zero-day versus positive-duration contradiction. |
| `protocols/STATE_WRITE_POLICY.md` | TH-02 | Documents canonical targeted validation contract. |
| `protocols/TEMPLATE_INSTANCE_BOUNDARY.md` | TH-01 | Documents executable mode boundary. |
| `protocols/UPDATE_STATE.md` | TH-02 | Documents operation-scoped targeted validation. |
| `scripts/agent_preflight.py` | TH-01 | Reads the template backlog in template mode. |
| `scripts/build_context_pack.py` | TH-01 | Refuses learner context generation in template mode. |
| `scripts/check_studydd.py` | TH-01 plus compatibility repair | Requires template backlog and contains a small regex-name repair. |
| `scripts/compact_state.py` | TH-02 | Atomic writes and canonical evidence metadata parsing. |
| `scripts/create_instance.py` | TH-01 | Exact mode/remote guard and template-backlog exclusion. |
| `scripts/fast_drill_mode.py` | TH-01 and TH-02 | Mode guard, atomic writes, target scope, ambiguity, duplicate protection. |
| `scripts/lint_questions.py` | TH-02 question quality | Validates target scope/ambiguity and warns on option-length bias. |
| `scripts/plan_learning_activity.py` | TH-01 and TH-02 | Mode refusal and atomic state writing. |
| `scripts/plan_state_update.py` | TH-01 | Refuses learner planning in template mode. |
| `scripts/record_activity_result.py` | TH-01 and TH-02 | Mode refusal, preflighted review scheduling, atomic writes, exact evidence link. |
| `scripts/record_source_check.py` | TH-01 and TH-02 | Mode refusal and atomic source-state writing; PR #4 overlap. |
| `scripts/schedule_review.py` | TH-01 and TH-02 | Mode refusal, idempotency, positive learning steps, atomic writes. |
| `scripts/select_next_study_action.py` | TH-01 and TH-02 | Mode refusal and read-only due classification. |
| `scripts/test_compact_state.py` | TH-02 | Covers ambiguity/readiness metadata compaction. |
| `scripts/test_context_pack.py` | TH-01 | Covers template-mode refusal. |
| `scripts/test_fast_drill_mode.py` | TH-02 | Covers target scope, ambiguity, and duplicate markers. |
| `scripts/test_learning_activities.py` | TH-01 and TH-02 | Covers refusal, evidence links, and time-hermetic freshness. |
| `scripts/test_question_quality.py` | TH-02 question quality | Covers target scope, ambiguity, and length bias. |
| `scripts/test_record_source_check.py` | TH-02 compatibility | Makes freshness assertions time-hermetic; PR #4 overlap. |
| `scripts/validate_touched_state.py` | TH-02 | Canonical fast-path validator and exact cross-ID checks. |
| `state/STATE_MANIFEST.yaml` | TH-01 planning/closure policy | Adds template backlog and prose closure policy to runtime manifest v1; lifecycle integration hotspot. |
| `state/STUDY_BACKLOG.md` | TH-01 | Restores generic learner-seed backlog. |
| `TEMPLATE_BACKLOG.md` | TH program state | New template-engineering queue and WIP status record. |
| `docs/superpowers/plans/2026-07-10-core-safety-foundation.md` | TH design | Approved phased implementation plan; includes later work only as plans. |
| `docs/superpowers/specs/2026-07-10-transactional-hardening-program.md` | TH design | Program architecture, dependencies, and invariants. |
| `scripts/mode_guard.py` | TH-01 | Thin CLI compatibility adapter around `studydd.mode`. |
| `scripts/test_fast_path_integrity.py` | TH-02 | Focused regression suite for the recovered defects. |
| `scripts/test_mode_guards.py` | TH-01 | Focused mode/remote and no-write regression suite. |
| `studydd/__init__.py` | TH-01/TH-02 package seed | Exposes shared generic helpers. |
| `studydd/atomic.py` | TH-02 | Standard-library atomic text replacement helper. |
| `studydd/mode.py` | TH-01 | Canonical mode/remote validation contract. |

## Classification summary

- Fast-drill integration: existing committed base plus seven dirty extensions
  across code, docs, examples, and tests.
- Source-check completion: existing committed behavior; two dirty compatibility
  and test overlaps, not a wholesale PR #4 copy.
- Repository safety/remediation: the dominant dirty objective (`TH-01` and
  `TH-02`).
- Generic lived-instance lessons: represented only as public-safe invariants,
  synthetic fixtures, and tests.
- Unrelated or pre-existing dirty work: none located.
- Unknown dirty work: none located.
