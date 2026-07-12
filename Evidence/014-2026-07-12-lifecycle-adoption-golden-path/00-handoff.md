# Lifecycle adoption handoff

## Identity

- Base: `27e153d57226560a09c50294e97fea54cf31b71d` (`origin/main`).
- Branch: `agent/golden-path-studydd-lifecycle-adoption`.
- Final head: the pushed head containing this evidence and the final local gate;
  exact SHA is recorded by `git rev-parse HEAD` in the delivery handoff.
- No PR, CI dispatch/rerun, or merge was created.

## Contract and manifest

- Lifecycle format: `statedd.template-manifest/v2`.
- Template: `studydd`, release `0.10.0`, StateDD spec `statedd-template-v5`.
- Instance layout: `studydd.instance-layout/v1`.
- Source: `canonical_source`, `productionEligible: true`, canonical public
  StudyDD template remote, unresolved commit/tree metadata left null.
- Selected virtual modules: `studydd.core` → `studydd.activities` and
  `studydd.source-freshness` (the latter two depend on core).
- Deferred: `studydd.fast-drill`, `studydd.question-bank-engine`, and
  `studydd.integrations`; none is declared because its accepted implementation
  is not present on origin/main.
- Coverage: 30 exact assets, 12 owned trees, 290 current tracked paths, and
  278 origin/main paths. Every current tracked path resolves exactly once;
  exact/tree collisions, missing module assets, bad dependencies, private
  markers, and stale generated views fail validation.

## Ownership and compatibility

- `instance.yaml` is the small lifecycle descriptor for mode and source link.
- `.statedd/manifest.yaml` is template lifecycle authority; `.statedd/lock.yaml`
  is instance source identity/provenance authority.
- `state/STUDYDD_MODE.yaml`, `state/STUDYDD_TEMPLATE_VERSION.yaml`, and
  `state/STATE_MANIFEST.yaml` are deterministic compatibility views.
- `state/STATE_MANIFEST.template.yaml` and
  `state/STATE_MANIFEST.instance.yaml` are explicit fragment authorities.
- `state/LEARNER_PROFILE.yaml` remains instance-owned; no learner identity is
  seeded in the public template.
- No arbitrary recursive YAML merge or Markdown fragment composition was added.

## Validation and proof

- `python3 scripts/check_studydd.py` — pass.
- `python3 scripts/validate_manifest.py` — pass.
- `python3 scripts/test_instance_layout_contract.py` — pass.
- `python3 scripts/test_compatibility_views.py` — pass.
- `python3 scripts/test_create_instance.py` — pass, including regeneration
  idempotence and source immutability.
- `PYTHONDONTWRITEBYTECODE=1 STATEPORT_ROOT=<StatePort checkout> python3
  scripts/test_lifecycle_adoption.py` — pass.
- `python3 scripts/agent_privacy_check.py` — soft pass with only known scanner
  self-match warnings; no credential or learner-content finding.

The golden-path proof used only synthetic placeholders in a temporary workspace.
It did not inspect or copy private canary content.

## Integrated commits

- Layout: `f025b8b74bae890179de2b7b95e128b7a1f19d54`.
- Manifest/coverage: `0dc1dc625159d612edfbac5e5d8a20df5f1a1f20`.
- Ownership: `871cede3891fa5e75512ea2ec599830959bdb875`.
- Instantiation: `8f02e412ea82ce7c5b65b05071620c610905affe`.
- Privacy/conflict review: `13a1502cc108c5005c7547b46c029248436dc066`.

The StatePort parser/CLI is consumed as an external authority; no StatePort
engine was copied into StudyDD.
