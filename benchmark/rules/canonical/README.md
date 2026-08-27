# Canonical Rule Drafts

`phase0-canonical.yaml` contains the first agent-reviewed semantic rule drafts.
It has 45 records derived from the 44 candidates in
`../candidates/phase0-candidates.yaml`; the one-to-many decomposition of
`rule-p0-014` is recorded in `../candidates/phase0-review.yaml`.

These records are canonicalized enough to serve as inputs to task matching and
Item construction, but they are not a released benchmark. `prior`,
contamination, task opportunity, verifier qualification, and final human
approval remain open. The `source_pool` field must be retained so
`harness_native_calibration` records cannot silently enter a generalization
release.
