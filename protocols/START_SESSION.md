# START_SESSION — Agent Session Startup

> **Agent action.** Run this protocol at the start of every StudyDD session.

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

5. **Read required files.**
   - All files listed in `AGENTS.md` "Required First Actions".

6. **Report a short orientation.**
   - Active target.
   - Session mode proposed (normal, deep, low-energy, recovery).
   - Due reviews.
   - Last session focus.
   - Weakest skill.

7. **Choose session mode.**
   - Default: normal.
   - Use low-energy if the learner says they are tired, busy, or want something light.
   - Use recovery if the learner is stuck or wants to absorb without testing.
   - Use deep if the learner wants a hard scenario or exam-style drill.

8. **Confirm the first action with the learner.**
   - State the proposed next action.
   - Wait for confirmation before asking the first question.
