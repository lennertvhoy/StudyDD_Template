# START_SESSION — Agent Session Startup

> **Agent action.** Run this protocol at the start of every StudyDD session.

This is a **session-boundary** operation: compaction and full validation are appropriate here.

## Must Do

1. **Verify repo path.**
   - `pwd`
   - `git rev-parse --show-toplevel`
   - Confirm the repo root is the expected StudyDD root.
   - If it is not, stop and tell the learner.

2. **Verify remote.**
   - `git remote -v`
   - Confirm the remote matches `https://github.com/lennertvhoy/StudyDD_Template.git` for template work.
   - For a forked learner copy, confirm the learner's remote.

3. **Check worktree.**
   - `git status --short`
   - If there are unexpected changes, report them before editing.

4. **Run validator.**
   - `python3 scripts/check_studydd.py`
   - Report pass/fail.
   - Fix validator failures before asking the first question.

5. **Build and read the context pack (session boundary).**
   - Run `python3 scripts/compact_state.py --check-stale` and only run `python3 scripts/compact_state.py` if stale.
   - Run `python3 scripts/build_context_pack.py --task start_session`.
   - Read `.studydd/context_pack.md`.
   - Load the active target's `study_skills/<id>/SKILL.md` or fall back to `study_skills/generic/SKILL.md`.
   - Open raw audit logs only if the context pack or validator says it is necessary.
   - See `protocols/STATE_LOADING_POLICY.md`.

6. **Check time-aware review state.**
   - Read the current date/time.
   - Read `reviews/REVIEW_STATE.yaml`.
   - Run or perform the equivalent of `scripts/select_next_study_action.py`.
   - If reviews are due or overdue, recommend review first before new material.

7. **Report a short orientation.**
   - Active target.
   - Session mode proposed (normal, deep, low-energy, recovery).
   - Due reviews and overdue reviews.
   - Last session focus.
   - Weakest skill.

8. **Choose session mode.**
   - Default: normal.
   - Use low-energy if the learner says they are tired, busy, or want something light.
   - Use recovery if the learner is stuck or wants to absorb without testing.
   - Use deep if the learner wants a hard scenario or exam-style drill.

9. **Confirm the first action with the learner.**
   - State the proposed next action.
   - If a review is due, say: "Recommended by StudyDD: review first. You can override, but this is the highest-retention move."
   - Wait for confirmation before asking the first question.
