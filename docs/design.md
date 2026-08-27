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

### 3.1 Object boundaries

The following boundaries are important enough to keep explicit throughout the
implementation:

| Object | Owns | Does not own |
| --- | --- | --- |
| `TaskSpec` | A thin, reviewable neutral task description, source pin, and evaluator reference | Harbor directory layout, rule text, or a live workspace |
| Task index | A reproducible panel selection and sampling record | Task content or Item composition |
| `Item` | One task reference, one or more rule bindings, surface/policy assignments, and optional tool-set reference | StepCLI config keys, generated prompts, or hidden oracle data |
| `Pack` | Backend-specific generated input package | Canonical benchmark meaning or mutable run state |
| `Trial` | One isolated execution, native events, and evidence | Reusable task/rule definitions |

The same `TaskSpec` may participate in many Items. The same rule may occur in
many Items, with a different role or target surface recorded in each binding.
This reuse is intentional; the repository must not materialize a permanent
task-by-rule Cartesian product.

## 4. Data production lifecycle

### 4.1 Source intake

Source metadata and permitted excerpts are collected from open-source
repositories, documentation, and other approved material. Large source trees
are referenced by immutable revision or archive hash rather than copied into
the Git repository by default.

An LLM may propose candidate rules, task ideas, paraphrases, or verifier plans.
Every proposal keeps its source provenance and review state.

The initial source selection is recorded in the
[Phase 0 source shortlist](source-shortlist.md). It intentionally contains both
human-facing project guidance and real harness-native instruction files. Both
are eligible for the same cleaning path; `source_pool` remains a separate
annotation so later contamination, product-specificity, and task-opportunity
analysis can be applied without discarding material during intake.

### 4.2 Canonicalization

Candidate rules are normalized into reusable semantic units. A canonical rule is
not tied to a product name or a particular file name unless the experiment is
explicitly testing that product-specific behavior. Surface-specific wording is
kept as a rendering or template, not mixed into the rule's meaning.

Tasks are represented by a thin `TaskSpec`: a neutral objective, a pinned
upstream/source reference, cleaned model-visible task text, repository/base
commit metadata, opportunity annotations, and an evaluator-only reference.
For the first SWE-bench Multilingual pilot, the selected IDs live in a fixed
index and the individual specs live under `benchmark/tasks/specs/`; complete
Harbor packages and downloaded repositories remain external. See
[Task sourcing and representation](task-sourcing.md) for the collection
contract and the explicit list of fields that must stay evaluator-only.

Small synthetic repositories can live in the source tree. Large repositories,
dependency caches, evaluator records, and generated workspaces are external
inputs pinned by revision and checksum.

### 4.3 Item and pair construction

An Item binds reusable assets into one experimental condition. Its conceptual
inputs are:

- task reference and fixture;
- one or more rule bindings, each with a role and an independently controlled
  semantic target surface;
- authority, precedence, and conflict policy;
- verifier reference and observable evidence;
- an optional backend-neutral tool-set reference;
- provenance, version, and compatibility metadata.

The Item stores the *plan*, not the rendered StepCLI configuration. A binding
such as `target_surface: project_file` says what experimental surface is meant;
it does not say which filename, CLI flag, or internal StepCLI option implements
it. The latter belongs to the target harness adapter.

Authority and precedence are represented by an Item-level policy plus any
per-binding authority class needed for the experiment. They must not be inferred
from the order in which a compiler happened to concatenate strings. A normal
override, a protected project rule, and an explicit conflict experiment are
different conditions and should be named as such; the policy vocabulary remains
pending review.

One binding has one target surface by default. Intentional delivery of the same
rule to several surfaces must be represented as several explicit bindings so
that the rule-surface opportunity and any delivery failure remain observable.
Whether multi-surface duplication is admitted to the first released panel is an
open decision.

The proposed semantic vocabulary (pending Phase 1 approval) is:

| Surface | Semantic meaning |
| --- | --- |
| `system_prompt` | Harness-level system context supplied for the condition |
| `managed_instruction` | Organization/provider-managed instruction layer |
| `global_instruction` | User- or account-level instruction discovered outside the project |
| `project_file` | Repository/workspace instruction file or equivalent project context |
| `user_message` | The task turn or an additional user-level instruction |
| `tool_description` | Text/schema presented alongside an exposed tool |
| `skill` | On-demand or preloaded workflow instruction resource |

These names describe experimental surfaces, not StepCLI filenames, flags, or
configuration keys. A future harness may merge, split, or lack one of them; the
adapter must report that fact in the effective-surface record.

The experiment layer should group a baseline and an intervention under a stable
pair identifier. A pair may later expand to multiple controlled surface
variants, but each variant must identify its intended difference.

For the first candidate panel, the repository uses one `hif.item_pair` YAML
file per task under `benchmark/items/pairs/`. The file contains a zero-injection
baseline and a multi-rule intervention, so their shared TaskSpec reference,
authority policy, optional tool-set factor, and provenance stay together. This
is a provisional representation for data bring-up, not the final schema; the
pair's bindings remain semantic references and are not rendered prompts.

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
the actual StepCLI extension/configuration or workspace mechanism. This is where
an Item binding is mapped to a concrete system prompt, project instruction
file, user message, tool description, skill, or future entry point. It must not
silently turn independent surfaces into one undifferentiated prompt, and the
mapping must not be duplicated in the semantic Item or Harbor compiler.

The adapter needs a pre-run materialization boundary: for a fresh workspace, it
prepares the requested surfaces and optional tool set before the StepCLI process
starts or its first model call is made, then returns a delivery manifest. The
implementation may use a Harbor setup hook, an agent wrapper, or a future
StepCLI-native API; that choice is deferred to the execution phase.

Before the first model call, the adapter should emit an effective-surface
snapshot for every binding, including intended surface, actual target, loaded
files, resolved prompt contributions, available tools, source references,
precedence/import behavior, truncation, and stable content hashes where the
harness exposes them. A binding can therefore be classified as delivered,
unsupported, truncated, merged, misrouted, or infrastructure-failed
independently of the model's later behavior. An unintended merge is a delivery
failure, not evidence that the model ignored a rule.

The Item may also carry an optional top-level `tool_set_ref` (with a
backend-specific resolution recorded in the run lock). This is separate from a
`tool_description` rule surface: the former is an experimental request for a
tool-set capability, while the latter is a rule about what a tool description
should say or do. A future adapter may materialize a complete registry,
schemas/presentations, implementations, and permission policy from the
reference. The default reference means the harness-native tool set; current
work only reserves the field and records unsupported capability.

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

The external `cache/` may include run-local derived task materializations keyed by
the upstream dataset revision and task ID. A shared/reusable source or
evaluator cache may instead be configured through `HIF_TASK_CACHE` outside this
experiment directory. In either location it is an evaluator/compiler input,
not a benchmark source directory and not a model-visible mount.

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
- the exact semantic surface vocabulary, StepCLI injection protocol, and
  capability matrix;
- whether every rule binding is restricted to one target surface, or whether
  intentional multi-surface delivery is allowed in released Items;
- the minimum semantics of `tool_set_ref` (registry only versus registry,
  presentation, implementation, and permission policy);
- whether tool-set selection is fully independent of rule surface assignment;
- the public/private manifest boundary implementation;
- TaskSpec task-text retention (inline cleaned text versus external blob) and the
  evaluator-cache provider/location;
- treatment of ambient instructions already present in a workspace or home
  directory (clear, preserve, controlled fixture, or fail on unexpected input);
- the first SWE-bench sample count, randomization/stratification policy, seed,
  and duplicate-repository cap;
- the formal baseline/intervention schema and release representation (the
  candidate panel currently uses one Pair object containing two Item variants);
- the first rule families, task families, and deterministic verifiers;
- qualification thresholds and release/split policy;
- Harbor adapter versus a thin independent runner;
- artifact retention, object storage, and cache policy.
