# Proposal contract

The plan action can emit `studydd.state-change-proposal/v1` with a run binding,
pre-state digest, typed operations, destination, rationale, sensitivity, and
required validation. The writer rejects arbitrary patches and restores the
destination bytes if validation fails.
