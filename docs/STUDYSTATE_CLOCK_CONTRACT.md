# StudyState private-alpha logical-clock contract

The public-safe StudyDD development scenario is materialized only with an
explicit ISO-8601 `--evaluation-time` that includes a timezone. It never reads
the machine wall clock for scheduling or source-fixture timestamps.

At a given logical time, replaying the scenario produces the same due-review
state. Advancing the supplied time by one day moves the same review from
scheduled to due. The scenario's retrieval question is `conceptual_practice`; it
does not convert fixture metadata into a live-source assertion.

Production behavior remains strict: an `authoritative_current` volatile or
live question still requires a fresh usable source at the actual evaluation
time. The development candidate is explicitly `productionEligible: false`.

The StatePort journey may propose placing the due review ahead of new material,
but the proposal is human-on-the-loop, visible, redirectable, and reversible.
StatePort owns acceptance of a plan change; the StudyDD harness only provides
the deterministic domain scenario and evidence.
