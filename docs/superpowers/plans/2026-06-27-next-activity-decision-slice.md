# StudyDD Next-Activity Decision Slice — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `scripts/plan_learning_activity.py` recommend among exam-style question, spaced-repetition review, lab/practical exercise, diagram/visual explanation, and recent-info check using protocol-driven, auditable rules.

**Architecture:** Extend the existing activity planner with small helper functions that inspect the active target (`TARGET.yaml`), study skill, recent activities, and review state. Keep the decision tree as simple if/elif branches that print the triggering rule. Add the new `recent_info_check` activity type to `activities/ACTIVITY_TEMPLATES.yaml`, update protocols and docs, and cover the rules with tests on temporary learner instances.

**Tech Stack:** Python 3.10+, PyYAML, existing StudyDD scripts.

---

## File structure

| File | Responsibility |
|------|----------------|
| `activities/ACTIVITY_TEMPLATES.yaml` | Declares the new `recent_info_check` activity type and a `source_freshness_check` template. |
| `scripts/plan_learning_activity.py` | Loads active target, inspects volatility/study skill/recent activity, and routes to one of the five activity categories with an auditable reason. |
| `protocols/SELECT_NEXT_ACTION.md` | Documents the activity-type routing rules and references the script/templates. |
| `protocols/LEARNING_ACTIVITY_POLICY.md` | Mentions `recent_info_check` and volatile-topic routing. |
| `scripts/test_learning_activities.py` | Adds tests for the new routing behavior. |
| `README.md` | Adds a short "How the agent chooses the next activity" section. |
| `NEXT_ACTIONS.md` | Records this slice as completed and sets the next recommended slice. |

---

### Task 1: Add `recent_info_check` activity type and template

**Files:**
- Modify: `activities/ACTIVITY_TEMPLATES.yaml`

- [ ] **Step 1: Add `recent_info_check` to `activity_types`**

Insert after `retrieval_question`:

```yaml
recent_info_check:
  description: "Verify current facts, sources, or exam objectives for a volatile topic before authoritative study."
```

- [ ] **Step 2: Add `source_freshness_check` template**

Insert at the end of the `templates` list:

```yaml
- id: source_freshness_check
  activity_type: recent_info_check
  best_for:
    - volatile_topic
    - it_certification
    - live_topic
  expected_evidence:
    - source_metadata
    - short_summary
    - answer_to_check_question
```

- [ ] **Step 3: Run activity-template test to confirm parsing**

Run:

```bash
python3 scripts/test_learning_activities.py
```

Expected: existing tests still pass; `test_activity_templates_parse` covers the new type because it only checks required types.

- [ ] **Step 4: Commit**

```bash
git add activities/ACTIVITY_TEMPLATES.yaml
git commit -m "feat: add recent_info_check activity type and source_freshness_check template"
```

---

### Task 2: Add target loading and decision helpers

**Files:**
- Modify: `scripts/plan_learning_activity.py`

- [ ] **Step 1: Add constants for target and source paths**

After `MODE_PATH = ROOT / "state" / "STUDYDD_MODE.yaml"`, add:

```python
TARGETS_DIR = ROOT / "targets"
SOURCES_STATE_PATH = ROOT / "sources" / "SOURCE_STATE.yaml"
```

- [ ] **Step 2: Add helper to load active target metadata**

Insert before `count_due_reviews`:

```python
def load_active_target(active_target_id: str | None) -> dict[str, Any]:
    """Load TARGET.yaml for the active target, if any."""
    if not active_target_id:
        return {}
    target_path = TARGETS_DIR / active_target_id / "TARGET.yaml"
    if not target_path.is_file():
        return {}
    try:
        return load_yaml(target_path)
    except Exception:
        return {}
```

- [ ] **Step 3: Add volatility helper**

```python
VOLATILE_CLASSES = {"moderate", "volatile", "live"}


def target_is_volatile(target: dict[str, Any]) -> bool:
    volatility = target.get("volatility") or "moderate"
    return volatility in VOLATILE_CLASSES
```

- [ ] **Step 4: Add recent-activity-type helper**

```python
def recent_activity_types(activity_state: dict[str, Any], limit: int = 5) -> list[str]:
    recent = activity_state.get("recent_activities") or []
    return [a.get("type") for a in recent[:limit] if a.get("type")]
```

- [ ] **Step 5: Add study-skill → activity-type matcher**

```python
def activity_types_for_study_skill(
    study_skill: str | None,
    templates: list[dict[str, Any]],
) -> list[str]:
    """Return activity types whose templates list this study skill in best_for."""
    if not study_skill:
        return []
    matched: set[str] = set()
    for template in templates:
        best_for = template.get("best_for") or []
        if study_skill in best_for or "conceptual_understanding" in best_for:
            matched.add(template.get("activity_type"))
    return list(matched)
```

- [ ] **Step 6: Commit**

```bash
git add scripts/plan_learning_activity.py
git commit -m "feat: add target loading and decision helpers to activity planner"
```

---

### Task 3: Update `choose_activity_type` routing

**Files:**
- Modify: `scripts/plan_learning_activity.py`

- [ ] **Step 1: Update `choose_activity_type` signature**

Change:

```python
def choose_activity_type(
    skill_id: str | None,
    due_reviews: int,
    weakest_skill: dict[str, Any] | None,
    low_energy: bool,
) -> tuple[str, str, list[str]]:
```

To:

```python
def choose_activity_type(
    skill_id: str | None,
    due_reviews: int,
    weakest_skill: dict[str, Any] | None,
    low_energy: bool,
    target: dict[str, Any] | None,
    study_skill: str | None,
    recent_types: list[str],
    templates: list[dict[str, Any]],
) -> tuple[str, str, list[str]]:
```

- [ ] **Step 2: Replace the body with the five-category routing**

Replace the entire body of `choose_activity_type` with:

```python
    target = target or {}
    target_type = target.get("type") or ""
    target_volatile = target_is_volatile(target)
    recent_set = set(recent_types)
    matched_types = activity_types_for_study_skill(study_skill, templates)

    # 1. Spaced repetition is the highest-priority learning debt.
    if due_reviews > 0:
        return (
            "spaced_review",
            f"Rule: review-first doctrine — {due_reviews} due review item{'s' if due_reviews != 1 else ''}.",
            ["typed_answer", "transcript", "screenshot"],
        )

    # 2. Recent-info check for volatile topics before authoritative questions.
    if target_volatile and "recent_info_check" not in recent_set:
        return (
            "recent_info_check",
            "Rule: volatile target with no recent source check — verify freshness before an authoritative question.",
            ["source_metadata", "short_summary", "answer_to_check_question"],
        )

    # 3. Lab / practical exercise when the domain fits.
    if "practical_lab" in matched_types or study_skill in {"practical_lab", "sysadmin", "cloud", "networking"}:
        if "practical_lab" not in recent_set:
            return (
                "practical_lab",
                f"Rule: study skill '{study_skill}' is hands-on — a lab produces stronger evidence than a chat question.",
                ["screenshot", "command_output", "explanation"],
            )

    # 4. Diagram / visual explanation for conceptual domains.
    if "diagram_or_whiteboard" in matched_types or study_skill in {"philosophy", "conceptual_understanding"}:
        if "diagram_or_whiteboard" not in recent_set:
            return (
                "diagram_or_whiteboard",
                f"Rule: study skill '{study_skill}' benefits from visual explanation — draw the model before defending it.",
                ["whiteboard_diagram", "photo"],
            )

    # 5. Exam-style question for certification/exam targets with practiced+ skills.
    if target_type in {"certification", "exam"}:
        skill_ready = weakest_skill is None or int(weakest_skill.get("readiness") or 0) >= 40
        if skill_ready and "retrieval_question" not in recent_set:
            return (
                "retrieval_question",
                f"Rule: certification target '{target.get('title') or target_type}' — use an exam-style question.",
                ["typed_answer"],
            )

    if weakest_skill is not None and weakest_skill.get("status") == "weak":
        return (
            "paper_exercise",
            f"Rule: skill '{weakest_skill.get('label') or weakest_skill.get('id')}' is weak — a written exercise surfaces hidden gaps.",
            ["photo", "typed_answers"],
        )

    if weakest_skill is not None and weakest_skill.get("status") == "blocked":
        return (
            "explain_back",
            f"Rule: skill '{weakest_skill.get('label') or weakest_skill.get('id')}' is blocked — explain it back to repair the confusion.",
            ["written_explanation", "transcript"],
        )

    if low_energy:
        return (
            "explain_back",
            "Rule: low-energy mode — short explain-back task keeps the session small.",
            ["written_explanation"],
        )

    if skill_id:
        return (
            "retrieval_question",
            f"Rule: focusing on skill '{skill_id}' — one targeted question is the fastest next move.",
            ["typed_answer"],
        )

    return (
        "retrieval_question",
        "Rule: no stronger signal — start with one focused question.",
        ["typed_answer"],
    )
```

- [ ] **Step 3: Update callers of `choose_activity_type`**

In `plan_activity`, after loading data, add:

```python
    target = load_active_target(active_target_id)
    study_skill = target.get("study_skill") or ""
    recent_types = recent_activity_types(activity_state)
    templates = templates_data.get("templates") or []
```

And update the call:

```python
    activity_type, reason, expected_evidence = choose_activity_type(
        skill_id,
        due_reviews,
        weakest_skill,
        low_energy,
        target,
        study_skill,
        recent_types,
        templates,
    )
```

- [ ] **Step 4: Update task description mapping for `recent_info_check`**

In the `task_description` dict, add:

```python
        "recent_info_check": "Check the freshness of the relevant source, then answer the check question or summarize what changed.",
```

- [ ] **Step 5: Run the planner demo**

Run:

```bash
python3 scripts/plan_learning_activity.py --demo
```

Expected: output still contains all required sections.

- [ ] **Step 6: Commit**

```bash
git add scripts/plan_learning_activity.py
git commit -m "feat: route next activity among five categories with auditable rules"
```

---

### Task 4: Update `protocols/SELECT_NEXT_ACTION.md`

**Files:**
- Modify: `protocols/SELECT_NEXT_ACTION.md`

- [ ] **Step 1: Add Activity-type routing subsection**

Insert after the existing "## Selection Priority" section, before "## Override Handling":

```markdown
## Activity-type routing

After applying the selection priority above, use `scripts/plan_learning_activity.py` to choose one of the five canonical activity categories. The script prints the rule that triggered the choice so the recommendation is auditable.

1. **Spaced-repetition review** (`spaced_review`) — due or overdue reviews first.
2. **Recent-info check** (`recent_info_check`) — if the active target is `moderate`/`volatile`/`live` and no recent source check is recorded.
3. **Lab / practical exercise** (`practical_lab`) — if the active study skill is `practical_lab`, `sysadmin`, `cloud`, or `networking`.
4. **Diagram / visual explanation** (`diagram_or_whiteboard`) — if the active study skill is `philosophy` or `conceptual_understanding`.
5. **Exam-style question** (`retrieval_question`) — if the target `type` is `certification` or `exam` and the skill is at least practiced (`readiness >= 40`).
6. **Fallback** — focused retrieval question, paper exercise, or explain-back based on skill status.

The learner can accept, modify, or override the recommendation. Strong overrides are recorded in `state/EVIDENCE_LOG.md` and `activities/ACTIVITY_LOG.md`.
```

- [ ] **Step 2: Commit**

```bash
git add protocols/SELECT_NEXT_ACTION.md
git commit -m "docs: document five-category activity routing in SELECT_NEXT_ACTION"
```

---

### Task 5: Update `protocols/LEARNING_ACTIVITY_POLICY.md`

**Files:**
- Modify: `protocols/LEARNING_ACTIVITY_POLICY.md`

- [ ] **Step 1: Mention `recent_info_check` in supported activities**

In the list under "## Inputs the agent must consider" or add a short note after the first paragraph:

```markdown
When a target is volatile or the active source is stale, the agent may recommend a `recent_info_check` activity. The learner verifies current facts, sources, or exam objectives and submits source metadata or a short summary before the agent builds authoritative questions.
```

- [ ] **Step 2: Commit**

```bash
git add protocols/LEARNING_ACTIVITY_POLICY.md
git commit -m "docs: mention recent_info_check in learning activity policy"
```

---

### Task 6: Add tests for the new routing

**Files:**
- Modify: `scripts/test_learning_activities.py`

- [ ] **Step 1: Add `recent_info_check` to required activity types**

Update `REQUIRED_ACTIVITY_TYPES` to include `"recent_info_check"`.

- [ ] **Step 2: Add test for new activity type exists**

```python
def test_recent_info_check_activity_type_exists() -> None:
    data = load_yaml(ROOT / "activities" / "ACTIVITY_TEMPLATES.yaml")
    activity_types = data.get("activity_types") or {}
    assert "recent_info_check" in activity_types, "recent_info_check activity type must exist"
    templates = data.get("templates") or []
    assert any(
        t.get("id") == "source_freshness_check" and t.get("activity_type") == "recent_info_check"
        for t in templates
    ), "source_freshness_check template must exist"
```

- [ ] **Step 3: Add test for volatile target routes to recent_info_check**

Use a temporary instance. Add:

```python
def test_plan_recommends_recent_info_check_for_volatile_target() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-volatile-test-") as tmp:
        target = Path(tmp) / "StudyDD_VolatileTest"
        remote = "https://github.com/example/StudyDD_VolatileTest.git"
        run([sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote])

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = load_yaml(mode_path)
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        save_yaml(mode_path, mode_data)

        study_state = load_yaml(target / "state" / "STUDY_STATE.yaml")
        study_state["learner"]["name"] = "Volatile Test Learner"
        study_state["active_target_id"] = "volatile-target"
        save_yaml(target / "state" / "STUDY_STATE.yaml", study_state)

        (target / "targets" / "volatile-target").mkdir(parents=True, exist_ok=True)
        (target / "targets" / "volatile-target" / "TARGET.yaml").write_text(
            "---\nid: volatile-target\ntype: certification\ntitle: Volatile Cert\nvolatility: volatile\nstudy_skill: it_certification\n",
            encoding="utf-8",
        )

        result = run([sys.executable, "scripts/plan_learning_activity.py"], cwd=target)
        assert "recent_info_check" in result.stdout, "Volatile target should route to recent_info_check"
        assert "Rule: volatile target" in result.stdout, "Reason should reference the volatility rule"
```

- [ ] **Step 4: Add test for practical-lab routing**

```python
def test_plan_recommends_lab_for_practical_skill() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-lab-test-") as tmp:
        target = Path(tmp) / "StudyDD_LabTest"
        remote = "https://github.com/example/StudyDD_LabTest.git"
        run([sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote])

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = load_yaml(mode_path)
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        save_yaml(mode_path, mode_data)

        study_state = load_yaml(target / "state" / "STUDY_STATE.yaml")
        study_state["learner"]["name"] = "Lab Test Learner"
        study_state["active_target_id"] = "lab-target"
        save_yaml(target / "state" / "STUDY_STATE.yaml", study_state)

        (target / "targets" / "lab-target").mkdir(parents=True, exist_ok=True)
        (target / "targets" / "lab-target" / "TARGET.yaml").write_text(
            "---\nid: lab-target\ntype: skill\ntitle: Lab Target\nstudy_skill: practical_lab\n",
            encoding="utf-8",
        )

        result = run([sys.executable, "scripts/plan_learning_activity.py"], cwd=target)
        assert "practical_lab" in result.stdout, "practical_lab study skill should route to practical_lab"
```

- [ ] **Step 5: Add test for diagram routing**

```python
def test_plan_recommends_diagram_for_conceptual_skill() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-diagram-test-") as tmp:
        target = Path(tmp) / "StudyDD_DiagramTest"
        remote = "https://github.com/example/StudyDD_DiagramTest.git"
        run([sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote])

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = load_yaml(mode_path)
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        save_yaml(mode_path, mode_data)

        study_state = load_yaml(target / "state" / "STUDY_STATE.yaml")
        study_state["learner"]["name"] = "Diagram Test Learner"
        study_state["active_target_id"] = "diagram-target"
        save_yaml(target / "state" / "STUDY_STATE.yaml", study_state)

        (target / "targets" / "diagram-target").mkdir(parents=True, exist_ok=True)
        (target / "targets" / "diagram-target" / "TARGET.yaml").write_text(
            "---\nid: diagram-target\ntype: skill\ntitle: Diagram Target\nstudy_skill: philosophy\n",
            encoding="utf-8",
        )

        result = run([sys.executable, "scripts/plan_learning_activity.py"], cwd=target)
        assert "diagram_or_whiteboard" in result.stdout, "philosophy study skill should route to diagram_or_whiteboard"
```

- [ ] **Step 6: Add test for exam-style question routing**

```python
def test_plan_recommends_exam_question_for_certification_target() -> None:
    with tempfile.TemporaryDirectory(prefix="studydd-exam-test-") as tmp:
        target = Path(tmp) / "StudyDD_ExamTest"
        remote = "https://github.com/example/StudyDD_ExamTest.git"
        run([sys.executable, "scripts/create_instance.py", "--target", str(target), "--remote", remote])

        mode_path = target / "state" / "STUDYDD_MODE.yaml"
        mode_data = load_yaml(mode_path)
        mode_data["mode"] = "learner_instance"
        mode_data["personalized"] = True
        save_yaml(mode_path, mode_data)

        study_state = load_yaml(target / "state" / "STUDY_STATE.yaml")
        study_state["learner"]["name"] = "Exam Test Learner"
        study_state["active_target_id"] = "exam-target"
        save_yaml(target / "state" / "STUDY_STATE.yaml", study_state)

        (target / "targets" / "exam-target").mkdir(parents=True, exist_ok=True)
        (target / "targets" / "exam-target" / "TARGET.yaml").write_text(
            "---\nid: exam-target\ntype: certification\ntitle: Exam Target\nstudy_skill: it_certification\n",
            encoding="utf-8",
        )

        # Add a practiced skill so the exam-style branch fires.
        skill_map = load_yaml(target / "state" / "SKILL_MAP.yaml")
        skill_map["skills"] = [
            {
                "id": "exam-skill",
                "label": "Exam skill",
                "status": "practiced",
                "readiness": 55,
                "confidence": "medium",
                "evidence": [],
            }
        ]
        save_yaml(target / "state" / "SKILL_MAP.yaml", skill_map)

        result = run([sys.executable, "scripts/plan_learning_activity.py"], cwd=target)
        assert "retrieval_question" in result.stdout, "Certification target should route to exam-style retrieval question"
        assert "exam-style" in result.stdout.lower() or "certification target" in result.stdout, "Reason should mention exam/certification"
```

- [ ] **Step 7: Register new tests in `main()`**

Add the new test functions to the `tests` list in `main()`.

- [ ] **Step 8: Run tests**

```bash
python3 scripts/test_learning_activities.py
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add scripts/test_learning_activities.py
git commit -m "test: cover five-category next-activity routing"
```

---

### Task 7: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add "How the agent chooses the next activity" section**

Insert after the "### Spaced repetition by default" section (or near the learning-activities paragraph):

```markdown
### How the agent chooses the next activity

StudyDD recommends one activity at a time using protocol-driven rules:

1. **Due reviews first** — spaced retrieval is the highest-retention move.
2. **Recent-info check** — for `moderate`, `volatile`, or `live` topics without a recent source check.
3. **Lab or diagram** — when the study skill is hands-on (`practical_lab`, `cloud`, `sysadmin`, `networking`) or conceptual (`philosophy`, `conceptual_understanding`).
4. **Exam-style question** — when the target is a certification or exam and the skill is practiced.
5. **Fallback question** — a focused retrieval question, paper exercise, or explain-back.

The agent explains which rule triggered the recommendation. The learner can accept, modify, or override it.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: explain how StudyDD chooses the next activity"
```

---

### Task 8: Run validation

**Files:** none

- [ ] **Step 1: Run full validator**

```bash
python3 scripts/check_studydd.py
```

Expected: passes.

- [ ] **Step 2: Run learning-activities tests**

```bash
python3 scripts/test_learning_activities.py
```

Expected: all tests pass.

- [ ] **Step 3: Run planner demo**

```bash
python3 scripts/plan_learning_activity.py --demo
```

Expected: clean output with all required sections.

- [ ] **Step 4: Run other CI tests**

```bash
python3 scripts/test_instantiate_template.py
python3 scripts/test_study_loop_smoke.py
python3 scripts/test_compact_state.py
python3 scripts/test_context_pack.py
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git commit -m "chore: validate next-activity decision slice" --allow-empty
```

---

### Task 9: Update `NEXT_ACTIONS.md`

**Files:**
- Modify: `NEXT_ACTIONS.md`

- [ ] **Step 1: Move current action to recently completed and add next slice**

Rewrite `NEXT_ACTIONS.md` to:

```markdown
# NEXT_ACTIONS — Active Queue

> **Agent-maintained.** This is the single canonical next-action file for the repo.

## Current next action

1. Wire the active activity recommendation reason into `scripts/build_context_pack.py` and add a focused `scripts/test_next_activity_decision.py` for the decision rules.

## Pending actions

- Run `python3 scripts/check_studydd.py` after initialization or any state change.
- Add weak or uncertain skills to `reviews/REVIEW_QUEUE.md` after evidence exists.

## Recently completed

- 2026-06-27: Improved next-activity selection to recommend among exam-style question, spaced-repetition review, lab/practical exercise, diagram/visual explanation, and recent-info check.
```

- [ ] **Step 2: Commit**

```bash
git add NEXT_ACTIONS.md
git commit -m "docs: update NEXT_ACTIONS after next-activity slice"
```

---

### Task 10: Final push (if green)

**Files:** none

- [ ] **Step 1: Run final validation**

```bash
python3 scripts/check_studydd.py
python3 scripts/test_learning_activities.py
```

- [ ] **Step 2: Push if green and user has authorized**

```bash
git push origin main
```

Only push after explicit user approval.

---

## Spec coverage check

| Spec section | Task |
|--------------|------|
| Add `recent_info_check` activity type | Task 1 |
| Extend `plan_learning_activity.py` | Tasks 2–3 |
| Update `SELECT_NEXT_ACTION.md` | Task 4 |
| Update `LEARNING_ACTIVITY_POLICY.md` | Task 5 |
| Add tests | Task 6 |
| Update `README.md` | Task 7 |
| Run validation | Task 8 |
| Update `NEXT_ACTIONS.md` | Task 9 |
| Public-safety / template-safety | All tasks use generic data; tests use temp instances. |

## Placeholder scan

No placeholders. Every step includes exact file paths, code blocks, and commands.
