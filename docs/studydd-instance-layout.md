# StudyDD instance layout contract

The machine-readable contract is [`contracts/studydd.instance-layout.yaml`](../contracts/studydd.instance-layout.yaml). Its stable ID is `studydd.instance-layout/v1`.

It describes the existing StudyDD template/instance boundary without changing the repository tree. The three supported mode markers are `template`, `bootstrap`, and `learner_instance`, read from `state/STUDYDD_MODE.yaml`.

## Authority boundary

- Generic scripts, protocols, prompts, study skills, documentation, workflow files, and activity templates are template assets.
- Learner state, next actions, activity history, and learner-created trees are instance-owned. Their generic placeholders in the public template do not make learner data public.
- Compact context, evidence indexes, session summaries, and context packs are generated views. Their declared generators and inputs are the surfaces to edit.
- `state/STUDYDD_MODE.yaml`, `state/STUDYDD_TEMPLATE_VERSION.yaml`, and the domain `state/STATE_MANIFEST.yaml` are compatibility metadata. The latter remains a runtime loading manifest, not a StatePort lifecycle manifest.

`scripts/validate_manifest.py` now proves that every currently tracked path is classified exactly once, that exact assets and owned trees do not collide, that module assets and self-tests resolve, and that generated compatibility views are reproducible. A consumer must not infer permission to overwrite a path from its directory name alone.

## Source link and lock boundary

The public template records `template_remote` in `state/STUDYDD_MODE.yaml`. A copied instance records the same source as `template_origin`, and `.statedd/lock.yaml` records the local source digest, version, and creation provenance. `state/STUDYDD_MODE.yaml`, `state/STUDYDD_TEMPLATE_VERSION.yaml`, and `state/STATE_MANIFEST.yaml` remain generated compatibility views.

## Validator mapping

Run:

```bash
python3 scripts/check_studydd.py
```

The entry point validates the contract's presence and shape and maps mode, template-version, selected dynamic-tree, and generated-view checks. Run `python3 scripts/validate_manifest.py` for lifecycle ownership coverage and StatePort-compatible manifest checks. `python3 scripts/test_instance_layout_contract.py` exercises the contract hook and malformed-contract failures.

## Privacy

Template mode is public-safe. Bootstrap requires review. Learner-instance data is private by default: names, targets, answers, evidence, sessions, reviews, source notes, and local extensions must not be copied back into this public template. Secrets and credentials are never valid repository content.

## Limitations

This contract does not implement Git source resolution, registry access, upgrade application, transactional migration, or retirement. Optional instance trees may not exist until initialization, but the manifest declares their ownership prefixes and the coverage validator rejects ambiguous tracked-path classification.
