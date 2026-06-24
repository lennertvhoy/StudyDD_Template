# PRIVACY_REVIEW — Pre-Push Scan For A Learner Instance

Before pushing a learner instance to a public or shared remote, scan for
content that should stay private.

## What to scan

Walk learner-state files and any notes the learner added:

- `state/`
- `targets/`
- `sessions/`
- `reviews/`
- `sources/`
- `NEXT_ACTIONS.md`
- Any extra `.md` or `.yaml` files the learner created

## What to flag

Warn or stop for:

- Personal names (learner's real name if they chose not to share it)
- Email addresses
- Phone numbers
- Health or recovery details
- Employer-sensitive information
- Proprietary exam dumps or paid content
- Credentials, secrets, tokens, API keys, passwords
- Private learner notes intended only for the learner

## Practical scan

Use `scripts/agent_privacy_check.py` for a first pass. It warns by default.
Review every warning before pushing.

## What not to do

- Do not fail the template repo because it contains generic placeholder text.
- Do not create a large compliance framework.
- Do not push a learner instance publicly without the learner's explicit
  consent.
