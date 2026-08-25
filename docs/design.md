# Overall Design

## 1. Purpose

Harness-IF Lab is a data-generation and evaluation system for studying whether
coding agents follow rules delivered by an agent harness, especially when those
rules conflict with a model's learned default behavior.

The first research track focuses on single-agent StepCLI runs. It can cover
coding style, project conventions, tool-facing instructions, and authority or
priority conflicts. Sub-agent communication is reserved for a later track so
that the first measurements do not mix instruction following with multi-agent
coordination.

## 2. Design principles

### Semantic data first

The repository owns the meaning of rules, tasks, Items, and evaluation
conditions. A runner backend only determines how those conditions are executed.
This keeps the same research item usable across StepCLI, Pi, Codex, or a future
runner.

### One intended intervention

An experiment should change one declared factor at a time where possible. The
baseline and intervention use the same task, fixture, model settings,
environment, and execution budget; the intended rule delivery is the controlled
difference.

### Surface fidelity

The experiment distinguishes the semantic rule from its rendering on a surface:
system prompt, managed instruction, project file, user message, tool
description, skill, or another explicitly supported channel. The runner records
both the intended surface plan and the effective surface after discovery,
precedence, imports, filtering, and truncation.

### Evidence over impression

Each rule opportunity must have an auditable verifier whenever feasible. A final
score is derived from structured evidence, not only from the model's narrative
claim that it followed a rule.

### Reproducible external execution

Generated execution packages and run data are content-addressed or versioned and
stored under an external output root. The Git repository remains reviewable and
portable; a run can still be reconstructed from its lock manifest and hashes.

## 3. System layers

```text
+----------------------+     +-------------------------+
| Source and curation  | --> | Canonical benchmark     |
| extraction, review   |     | rules and task assets   |
+----------------------+     +-------------------------+
                                      |
                                      v
                            +-------------------------+
                            | Item / Pair compiler   |
                            | validation and release |
                            +-------------------------+
                                      |
                                      v
                            +-------------------------+
                            | Backend Pack compiler  |
                            | (Harbor first)         |
                            +-------------------------+
                                      |
                                      v
                            +-------------------------+
                            | Runner and harness     |
                            | adapter (StepCLI first)|
                            +-------------------------+
                                      |
                                      v
                            +-------------------------+
                            | Trial evidence         |
                            | verifier + artifact    |
                            +-------------------------+
                                      |
                                      v
                            +-------------------------+
                            | Normalization and      |
                            | cross-run analysis     |
                            +-------------------------+
```

The layers communicate through versioned manifests, but their implementations
are intentionally not being specified in this scaffold.

## 4. Data production lifecycle

### 4.1 Source intake

Source metadata and permitted excerpts are collected from open-source
repositories, documentation, and other approved material. Large source trees
are referenced by immutable revision or archive hash rather than copied into
the Git repository by default.

An LLM may propose candidate rules, task ideas, paraphrases, or verifier plans.
Every proposal keeps its source provenance and review state.

### 4.2 Canonicalization

Candidate rules are normalized into reusable semantic units. A canonical rule is
not tied to a product name or a particular file name unless the experiment is
explicitly testing that product-specific behavior. Surface-specific wording is
kept as a rendering or template, not mixed into the rule's meaning.

Tasks are represented by neutral goals plus a reproducible fixture reference.
Small synthetic repositories can live in the source tree. Large repositories,
dependency caches, and generated workspaces are external inputs pinned by
revision and checksum.

### 4.3 Item and pair construction

An Item binds reusable assets into one experimental condition. Its conceptual
inputs are:

- task reference and fixture;
- one or more rule references and their roles;
- surface placement and rendering target;
- authority, precedence, and conflict policy;
- verifier reference and observable evidence;
- provenance, version, and compatibility metadata.

The experiment layer should group a baseline and an intervention under a stable
pair identifier. A pair may later expand to multiple controlled surface
variants, but each variant must identify its intended difference.

The eventual authored format may be YAML validated by JSON Schema and compiled
to canonical JSON. This document intentionally does not define those schemas.

### 4.4 Qualification and release

Before an Item is released, the curation pipeline checks structure, semantic
clarity, rule/task compatibility, surface support, verifier availability,
behavioral opportunity, and leakage risk. A small qualification run may be
needed to establish that the constrained behavior differs from the baseline
behavior. Failed or ambiguous candidates remain outside the released split.

## 5. Execution lifecycle

```text
released Item / Pair
        -> experiment selection and run config
        -> immutable backend Pack
        -> isolated trial workspace
        -> surface materialization
        -> StepCLI execution
        -> raw event and workspace capture
        -> per-trial verification
        -> normalized run record
        -> aggregate analysis and report
```

### 5.1 Experiment selection

An experiment configuration selects Items or pairs, model/provider settings,
harness profile, backend, repetition count, random seeds, resource limits, and
the external output root. These run parameters are not part of the semantic
Item.

### 5.2 Pack compilation

The Pack compiler translates a semantic Item into the format expected by the
chosen backend. A Pack may contain task instructions, fixture/build material,
public project files or skills, verifier entry points, and provenance metadata.

Packs are generated inputs and should be immutable once referenced by a run.
They are stored outside the source repository and identified by a hash.

### 5.3 Harness integration

The StepCLI adapter is responsible for delivering each declared surface through
the actual StepCLI extension/configuration or workspace mechanism. It must not
silently turn independent surfaces into one undifferentiated prompt. It should
emit an effective-surface snapshot before the first model call, including loaded
files, resolved prompt contributions, available tools, source references, and
stable hashes where the harness exposes them.

The adapter also preserves native StepCLI events. A normalized trajectory format
can be derived later, but must not replace raw evidence.

Harbor is a suitable first execution backend because it already models isolated
tasks, environments, tests, and agent execution. The research contracts remain
backend-neutral so that a later runner can reuse the same Item and Pack
semantics.

## 6. Verification and analysis

Verification is trial-local. It evaluates the final workspace, file diff,
tests, tool events, and other declared evidence, then emits rule-level and
task-level verdicts. It should distinguish at least model behavior failure from
instruction delivery failure and infrastructure failure.

Analysis is cross-trial. It ingests verified evidence, validates artifact
completeness, pairs baseline and intervention runs, computes rule-opportunity
metrics, and produces aggregate tables, confidence intervals, comparisons, and
reports. Generated normalized data and reports stay outside Git.

The primary scoring unit is a rule opportunity in a particular run. Analysis
must retain enough information to report conditional scores, behavior-diff
subsets, baseline comparisons, and delivery-failure rates separately.

## 7. Runtime output boundary

The recommended external layout is:

```text
<output_root>/<experiment_id>/
├── experiment.lock.json
├── packs/
├── harbor/jobs/
├── artifacts/
├── normalized/
├── reports/
└── cache/
```

`workspace/` is a per-trial runtime resource. By default, retain manifests,
before/after file inventories, diffs, verifier evidence, and references to raw
logs; retain full snapshots only under an explicit storage policy.

## 8. Extensibility

Future harness adapters should implement the same high-level contract:

```text
compile surface -> materialize -> snapshot effective surface -> run -> collect
```

Pi and Codex can then be added without changing the meaning of a canonical rule
or task. A multi-agent track should introduce explicit actors, delegation, and
communication surfaces as additional dimensions rather than changing the
single-agent score definition.

## 9. Open design decisions

The scaffold deliberately leaves these for a later design review:

- the formal schemas and compatibility/versioning rules;
- the exact surface vocabulary and StepCLI injection protocol;
- the public/private manifest boundary implementation;
- the first rule families, task families, and deterministic verifiers;
- qualification thresholds and release/split policy;
- Harbor adapter versus a thin independent runner;
- artifact retention, object storage, and cache policy.
