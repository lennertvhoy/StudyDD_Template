# INSTANTIATE_TEMPLATE — Create A Learner Instance From The Mold

> **Agent action.** Use this protocol when the learner wants a new StudyDD repo.

## Law

`StudyDD_Template` is the factory mold. A learner instance is a cast made from that mold.

- Do not personalize the template repo.
- Do not put private learner state into the template repo.
- Personalization happens only after the template has been cloned, its `.git/` removed, and Git reinitialized in a new learner directory.
- The repo must pass through `bootstrap` mode before it becomes a `learner_instance`.

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

# 7. Verify where you are before editing state
pwd
git rev-parse --show-toplevel
git remote -v
cat state/STUDYDD_MODE.yaml

# 8. Switch from template to bootstrap mode
```

Edit `state/STUDYDD_MODE.yaml` to:

```yaml
mode: bootstrap
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: false
public_safe: false_or_review_required
```

Then continue:

```bash
# 9. Run bootstrap-safe validation
python3 scripts/check_studydd.py

# 10. Initialize the learner profile and first target
#     (Use protocols/START_SESSION.md and PROMPTS/coding_agent_start_prompt.md
#      inside the new instance, not in the template repo.)

# 11. Switch from bootstrap to learner_instance mode
```

Edit `state/STUDYDD_MODE.yaml` to:

```yaml
mode: learner_instance
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: true
public_safe: false_or_review_required
```

Then continue:

```bash
# 12. Run full learner-instance validation
python3 scripts/check_studydd.py

# 13. First commit
git add .
git commit -m "chore: initialize StudyDD learner instance"

# 14. Push only if the learner explicitly requested it
git push -u origin main
```

Replace `/home/ff/Study_Lenny` and the remote URL with the learner's actual paths.

## Bootstrap Mode

`bootstrap` means:

- The repo has left the template remote.
- Git history has been reset.
- Required template files, protocols, scripts, prompts, and mode marker are present.
- Learner profile and first target are **not** initialized yet.
- Validation passes with a warning that personalization is incomplete.

Do not switch to `learner_instance` until the learner profile, first target, skill map, sources, and next action are initialized.

## After Instantiation

1. Confirm the new repo is now a learner instance.
2. Initialize the learner profile and first target only inside the new instance.
3. Never return to the template repo to make learner-specific edits.

## Manual Instantiation Smoke Test

If you want to verify the template can still be instantiated:

```bash
python3 scripts/test_instantiate_template.py
```

The smoke test creates a temporary copy, reinitializes Git, runs bootstrap validation, simulates minimal learner initialization, switches to `learner_instance`, runs full validation, and cleans up.

## What Not To Do

- Do not edit the template repo during instantiation except to read it.
- Do not leave the template `.git/` history in the new instance.
- Do not initialize learner state before `.git/` is removed and Git is reinitialized.
- Do not set the new instance remote to `StudyDD_Template`.
- Do not run learner-instance validation until learner profile and first target are initialized.
- Do not switch directly from `template` to `learner_instance`; always use `bootstrap` first.
