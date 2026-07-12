# Public-safety and secret-scan record

## Result

No learner-specific data, personal targets, personal evidence, private
question-bank material, credentials, tokens, or private repository URLs were
located in the recovered dirty additions.

## Checks

- `python3 scripts/agent_privacy_check.py` completed in soft mode.
- Added-line and untracked-file scans checked for machine-specific home paths,
  private-canary names, common GitHub/OpenAI/AWS token signatures, and PEM
  private-key headers.
- Changed and untracked files were reviewed for repository URLs. New URLs are
  limited to the canonical public template, its SSH spelling in normalization
  tests, and `example` fixture remotes.

The soft scanner's warnings were reviewed:

- sensitive keywords occur in the scanner's own pattern list;
- `git@github.com` normalization fixtures are parsed as possible emails;
- a generic `medical` keyword occurs in a pre-existing design document.

These are not private learner findings.

## Pre-existing debt distinguished from this WIP

Whole-file scanning surfaced existing README and instantiation examples that
use a machine-specific home path and a sample learner-repository name. The
recovered diff did not add those lines. They were preserved unchanged and
should be handled in a separately reviewed public-template cleanup rather than
silently folded into this WIP.

Dedicated secret-scanning CLIs were not installed in the environment. No
dependency was installed because repository policy requires explicit consent.
