# Initial repo/mode/remote check

## pwd
/home/ff/Documents/Projects/StudyDD

## git rev-parse --show-toplevel
/home/ff/Documents/Projects/StudyDD

## git remote -v
origin	https://github.com/lennertvhoy/StudyDD_Template.git (fetch)
origin	https://github.com/lennertvhoy/StudyDD_Template.git (push)

## state/STUDYDD_MODE.yaml
---
mode: template
template_remote: "https://github.com/lennertvhoy/StudyDD_Template.git"
personalized: false
public_safe: true

# StudyDD mode lifecycle
#
# Allowed values:
#   - template          : reusable public mold. Must remain generic and public-safe.
#   - bootstrap         : newly cloned/reinitialized instance that is not
#                         personalized yet. The repo has left the template remote
#                         but the learner profile and first target are not ready.
#   - learner_instance  : active personal study repo with learner profile,
#                         targets, evidence, sessions, reviews, and next action.
#
# Transitions:
#   template -> bootstrap        : clone template, remove .git/, git init,
#                                  set new learner remote.
#   bootstrap -> learner_instance: initialize learner profile and first target.
#
# When this file is copied into a learner instance, first update it to:
#
#   mode: bootstrap
#   template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
#   personalized: false
#   public_safe: false_or_review_required
#
# Then, after the learner profile and first target are initialized, update it to:
#
#   mode: learner_instance
#   template_origin: "https://github.com/lennertvhoy/StudyDD_Template.git"
#   personalized: true
#   public_safe: false_or_review_required
#
# The mode field is the single source of truth for whether the current repo is
# the public template, a bootstrap instance, or a personal learner instance.

## state/STUDYDD_TEMPLATE_VERSION.yaml
---
# StudyDD template version tracking.
#
# This file is required in both the public template and every learner instance.
#
# Template mode:
#   template_version           : public version of the template mold.
#   template_commit            : HEAD commit of the template repo (populated by CI or agents).
#
# Learner instance mode:
#   instance_created_from_template_version : version of the template this instance was cast from.
#   instance_created_from_template_commit  : template HEAD at creation time.
#   last_template_upgrade_version          : version of the last generic upgrade applied.
#   last_template_upgrade_commit           : template HEAD of the last generic upgrade.
#   upgrade_history                        : list of applied upgrades with dates and notes.
#
# Do not edit template_version manually in a learner instance. Use the upgrade
# protocol in protocols/UPGRADE_INSTANCE_FROM_TEMPLATE.md.

template_version: "0.9.0"
template_commit: ""
instance_created_from_template_version: ""
instance_created_from_template_commit: ""
last_template_upgrade_version: ""
last_template_upgrade_commit: ""
upgrade_history: []
