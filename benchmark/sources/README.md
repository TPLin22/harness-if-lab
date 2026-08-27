# Source Intake

This directory contains the small, reviewable inputs to Phase 0 rule
curation. It does not contain a checkout or a long snapshot of an upstream
repository.

`phase0-source-manifest.yaml` pins the upstream file, commit, Git blob hash,
content hash, license, and source pool used for this batch. The manifest is an
internal curation record; it is not the public provenance tier of a released
rule.

`phase0-raw-units.yaml` retains bounded working excerpts and their source
locations and section headings. A raw unit is deliberately allowed to be
bundled. Its
`candidate_ids` field records any one-to-many decomposition into atomic
candidates. Excerpts may normalize markup/capitalization and omit surrounding
context; the pinned commit, path, and line locator are authoritative and the
excerpt is not a replacement for the upstream file.

The batch-level selection flags state that the sampled units are not generated
file instructions and are not alias/import-only instructions. A future intake
that selects such material must override those flags and explain the choice.

The current batch was retrieved on 2026-08-27 through the GitHub Contents API.
Long source files were downloaded to a system temporary directory during
intake and are not part of this repository.
