# Repository Layout

The source repository is intentionally small. It contains definitions and code
that can be reviewed and versioned. Runtime data is external.

## Source tree

```text
harness-if-lab/
├── AGENTS.md
├── README.md
├── benchmark/
│   ├── sources/
│   ├── rules/
│   │   ├── candidates/
│   │   ├── canonical/
│   │   └── renderings/
│   ├── tasks/
│   │   ├── indexes/
│   │   ├── specs/
│   │   ├── fixtures/
│   │   └── generators/
│   ├── items/
│   └── splits/
├── schemas/
├── generators/
├── compilers/
│   └── harbor/
├── harnesses/
│   └── stepcli/
├── verifiers/
├── analysis/
├── configs/
├── docs/
│   ├── source-shortlist.md
│   ├── task-sourcing.md
│   └── plans/
│       └── completed/
├── examples/
│   └── smoke/
└── tests/
```

## Directory responsibilities

| Directory | Purpose in the initial design |
| --- | --- |
| `benchmark/sources` | Source metadata, permitted excerpts, and provenance references. |
| `benchmark/rules/candidates` | Unreviewed or LLM-assisted rule proposals. |
| `benchmark/rules/canonical` | Reviewed, reusable semantic rules. |
| `benchmark/rules/renderings` | Surface-specific expressions of canonical rules. |
| `benchmark/tasks/specs` | Neutral task definitions and fixture references. |
| `benchmark/tasks/indexes` | Frozen task-panel selections, sampling metadata, and reserve/exclusion records. |
| `benchmark/tasks/fixtures` | Small, versioned fixtures suitable for the source tree. |
| `benchmark/tasks/generators` | Future task-generation utilities. |
| `benchmark/items` | Reviewed experimental Item/Pair definitions or release indexes. |
| `benchmark/splits` | Future split and release metadata. |
| `schemas` | Future machine-readable validation schemas; no formal specs yet. |
| `generators` | Cross-cutting candidate and dataset generation programs. |
| `compilers/harbor` | Translation from semantic Items to Harbor input packages. |
| `harnesses/stepcli` | StepCLI-specific surface delivery and evidence adapter. |
| `verifiers` | Single-trial rule/task evidence checks. |
| `analysis` | Cross-trial ingestion, normalization, statistics, and report code. |
| `configs` | Future experiment and backend configuration templates. |
| `docs` | Durable documents: design, constraints, workflow, and layout. |
| `docs/plans` | Dated execution plans; superseded rather than maintained. See `AGENTS.md`. |
| `examples/smoke` | Future tiny end-to-end examples for CI and adapter tests. |
| `tests` | Tests for the eventual contracts and implementations. |

`benchmark/tasks/indexes` is for selecting upstream task instances (for example,
the 20-task SWE-bench pilot). `benchmark/splits` is reserved for released
rule/Item train, qualification, and evaluation split metadata; the two should
not be used interchangeably. `benchmark/sources` remains primarily the
provenance area for rule-source material; task-source pins and task content live
under `benchmark/tasks/`.

## External inputs and output root

There are two different external locations. A task cache is reusable input data;
an output root is mutable data produced by one experiment. They may share a
filesystem but should not be assumed to have the same lifecycle or permissions.

### External task cache

`HIF_TASK_CACHE` (or an equivalent setting) points to evaluator/compiler input
keyed by provider, immutable dataset revision, and task ID. It may contain
downloaded source repositories, hidden patches, test metadata, or prebuilt image
references. It is never committed and must not be mounted into the model's
readable workspace.

### External output root

No `packs` or `artifacts` directory is maintained in this repository. A run
should receive an explicit `HIF_OUTPUT_ROOT` (or equivalent configuration), for
example:

```text
/mnt/experiments/harness-if/exp-<id>/
├── experiment.lock.json
├── packs/
├── harbor/jobs/
├── artifacts/
├── normalized/
├── reports/
└── cache/
```

The exact storage medium may be a local disk, shared filesystem, or object
store. The source repository should only retain references, hashes, and small
smoke fixtures.

## Input versus output

- A canonical rule or task is a reusable source input.
- An Item is a declarative research condition.
- A Pack is a compiled execution input and can be regenerated from an Item.
- A workspace is an ephemeral trial resource.
- An Artifact is evidence from one run, not a second source repository.
- A report is a derived view and must be reproducible from external artifacts.
