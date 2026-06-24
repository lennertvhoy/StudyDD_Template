# Repo Check — StudyDD Demo Path v1

**Date:** 2026-06-24

```bash
pwd
# /home/ff/Documents/Projects/StudyDD

git rev-parse --show-toplevel
# /home/ff/Documents/Projects/StudyDD

git remote -v
# origin	https://github.com/lennertvhoy/StudyDD_Template.git (fetch)
# origin	https://github.com/lennertvhoy/StudyDD_Template.git (push)
```

`state/STUDYDD_MODE.yaml`:

```yaml
mode: template
template_remote: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: false
public_safe: true
```

`state/STUDYDD_TEMPLATE_VERSION.yaml`:

```yaml
template_version: "0.7.0"
```

Confirmed: working in the public template repo with the correct remote. Mode is `template`, public-safe, and unpersonalized.
