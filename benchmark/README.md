# Benchmark Data Area

This directory will contain reviewed source metadata, canonical rule and task
assets, Item/Pair definitions, and release split metadata.

The adopted initial source set is documented in the
[Phase 0 source shortlist](../docs/source-shortlist.md). Source intake and
candidate extraction have not started yet.

The planned SWE-bench Multilingual pilot representation is documented in
[Task sourcing and representation](../docs/task-sourcing.md). It uses a fixed
selection index plus one thin task spec per selected upstream instance; it does
not copy Harbor task directories into this repository.

The current repository intentionally has no benchmark records. Use the
subdirectories according to [the layout document](../docs/repository-layout.md).

Large source snapshots and generated workspaces do not belong here. Store them
externally and reference a fixed revision or content hash.
