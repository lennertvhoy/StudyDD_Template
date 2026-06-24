# Activity Log

## Purpose

This file is the append-only audit trail for StudyDD learning activities. It records every assigned activity, learner response, submitted evidence, override, and result. It is not default runtime context; agents normally load the compact `state/ACTIVITY_STATE.yaml` and the task-specific context pack instead.

## Activity entry format

```markdown
- **Activity ID:** act_...
- **Timestamp:** ISO 8601 with timezone
- **Type:** activity type from ACTIVITY_TEMPLATES.yaml
- **Target ID:** target identifier
- **Skill ID:** skill identifier
- **Status:** proposed | accepted | modified | overridden | completed | insufficient_evidence
- **Reason:** why the agent recommended this activity
- **Task:** what the learner was asked to do
- **Expected evidence:** list of expected evidence formats
- **Submitted evidence:** evidence ID(s) if any
- **Verdict:** correct | partial | incorrect | unclear | insufficient_evidence
- **Learner override reason:** if the learner changed or rejected the recommendation
- **Notes:** any other relevant detail
```

## Activities

None yet.
