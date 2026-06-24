# Create A New StudyDD Instance From The Template

You are creating a new StudyDD learner instance from the public template. **Do not personalize the template repo itself.** Personalization happens only inside the target repo after it has been cloned, detached from the template Git history, and reinitialized.

## Hard Rules

- The template repo (`StudyDD_Template`) is read-only except for template-maintenance tasks.
- Personalization starts only after `clone` → `rm -rf .git` → `git init` in the target repo.
- The target repo must pass through `bootstrap` mode before `learner_instance` mode.
- You must print `pwd`, `git rev-parse --show-toplevel`, `git remote -v`, and `cat state/STUDYDD_MODE.yaml` before editing any file.

## Before You Start

1. Confirm the source template:
   - repo path: `/home/ff/Documents/Projects/StudyDD`
   - remote: `https://github.com/lennertvhoy/StudyDD_Template.git`
   - `state/STUDYDD_MODE.yaml` says `mode: template`
2. Ask the learner for the new instance directory and remote.
3. Confirm the target directory does not already exist or is empty.
4. Confirm the target directory is not inside the template repo.

## Instantiation Steps

Run exactly:

```bash
git clone https://github.com/lennertvhoy/StudyDD_Template.git /home/ff/Study_Lenny
cd /home/ff/Study_Lenny
rm -rf .git
git init
git branch -M main
git remote add origin https://github.com/lennertvhoy/Study_Lenny.git

# Verify location and remote before any edit
pwd
git rev-parse --show-toplevel
git remote -v
cat state/STUDYDD_MODE.yaml
```

Replace `/home/ff/Study_Lenny` and the remote URL with the learner's actual values.

## Switch To Bootstrap Mode

Edit `state/STUDYDD_MODE.yaml` in the **target repo only** to:

```yaml
mode: bootstrap
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: false
public_safe: false_or_review_required
```

Then run bootstrap-safe validation:

```bash
python3 scripts/check_studydd.py
```

A bootstrap repo is expected to warn that personalization is not complete. That warning is normal. Do not treat it as a failure.

## Initialize The Learner

1. Read `AGENTS.md` inside the new instance.
2. Ask the learner the essential setup questions.
3. Initialize learner profile, first target, skill map, sources, reviews, sessions, and next action — **all inside the new instance only**.

## Switch To Learner Instance Mode

Only after learner profile and first target are initialized, edit `state/STUDYDD_MODE.yaml` in the target repo to:

```yaml
mode: learner_instance
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: true
public_safe: false_or_review_required
```

Then run full validation:

```bash
python3 scripts/check_studydd.py
```

**Warning:** Do not run learner-instance validation until learner profile and first target are initialized. The validator will fail if `mode: learner_instance` is set before the required learner state exists.

## First Commit And Push

```bash
git add .
git commit -m "chore: initialize StudyDD learner instance"
```

Push only if the learner explicitly requests it:

```bash
git push -u origin main
```

## What Not To Do

- Do not edit the template repo except to read it.
- Do not initialize learner state in the template repo.
- Do not switch directly to `mode: learner_instance` without passing through `bootstrap`.
- Do not run `python3 scripts/check_studydd.py` in learner-instance mode before learner initialization.
- Verify path and remote before every edit.
- Do not leave the template `.git/` history in the new instance.
