# StudyDD PR conflict matrix

Read-only review against `origin/main`; none of these branches was used as the
integration base.

| Surface | PR #4 source-check | PR #5 fast-drill | PR #6 WIP handoff | Adoption disposition |
|---|---|---|---|---|
| `AGENTS.md`, `README.md`, `NEXT_ACTIONS.md` | semantic overlap | semantic overlap | direct/semantic overlap | compatible only after independent extraction and rebase |
| `.gitignore` | independent | direct change | direct change | lifecycle branch keeps current main plus lifecycle-generated boundaries |
| `.github/workflows/validate.yml` | direct CI edits | direct CI edits | direct CI edits | do not integrate in this slice; local gate is authoritative |
| `state/STATE_MANIFEST.yaml` | direct | direct | direct | superseded as lifecycle authority by explicit template/instance fragments and generated view |
| `state/STUDYDD_MODE.yaml` | semantic | semantic | direct | generated compatibility view; no PR state merged |
| `state/STUDYDD_TEMPLATE_VERSION.yaml` | independent/semantic | independent | semantic | generated compatibility view from instance lock |
| `state/LEARNER_PROFILE.yaml` | independent | direct generic defaults | direct generic defaults | remains instance-owned; extract only public defaults later |
| `scripts/check_studydd.py` | direct | direct | direct | lifecycle contract hook integrated centrally; PR validator work remains separate |
| `scripts/create_instance.py` | independent | indirect | direct | lifecycle-aware creation integrated from clean main; rebase later work |
| protocols | direct/semantic | direct/semantic | direct/semantic | requires clean extraction per protocol, not stacked adoption |
| tests | direct/semantic | direct/semantic | direct/semantic | run independently after extraction; no open-PR-only test asset declared |

Disposition: PR #4 is source-check completion and is compatible after clean
rebase; PR #5 is conflict-heavy and must be independently extracted; PR #6 is
WIP preservation, not a closure candidate, and its exact PR ref was not present
in local refs. Recommended future order: lifecycle adoption → clean extraction
of PR #4 → separately reviewed PR #5 fast-drill → selectively extracted PR #6
hardening. No PR was modified by this slice.
