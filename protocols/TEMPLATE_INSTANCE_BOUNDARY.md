# TEMPLATE_INSTANCE_BOUNDARY — Hardening The Mold vs The Cast

## What the boundary is

`StudyDD_Template` is the public factory mold. A learner instance is a separate cast made from that mold.

- **Template files** (`boundary: template`) — generic repo infrastructure: scripts, protocols, prompts, docs, mode markers, and the state manifest itself. They must stay identical and unpersonalized in every clone.
- **Instance files** (`boundary: instance`) — learner-specific state: targets, skills, evidence, sessions, reviews, sources, activity history, and the learner profile. In the template they must remain empty/generic placeholders.
- **Generated files** (`boundary: generated`) — derived context and indexes produced by scripts such as `compact_state.py` and `build_context_pack.py`. Their content differs between template and instance, but they are regenerated automatically and are not hand-edited with learner data.

## How the boundary is encoded

`state/STATE_MANIFEST.yaml` declares a `boundary` field for every tracked file:

- `template`
- `instance`
- `generated`

The validator (`scripts/check_studydd.py`) reads this field. In template mode it warns if any `boundary: instance` file contains learner-specific data.

## Agent rule

Before writing any state file, check `state/STATE_MANIFEST.yaml` for its `boundary`.

- If `boundary: instance` and the repo is in template mode, **stop**. Do not add learner data. Use `scripts/create_instance.py` to create a learner copy, or explain the instantiation workflow from `protocols/INSTANTIATE_TEMPLATE.md`.
- If `boundary: template`, keep the file generic and public-safe.
- If `boundary: generated`, let the generation scripts update it; do not hand-edit learner data into it.

## How to recover if the boundary is accidentally violated

1. Stop writing state.
2. Identify the touched `boundary: instance` files.
3. Either revert those files to the template's generic placeholders, or copy the current directory to a new learner instance with `scripts/create_instance.py` and then sanitize the template repo.
4. Run `python3 scripts/check_studydd.py` in the template repo and confirm there are no boundary-violation warnings.
5. Review `protocols/PRIVACY_REVIEW.md` before pushing anything that may have touched learner data.

## Cross-links

- `protocols/INSTANTIATE_TEMPLATE.md` — create a learner instance from the template.
- `protocols/PRIVACY_REVIEW.md` — scan a learner instance before pushing it publicly.
- `protocols/WRONG_REPO_RECOVERY.md` — what to do if you are in the wrong repo or mode.
