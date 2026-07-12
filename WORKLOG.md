# StudyDD Worklog

## 2026-07-12 — bounded question-bank schema boundary

- Added a generic typed `studydd.question-bank/v1` envelope and linter checks
  for stable IDs, structured provenance, duplicate `(bank_id, question_id)`
  identity, and learner-state exclusion at the import/export boundary.
- Classified `question_banks/**` as an empty-in-template, private instance tree
  and kept `studydd.question-bank-engine` unselected.
- Added synthetic temporary tests only; no learner data or bank fixture was
  added. Import/export, materialisation, and runtime module selection remain
  deferred.

## 2026-07-12 — GOLDEN-PATH-MEGA-001 lifecycle adoption

- Adopted the external StateDD Lifecycle Manifest v2 boundary without copying
  StatePort's lifecycle engine into StudyDD.
- Added the truthful instance-layout contract, virtual core/activities/source-
  freshness modules, complete current tracked-path coverage, explicit mixed-
  ownership authorities, deterministic compatibility views, and a bootstrap
  lock/provenance path.
- Proved canonical validation, synthetic bootstrap creation, instance-owned
  mutation preservation, idempotent regeneration, StatePort classification, and
  source immutability in a temporary workspace.
- Remote CI was intentionally not triggered; no PR or merge was created.

Known limits remain Git source resolution, registry access, upgrade planning and
apply, schema migration, retirement, and production runtime acceptance.
