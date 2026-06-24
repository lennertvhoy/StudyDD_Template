# Sessions

`sessions/` contains tutor session logs and state update history.

Use this folder for durable session history. Keep only the current learner truth in `state/`.

## Files

- `SESSION_LOG.md` — chronological tutor session history.

Agents may create dated session files later if a study history becomes long, but the default happy path starts with `SESSION_LOG.md`.
