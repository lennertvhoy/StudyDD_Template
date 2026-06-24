# UPGRADE_INSTANCE_FROM_TEMPLATE — Apply Template Improvements Safely

> **Agent action.** Use this protocol when a learner wants generic
> StudyDD_Template improvements copied into their personal instance.

## Law

- The learner instance is the source of truth for learner state.
- Generic template files (protocols, prompts, scripts, docs, validator) may be
  upgraded from the template.
- Learner state files must never be blindly overwritten.

## Before you start

1. Confirm the current repo is `mode: learner_instance` in
   `state/STUDYDD_MODE.yaml`. If it is `template` or `bootstrap`, stop.
2. Inspect `state/STUDYDD_TEMPLATE_VERSION.yaml` for the instance origin and
   last upgrade.
3. Confirm the template source path or remote with the learner.
4. Read `protocols/GIT_PROVENANCE.md` and `protocols/PRIVACY_REVIEW.md`.

## Protected files

Never blindly overwrite these:

- `state/STUDY_STATE.yaml`
- `state/SKILL_MAP.yaml`
- `state/EVIDENCE_LOG.md`
- `state/STUDY_BACKLOG.md`
- `state/STUDY_STATUS.md`
- `state/STUDYDD_TEMPLATE_VERSION.yaml` (merge metadata, do not replace)
- `sessions/SESSION_LOG.md`
- `reviews/REVIEW_QUEUE.md`
- `sources/SOURCE_INDEX.md`
- `targets/<learner_target_folders>/`
- `NEXT_ACTIONS.md`

## Generic files to upgrade

Copy or merge from the template only when the template version is newer:

- `AGENTS.md`
- `README.md`
- `protocols/`
- `PROMPTS/`
- `scripts/`
- `docs/`
- `.github/workflows/`
- `EXAMPLES/` (only if the learner confirms; examples are reference material)

## Upgrade steps

1. Verify repo path, remote, branch, and mode.
2. Record the current instance version and commit.
3. Run `python3 scripts/check_studydd.py` before changing anything.
4. Copy generic files from the template source to the instance.
5. For `state/STUDYDD_TEMPLATE_VERSION.yaml`, merge:
   - keep `instance_created_from_*`
   - update `last_template_upgrade_version` and `last_template_upgrade_commit`
   - append to `upgrade_history`
6. Run `python3 scripts/check_studydd.py` after the copy.
7. If validation fails, stop and report; do not commit a broken upgrade.
8. Commit the upgrade separately from any study-session changes:
   ```bash
   git add <generic files>
   git commit -m "chore: upgrade StudyDD generic files from template vX.Y.Z"
   ```
9. Push only if the learner explicitly requests it.

## Final handoff

Report:

- Template source used
- Template version upgraded from / to
- Files copied
- Files merged
- Files skipped
- Files protected
- Validation result before and after
- Any limitations or manual steps required

## What not to do

- Do not upgrade learner state files automatically.
- Do not run an upgrade inside the public template repo.
- Do not commit a broken upgrade.
- Do not push without explicit instruction.
