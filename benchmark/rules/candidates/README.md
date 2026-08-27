# Candidate Rules

`phase0-candidates.yaml` is the immutable first extraction snapshot. It contains
provisional restatements extracted from the pinned source files in
`benchmark/sources/`; its `candidate_unreviewed` fields describe the extraction
state, not the later curation decision.

These records are intentionally usable enough to expose missing fields, but
they are not a formal schema and they are not canonical or released rules. In
particular:

- `statement` is a neutral behavioral restatement; it is not a verbatim copy of
  the source and should preserve the source's modality (`prefer` is not silently
  changed into `require`);
- `raw_unit_ref` links back to the bounded excerpt and preserves one-to-many
  decomposition when a source paragraph contains several constraints;
- `prior` is unset and contamination/opportunity qualification is not assessed;
- `surface_fit` is a draft suitability annotation, not a StepCLI configuration;
- `scoring_method` and evidence fields are hypotheses for later verifier design,
  not proof that a task opportunity exists.

The batch currently contains 44 candidates from 39 raw units. The
`generalization` and `harness_native_calibration` pools are intentionally kept
separate in metadata. Calibration candidates may mention a project-specific
tool or path and must not be silently promoted to the generalization track.

Coverage is 32 generalization candidates from G1--G6 and 12 calibration
candidates from C1--C4. C5 (Rust `AGENTS.md`) is pinned in the source manifest
but remains a reserve because its first sections are policy-heavy.

The agent review disposition is recorded in `phase0-review.yaml`. It accepts
all 44 candidate records for the draft library, splitting the bundled tests-and
docs candidate into two atomic records. The resulting 45 records are in
`benchmark/rules/canonical/phase0-canonical.yaml`.

This is an interim review for pipeline bring-up, not final human release
approval. Promotion to a released split still requires provenance/licensing
review, task-opportunity qualification, verifier coverage, prior labeling, and
the other release gates in the project design.
