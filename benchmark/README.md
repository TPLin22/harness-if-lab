# Benchmark Data Area

This directory will contain reviewed source metadata, canonical rule and task
assets, Item/Pair definitions, and release split metadata.

The adopted initial source set is documented in the
[Phase 0 source shortlist](../docs/source-shortlist.md). The first intake batch
has now been collected: pinned source metadata and raw units are in
[`sources/`](sources/), and provisional rule candidates are in
[`rules/candidates/`](rules/candidates/). They remain the extraction snapshot
and are not a released benchmark.

An agent review has produced 45 draft canonical records from the 44 candidates;
the review ledger is next to the candidate snapshot and the canonical records
are in [`rules/canonical/`](rules/canonical/). They remain unqualified and are
not a released benchmark.

The planned SWE-bench Multilingual pilot representation is documented in
[Task sourcing and representation](../docs/task-sourcing.md). It uses a fixed
selection index plus one thin task spec per selected upstream instance; it does
not copy Harbor task directories into this repository.

The repository intentionally has no released benchmark records yet. Use the
subdirectories according to
[the layout document](../docs/repository-layout.md).

Large source snapshots and generated workspaces do not belong here. Store them
externally and reference a fixed revision or content hash.
