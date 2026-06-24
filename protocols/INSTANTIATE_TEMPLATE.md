# INSTANTIATE_TEMPLATE — Create A Learner Instance From The Mold

> **Agent action.** Use this protocol when the learner wants a new StudyDD repo.

## Law

`StudyDD_Template` is the factory mold. A learner instance is a cast made from that mold.

- Do not personalize the template repo.
- Do not put private learner state into the template repo.
- Personalization happens only after the template has been cloned, its `.git/` removed, and Git reinitialized in a new learner directory.

## Source Template Verification

Before copying, confirm the source template:

- repo path: `/home/ff/Documents/Projects/StudyDD`
- remote: `https://github.com/lennertvhoy/StudyDD_Template.git`
- `state/STUDYDD_MODE.yaml` says `mode: template`

If the source repo does not look like the template, stop and ask the learner for the correct template path/remote.

## Target Directory Selection

1. Ask the learner for the new instance directory name, e.g. `Study_Lenny`.
2. Confirm the target path, e.g. `/home/ff/Study_Lenny`.
3. Verify the target directory does not already exist or is empty. If it exists and is not empty, stop and ask for confirmation.
4. Verify the target directory is not inside the template repo.

## Instantiation Steps

Run these commands exactly:

```bash
# 1. Clone the template into the new learner directory
git clone https://github.com/lennertvhoy/StudyDD_Template.git /home/ff/Study_Lenny

# 2. Enter the new directory
cd /home/ff/Study_Lenny

# 3. Remove the template Git history
rm -rf .git

# 4. Reinitialize Git
git init

# 5. Set the default branch
git branch -M main

# 6. Add the learner's remote if provided
git remote add origin https://github.com/lennertvhoy/Study_Lenny.git

# 7. Run the validator
python3 scripts/check_studydd.py
```

Replace `/home/ff/Study_Lenny` and the remote URL with the learner's actual paths.

## Replace Template Placeholders

1. Update `state/STUDYDD_MODE.yaml`:

```yaml
mode: learner_instance
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: true
public_safe: false_or_review_required
```

2. Update `state/STUDY_STATE.yaml` to mark the repo as a learner instance.
3. Keep template-version metadata so future template upgrades can be traced.

## First Commit

```bash
git add .
git commit -m "chore: initialize StudyDD learner instance"
```

## Push If Remote Exists And User Requested

```bash
git push -u origin main
```

Only push if the learner has provided a remote and explicitly asked to push.

## After Instantiation

1. Confirm the new repo is now a learner instance.
2. Initialize the learner profile and first target only inside the new instance.
3. Never return to the template repo to make learner-specific edits.

## What Not To Do

- Do not edit the template repo during instantiation except to read it.
- Do not leave the template `.git/` history in the new instance.
- Do not initialize learner state before `.git/` is removed and Git is reinitialized.
- Do not set the new instance remote to `StudyDD_Template`.
