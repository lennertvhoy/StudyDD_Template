# Integration order

Source-check completion and boundary work were reconciled first, Fast Drill
was retained as its own selected module, and lifecycle/bootstrap work was then
integrated. The manifest validator and freshness outcome handling were fixed
where the reconstructed contracts required it. The resulting commit/tree and
manifest digest were recalculated before StatePort was pinned.
