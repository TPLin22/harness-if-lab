# Harness-IF Lab

`harness-if-lab` is a research repository for constructing and evaluating
instruction-following behavior inside coding-agent harnesses.

The central question is not whether a model can follow an isolated natural
language instruction. It is whether, when a rule is delivered through a
particular harness surface, the model can carry out the requested behavior
instead of reverting to a learned default or preferred pattern.

The first execution target is the internally controlled StepCLI harness. The
execution layer is intentionally replaceable: Harbor may be used as the first
backend, while the benchmark data model remains owned by this repository.

## Current status

The repository now contains the first pinned rule-source intake and an
agent-reviewed draft canonical rule library. The rule records are still
unqualified for task opportunities, prior tendency, contamination, and release;
there are not yet any collected coding tasks, Items, compilers, runners,
verifiers, or analysis implementations.

## Conceptual pipeline

```text
source material / LLM proposals
            |
            v
candidate rules and tasks
            |
            v
canonical rules + task specifications
            |
            v
Item / baseline-intervention pair
            |
            v
offline validation and qualification
            |
            v
harness-specific Pack
            |
            v
Harbor runner + StepCLI adapter
            |
            v
trial evidence -> verifier verdicts -> cross-run analysis
```

The source repository stores definitions and programs. Generated Packs,
temporary workspaces, raw logs, run artifacts, normalized tables, and reports
belong under an external `output_root`; see [the repository layout](docs/repository-layout.md).

## Documents

- [Overall design](docs/design.md)
- [Repository and execution constraints](docs/constraints.md)
- [Curation and experiment workflow](docs/workflow.md)
- [Phase 0 source shortlist](docs/source-shortlist.md)
- [Task sourcing and representation](docs/task-sourcing.md)
- [Repository layout and output boundary](docs/repository-layout.md)
- [Execution plans](docs/plans/README.md), currently
  [methodology and construction plan](docs/plans/2026-08-26-methodology-and-construction-plan.md)
- [Benchmark area](benchmark/README.md), including the current [rule candidates](benchmark/rules/candidates/README.md) and [canonical draft](benchmark/rules/canonical/README.md)
- [Schemas area](schemas/README.md)

The contributor and coding-agent contract is in [AGENTS.md](AGENTS.md). For
construction work, start with the active plan in [docs/plans](docs/plans/README.md).

## Initial design decisions

- Rules and tasks are reusable assets; an Item is an experimental condition,
  not a permanent Cartesian-product expansion.
- SWE-bench tasks are kept as thin, pinned `TaskSpec` references and selection
  manifests. Complete Harbor task packages are generated only at run time.
- Every intervention should have a comparable baseline, normally represented by
  a baseline/intervention pair.
- A semantic Item is compiled into a backend-specific Pack. A Pack is an input
  package, not a live workspace and not the canonical benchmark representation.
- Verification is performed at single-trial scope; analysis aggregates verified
  evidence across trials, models, harnesses, and replications.
- Intended and effective instruction surfaces must both be recorded. A surface
  delivery failure must not be confused with a model rule-following failure.
- Large source snapshots and all runtime outputs are referenced or stored
  externally and pinned by content/version metadata.

## References

The design is informed by the Harness-IF paper ([arXiv:2608.11727](https://arxiv.org/abs/2608.11727)),
Harbor's task/execution model, and StepCLI's extension-surface and artifact
interfaces. These references are implementation inputs, not normative schemas
for this project.
