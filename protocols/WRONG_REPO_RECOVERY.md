# WRONG_REPO_RECOVERY — When The Agent Is In The Wrong Repo

If the repo path, remote, branch, or mode does not match expectations, stop
immediately.

## Recovery steps

1. Do not commit.
2. Do not push.
3. Print diagnostic state:
   ```bash
   pwd
   git rev-parse --show-toplevel
   git remote -v
   git branch --show-current
   git status --short
   cat state/STUDYDD_MODE.yaml
   ```
4. Report every file you have touched in this session.
5. Revert touched files only if it is clearly safe or the learner explicitly
   approves.
6. If you are inside `StudyDD_Template` and were asked to do learner work, stop
   and explain the instantiation workflow from
   `protocols/INSTANTIATE_TEMPLATE.md`.
7. Never repair learner state inside the public template.
8. Never personalize the template.

## After recovery

Ask the learner to confirm the correct repo before continuing.
