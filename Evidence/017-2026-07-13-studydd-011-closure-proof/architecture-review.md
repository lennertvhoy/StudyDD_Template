# Architecture review

StudyDD owns domain manifests, module contracts, source freshness, Fast Drill,
and compatibility-view content. StatePort owns lifecycle authority and
transaction mechanics. Runtime and lifecycle manifests remain distinct; no
arbitrary recursive merge or template code execution was added.
