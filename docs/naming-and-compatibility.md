# Naming and compatibility

StudyState is the public name of this learning application and template.
StateSpec is the public name of the portable application specification formerly
called StateDD. State-Centric Engineering names the engineering method.

This release changes current user-facing and operator-facing language without
breaking installed learner instances. Existing machine contracts remain valid:

- the repository and remote remain `StudyDD_Template`;
- `state/STUDYDD_MODE.yaml`, `state/STUDYDD_TEMPLATE_VERSION.yaml`,
  `.studydd/`, `STUDYDD_*` environment variables, script names, import names,
  schema identifiers, event names, and persisted fields retain their legacy
  spellings;
- existing URLs, Git history, evidence, session logs, and legal text are not
  rewritten;
- downstream instances may adopt the public name independently while continuing
  to consume the same compatibility contracts.

New prose should use StudyState, StateSpec, and State-Centric Engineering unless
it refers to an exact compatibility identifier. A future physical rename must
ship as a separately versioned migration with aliases, upgrade tests, rollback,
and an explicit removal schedule. Public naming alone is not permission to
rename paths or invalidate durable state.
