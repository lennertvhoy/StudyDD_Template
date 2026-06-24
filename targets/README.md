# Targets

`targets/` contains one folder per study target.

A target can be a certification, exam, interview loop, professional skill, course, or personal learning goal. Do not put the whole learner profile here; keep the live learner state in `state/`.

## Happy path

1. Create one folder with a stable lowercase ID, such as `targets/ai-103/` or `targets/networking-basics/`.
2. Add `TARGET.yaml` with the target title, goal, deadline, source policy, and success criteria.
3. Add target-specific skill notes only when they help the tutor choose or grade questions.
4. Keep readiness and evidence in `state/SKILL_MAP.yaml` and `state/EVIDENCE_LOG.md`.

## Target folder shape

```text
targets/<target-id>/
  TARGET.yaml
  SKILL_NOTES.md
```

The validator accepts an empty `targets/` folder for the public template. Once a real target folder exists, it should contain `TARGET.yaml`.
