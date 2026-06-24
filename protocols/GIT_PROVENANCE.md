# GIT_PROVENANCE — Agent Git Identity And History Rules

Agents must inspect Git provenance before making commits in a StudyDD repo.

## Required checks

Run and report:

```bash
pwd
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status --short
git config --show-origin --get user.name || true
git config --show-origin --get user.email || true
git log -1 --pretty=fuller || true
```

## Repo-local identity for learner instances

Set a repo-local identity so the agent does not leak the operator's personal
Git config into the learner repo:

```bash
git config user.name "StudyDD Agent"
git config user.email "studydd-agent@example.invalid"
```

Use repo-local config only. Do not use `--global`.

## Template repo identity

For commits inside `StudyDD_Template`, use the operator's real identity or the
repo-local identity above. The template must stay public-safe and generic.

## History

Do not rewrite history unless explicitly instructed by the learner. This
includes rebase, reset, and force-push.

## Handoff

Every agent handoff must include:

- repo path
- branch
- HEAD commit
- pushed status
- worktree status
