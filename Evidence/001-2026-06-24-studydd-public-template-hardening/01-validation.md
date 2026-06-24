# Validator Output

Command: `python3 scripts/check_studydd.py`

```text
StudyDD validation
==================

All required files present.
YAML validation passed.
No forbidden mentions found.
StudyDD state looks healthy.
```

Result: **PASS**

New checks exercised:

- `state/STUDYDD_TEMPLATE_VERSION.yaml` required and parsed.
- Cross-file evidence references (skills, reviews, sessions) validated.
- Review skill IDs validated against `state/SKILL_MAP.yaml`.
- Active question ID consistency between `state/STUDY_STATE.yaml` and `NEXT_ACTIONS.md`.
- `demonstrated` status requires evidence; readiness ≥ 70 requires evidence.
- Answer-key leakage heuristic on learner-facing target surfaces.
- Optional question-bank schema validation.
