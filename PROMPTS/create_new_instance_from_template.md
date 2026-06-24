# Create A New StudyDD Instance From The Template

You are creating a new StudyDD learner instance from the public template. Do not personalize the template repo itself.

## Before You Start

1. Confirm the source template:
   - repo path: `/home/ff/Documents/Projects/StudyDD`
   - remote: `https://github.com/lennertvhoy/StudyDD_Template.git`
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
python3 scripts/check_studydd.py
```

Replace `/home/ff/Study_Lenny` and the remote URL with the learner's actual values.

## Mark As Learner Instance

1. Update `state/STUDYDD_MODE.yaml`:

```yaml
mode: learner_instance
template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: true
public_safe: false_or_review_required
```

2. Update `state/STUDY_STATE.yaml` to mark the repo as a learner instance.

## First Commit

```bash
git add .
git commit -m "chore: initialize StudyDD learner instance"
```

Push only if the learner explicitly requests it:

```bash
git push -u origin main
```

## Then Initialize The Learner

1. Read `AGENTS.md` inside the new instance.
2. Ask the learner the essential setup questions.
3. Initialize learner profile, first target, skill map, sources, and next action — all inside the new instance only.

## Hard Rules

- Do not edit the template repo except to read it.
- Do not initialize learner state in the template repo.
- Verify path and remote before every edit.
- Do not leave the template `.git/` history in the new instance.
