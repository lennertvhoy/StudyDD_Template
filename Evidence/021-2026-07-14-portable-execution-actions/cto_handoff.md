# CTO handoff

StudyDD declares `studydd.plan-next-session/v1` and
`studydd.inspect-due-reviews/v1`. It validates structured action results and
owns the typed `set_active_activity` transactional writer. StatePort owns
orchestration and approval. No engine session or generated context is written
as canonical StudyDD state.
