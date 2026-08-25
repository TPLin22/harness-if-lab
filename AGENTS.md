# Repository Working Contract

This file is the repository-level instruction for contributors and coding
agents. It describes boundaries that must remain true while the project is
implemented.

## Scope

This repository studies instruction following in an agent harness. The unit of
interest is observable behavior under a declared instruction surface and
authority policy. It is not a general coding benchmark and it is not a prompt
library for one named product.

The first harness adapter is StepCLI. Pi and Codex are future adapters. Harbor
is an execution backend/reference, not the research data model.

## Non-negotiable boundaries

1. Keep semantic benchmark data independent from a particular runner. Rules,
   tasks, and Items must not be authored directly as Harbor-only structures.
2. Keep the intended surface separate from the effective surface. Record what
   the experiment tried to deliver and what the harness actually loaded or
   exposed.
3. Keep model-visible inputs separate from evaluator-only information. Hidden
   expected behavior, labels, oracle solutions, and verifier internals must not
   be mounted in the agent's readable context.
4. Pair interventions with a baseline whenever the claim depends on changing
   default behavior. Do not report an unpaired rule score as a causal result.
5. Treat a missing, truncated, or misrouted instruction as a delivery failure,
   not automatically as a model violation.
6. Preserve provenance and reproducibility: source references, versions,
   hashes, environment identity, model settings, harness commit, and replicate
   identity must travel with generated data and runs.
7. Keep generated runtime state out of Git. Packs, live workspaces, Harbor
   jobs, traces, artifacts, normalized tables, and reports belong in an
   externally configured `output_root`.
8. Prefer deterministic verifiers. An LLM judge is a documented fallback, not
   the only evidence for a rule that can be checked from code or event logs.
9. Do not add harness-name-specific wording to a generalization item unless the
   item is explicitly in a harness-specific track.
10. Do not add implementation or formal schema details ahead of the design
    decision they serve. Keep this scaffold lightweight until the core
    contracts are reviewed.

## Data curation rules

- LLM-assisted extraction is proposal generation. Human or deterministic review
  promotes candidates into canonical assets.
- A canonical rule should express one observable behavioral constraint, its
  scope, exceptions, and intended evidence. Bundled or purely stylistic prose
  should be split or rejected.
- A task should have a deterministic initial state, a neutral coding objective,
  and an executable or otherwise auditable success condition.
- A candidate Item must be checked for rule/task compatibility, an observable
  opportunity, surface support, verifier coverage, and accidental leakage.
- Exploratory combinations may be generated on demand. Only reviewed,
  versioned releases need to be fixed as a dataset artifact.

## Execution and evaluation rules

- The runner must materialize a fresh, isolated trial workspace.
- The runner must not silently flatten distinct surfaces merely because a
  backend exposes one instruction string. Unsupported surfaces must be marked
  unsupported or delivered through an explicit adapter contract.
- Native harness events should be retained alongside normalized trajectory data.
- A verdict must be traceable to concrete evidence: file diff, test result,
  tool event, or a clearly identified judge decision.
- Analysis code reads external artifacts and produces external reports; it does
  not mutate source benchmark definitions.

## Change discipline

- Read the relevant design document before changing a boundary or directory.
- Update documentation when a lifecycle, ownership boundary, or artifact
  contract changes.
- Keep changes scoped. Do not revert unrelated work in neighboring repositories.
- Before implementation begins, review and approve the future contracts for
  `RuleSpec`, `TaskSpec`, `Item/Pair`, `Pack`, `Run`, and `Verdict`.
