# Upgrade A StudyDD Learner Instance From The Template

You are applying a generic StudyDD_Template upgrade to an existing learner
instance. Do not touch learner state.

## Before you start

1. Verify repo path: `pwd`, `git rev-parse --show-toplevel`.
2. Verify remote and branch: `git remote -v`, `git branch --show-current`.
3. Read `state/STUDYDD_MODE.yaml` and confirm `mode: learner_instance`.
4. Read `state/STUDYDD_TEMPLATE_VERSION.yaml`.
5. Read `protocols/UPGRADE_INSTANCE_FROM_TEMPLATE.md`,
   `protocols/GIT_PROVENANCE.md`, and `protocols/PRIVACY_REVIEW.md`.

## Locate the template source

Ask the learner for the template path or remote. The public template is:

- Remote: `https://github.com/lennertvhoy/StudyDD_Template.git`
- Local path: the directory they originally cloned from

## Inspect versions

Compare:

- `state/STUDYDD_TEMPLATE_VERSION.yaml` in the instance
- `state/STUDYDD_TEMPLATE_VERSION.yaml` in the template source

Only proceed if the template source version is newer or the learner explicitly
wants a specific upgrade.

## Protect learner state

Do not overwrite:

- `state/STUDY_STATE.yaml`
- `state/SKILL_MAP.yaml`
- `state/EVIDENCE_LOG.md`
- `state/STUDY_BACKLOG.md`
- `state/STUDY_STATUS.md`
- `sessions/SESSION_LOG.md`
- `reviews/REVIEW_QUEUE.md`
- `sources/SOURCE_INDEX.md`
- `targets/<learner_target_folders>/`
- `NEXT_ACTIONS.md`

`state/STUDYDD_TEMPLATE_VERSION.yaml` should be merged, not replaced.

## Copy or merge generic improvements

Upgrade these from the template:

- `AGENTS.md`
- `README.md`
- `protocols/`
- `PROMPTS/`
- `scripts/`
- `docs/`
- `.github/workflows/`
- `EXAMPLES/` only if the learner confirms

## Validate before and after

Run `python3 scripts/check_studydd.py` before and after the upgrade. Do not
commit if validation fails.

## Commit and push

Commit only when instructed:

```bash
git add <generic files>
git commit -m "chore: upgrade StudyDD generic files from template vX.Y.Z"
```

Push only when the learner explicitly asks.

## Report

List copied, merged, skipped, and protected files. Note any validator warnings
or limitations.
