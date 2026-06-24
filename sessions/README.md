# Sessions

`sessions/` contains tutor session logs and SkillSignal update packets.

Use this folder for durable session history. Keep only the current learner truth in `state/`.

## Files

- `SESSION_LOG.md` — chronological tutor session history.
- `SKILLSIGNAL_PACKETS.md` — compact proposed updates from a session before they are applied to state.

Agents may create dated session files later if a study history becomes long, but the default happy path starts with these two files.
