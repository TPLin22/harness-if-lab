# Task Sourcing and Representation

**Status:** candidate task panel collected and agent-reviewed on 2026-08-27;
not a released benchmark and not a runtime package.

This document defines how the first coding-task pool is selected and represented
in Harness-IF Lab. It deliberately describes a thin semantic task record rather
than a Harbor task schema. The formal `TaskSpec` contract is introduced only
after the first records have exposed the fields that can actually be filled.

## 1. What is being stored

The repository stores enough information to identify, review, and compose a
coding task. It does not store a complete runnable task directory.

The objects have different ownership and lifetimes:

| Object | Meaning | Stored in Git? | Created when |
| --- | --- | --- | --- |
| Upstream record | The row in SWE-bench Multilingual or another source dataset | No; referenced by revision and ID | Source lookup |
| `TaskSpec` | A thin, reviewable semantic description of one task | Yes, after review (or candidate status during intake) | Task curation |
| Task index | A frozen selection and sampling manifest | Yes | Panel construction |
| `Item` | One experimental condition: one task plus rule bindings and policy | Yes, after review | Item assembly |
| Harbor Pack | A backend-specific runnable task package | No; external output | Pack compilation |
| Workspace / Trial | One isolated execution and its mutable state | No; external output | Runtime |

The resulting dependency chain is:

```text
SWE-bench row (pinned revision)
        -> TaskSpec (thin, reviewable)
        -> Item (task + one or more rule bindings)
        -> Harbor Pack (generated task directory)
        -> Harbor Trial / StepCLI run
```

`TaskSpec` is therefore not a copy of the Harbor task package, and an Item is
not a pre-rendered prompt. Both remain backend-neutral inputs to later
compilers.

The index, provenance fields, upstream dataset name, and evaluator references are
compiler metadata. They are not mounted or passed to the model; only the
reviewed neutral task content and the deliberately delivered rule surfaces enter
the model-visible context.

## 2. First task pool: SWE-bench Multilingual

The initial pilot uses the `test` split of
`SWE-bench/SWE-bench_Multilingual`. The local Harbor checkout currently contains
300 generated tasks and the local Hugging Face cache resolves the dataset
`main` ref to revision
`e5c585e008e2cb5eecc7c64192d855c53279d788`. That revision and the parquet
content hash are recorded in the checked-in panel index; they are a candidate
pin, not an automatic release decision.

The pilot target is approximately 20 instances. The selection must be a fixed
manifest, not a command that samples afresh each run. At minimum, the manifest
records:

- upstream dataset name, configuration, split, and immutable revision;
- population size after deterministic filters;
- sampling method, stratum definition/allocation (if applicable), and seed;
- selection/filter implementation version or hash;
- the final ordered `selected_ids` list;
- language and repository counts for the selected list;
- exclusions, replacements, and their reasons;
- the task-spec revision or content hash for every selected ID.

Recording the final IDs is mandatory even when a seed is recorded. Dataset row
order, upstream revisions, and filtering code can change; a seed alone does not
identify the experiment.

### 2.1 Recommended sampling policy

For a harness-following pilot, first apply only deterministic intake filters,
then use a reproducible random sample with lightweight coverage constraints:
sample by language (and cap repeated repositories), then draw randomly within
each stratum. This avoids a 20-task panel becoming an accidental test of one
dominant language or repository while preserving a clear randomization story.

If the study specifically requires an i.i.d. population estimate, use a pure
random sample instead and report the resulting language/repository imbalance.
If a constrained/stratified sample is used for a capability panel, report its
selection probabilities or stratum weights and do not present an unweighted
panel average as an estimate of the full dataset population. The choice is an
experiment decision, not something the TaskSpec should encode.

Either policy should keep a reserve list generated from the same pinned
population. A replacement may be used only before a release is frozen and must
be recorded in the index; after release, the selected list is immutable.

### 2.1.1 Collected pilot snapshot

The current candidate panel applies the deterministic filters above to a
300-row population, leaving 279 eligible rows. It selects 20 rows with one task
per repository and the following language allocation:

```text
c 2 | cpp 2 | go 3 | java 3 | javascript 3 | php 2 | ruby 2 | rust 3
```

The selection seed is `260827`; eight reserve IDs (one per language) are kept
in the index but do not yet have TaskSpecs. Exclusions are recorded with their
IDs and reasons. The exact ordered IDs, repository/language counts, source
parquet SHA-256 (`28b7f874e48496399077d276f9f2b163a077ddf0a70dc507c148d58da826baa9`),
and collection-program SHA-256 are in
[`benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml`](../benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml).

The 20 specs were checked against the pinned parquet snapshot by recomputing
each full source-row hash. The agent review is recorded in
[`swebench-multilingual-pilot-20-review.yaml`](../benchmark/tasks/indexes/swebench-multilingual-pilot-20-review.yaml).
That ledger accepts the records as candidates for pipeline work while flagging
solution/workaround wording, issue-template residue, and unusually detailed
diagnostics for a later release decision. It does not promote any record to a
released benchmark.

### 2.2 Task-level eligibility screening

Selection and eligibility are separate operations. The intake pass may mark a
task as `candidate`, `excluded`, or `needs_review` without deleting its source
reference. Screening should check, at least:

- the problem statement is present and readable after deterministic cleanup;
- the base commit and repository identity are resolvable;
- the language and runtime metadata are known;
- a Harbor/evaluator materializer can locate the hidden tests and oracle data;
- the chosen Harbor verifier mode keeps solution/test oracle files out of the
  agent-readable environment (this must be checked at package qualification,
  not assumed from directory names);
- the task has plausible opportunities for the rule families planned for the
  first Item panel;
- the model-visible statement does not contain an answer, gold patch, or
  evaluator-only hint.
- benchmark/dataset framing is removed when it is not part of the coding
  objective, while task-relevant repository context is preserved;

This screening does not decide whether a rule is contaminated by training or
whether a rule is difficult enough. Those are later rule and qualification
decisions. Do not use model success, expected compliance, or an early rule
score as a task-selection filter; doing so would make the task panel
post-treatment.

## 3. Repository layout for tasks

The task area should eventually look like this (empty directories remain valid
until records are reviewed):

```text
benchmark/tasks/
|-- indexes/
|   |-- swebench-multilingual-pilot-20.yaml
|   `-- swebench-multilingual-pilot-20-review.yaml
|-- specs/
|   `-- swebench-multilingual/
|       |-- <instance-id>.yaml
|       `-- ...
|-- fixtures/
|   `-- <small-synthetic-fixture>/
`-- generators/
```

`indexes/` answers **which tasks belong to a named panel** and stores panel-level
review ledgers. `specs/` answers
**what one selected task is and where its source/evaluator data comes from**.
`fixtures/` is only for small synthetic repositories that are intentionally
versioned with this project; it is not a place to copy SWE-bench repositories.

One file per task is preferred over one large file. It gives reviewers a small
diff, permits task-level ownership and status, and lets an Item refer to a
stable task ID without duplicating the task text. An index may still be the
source of truth for a pilot's selected order. Before the formal contract is
approved, candidate specs may use the same `specs/` location with a candidate
status; a separate task-candidate directory is not required for the first pilot.

The following is an illustrative shape only. It is intentionally not a schema
and must not be treated as a validation spec before the contract review:

```yaml
# benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml
dataset: SWE-bench/SWE-bench_Multilingual
split: test
revision: <immutable-dataset-revision>
population:
  size_after_filters: 300
  filters: []
sampling:
  method: language_stratified_random
  seed: <seed>
selected_ids: [<instance-id>, ...]
reserve_ids: [<instance-id>, ...]
```

```yaml
# benchmark/tasks/specs/swebench-multilingual/<instance-id>.yaml
task_id: swebench-multilingual/<instance-id>
source:
  dataset: SWE-bench/SWE-bench_Multilingual
  split: test
  revision: <same-revision-as-index>
  instance_id: <instance-id>
content:
  problem_statement: <cleaned-neutral-task-text>
  hints_policy: omitted
repository:
  repo: <owner>/<name>
  base_commit: <commit>
  language: <language>
offers_opportunity: [<tag>, ...]
evaluator_ref:
  provider: swebench_multilingual
  source_row_hash: <hash>
  evaluator_revision: <evaluator-revision-if-applicable>
status: candidate
```

The actual field names, status vocabulary, and hash algorithm remain subject to
the Phase 1 contract review. The pilot records below are a concrete intake
snapshot that exercises the proposed shape; they do not freeze the formal
schema.

## 4. Thin `TaskSpec` content

The eventual contract is not being frozen here. The following field groups are
the minimum information the first intake should try to capture.

### 4.1 Identity and source pin

- stable local `task_id` (for example, a namespaced form of the upstream
  `instance_id`);
- provider/dataset name, configuration, and split;
- upstream `instance_id`;
- immutable dataset revision and row/content hash;
- retrieval date and intake-tool version;
- dataset/license and redistribution status, where available.

The local ID must not depend on a local filesystem path. If an upstream ID is
renamed, the old ID remains an alias recorded in provenance rather than silently
becoming a different task. A filename-safe representation may be used on disk,
but the logical ID and its mapping must remain explicit.

### 4.2 Model-visible task content

- the cleaned `problem_statement` that will become the neutral coding objective;
- a deterministic normalization record (for example, canary removal or
  whitespace normalization, benchmark-framing removal) and the hash of the
  resulting text; retain a raw-text hash for audit even when raw text is not
  redistributed;
- an explicit hints policy. The default for this project is to omit
  `hints_text`, because maintainer discussion and workaround hints can leak the
  intended solution or change the task from a coding request into a discussion;
- optional neutral task framing metadata, kept separate from rule renderings.

For a 20-task pilot, retaining the cleaned problem statement inline in the
TaskSpec is recommended. It is small, reviewable, and makes Pack generation
auditable even if the upstream dataset later changes. The upstream reference
and hash remain authoritative for provenance. If licensing or policy later
requires the text to remain external, the same field can instead contain an
immutable blob reference and hash; that choice must be made before release, not
per task.

The statement is task content, not a rule surface. A compiler must not rewrite
it by appending rules when constructing the semantic Item. The later harness
adapter decides how a `user_message` or other surface is materialized.

Any generic agent/task framing (for example, a Harbor prompt template) is a
fixed harness/run configuration and must be held constant across a
baseline/intervention pair. It is not a substitute for, or an implicit part of,
the rule-surface assignment.

Dataset names, local task IDs, and provenance labels are compiler metadata. They
should not be injected into the model-visible instruction merely to identify the
benchmark; the Harbor package qualification pass must check any remaining task
names or environment variables for the same leakage risk.

### 4.3 Repository and execution hints

- repository slug and base commit;
- upstream version/release identifier when provided;
- programming language and optionally a coarse stack/category;
- difficulty only as upstream metadata, not as a measured capability score;
- an initial-state or `fixture_ref` describing where the materializer obtains
  the working tree (external repository/base commit for SWE-bench, or a small
  versioned fixture for a synthetic task);
- a coarse evaluator/verifier kind, without embedding hidden test content;
- tags describing likely observable opportunities (for example, `new-file`,
  `api-change`, `test-change`, `error-handling`, `tool-event`).

Opportunity tags are curation annotations. They help match a rule to a task but
do not assert that the opportunity occurred in a particular run. Run-time
verifiers decide that later.

Derived metadata such as language, stack, or opportunity tags should retain its
derivation method/version so a later materializer change cannot silently alter
the panel.

### 4.4 Evaluator-only reference

The TaskSpec should carry an opaque reference to the evaluator material needed
to build a runnable task, plus its revision/hash. For SWE-bench this can point
to the upstream row and evaluator version. The particular Harbor or other
backend materializer revision is compiler/run metadata recorded in the
experiment lock, not a requirement of the semantic TaskSpec.

The following must not be part of the model-visible TaskSpec or Item input:

- `patch` and `test_patch`;
- `FAIL_TO_PASS` and `PASS_TO_PASS` oracle lists;
- generated test scripts, solution scripts, or hidden verifier prompts;
- Docker image contents, full repository snapshots, dependency caches, and local
  absolute paths;
- credentials or private evaluator configuration.

The evaluator reference may resolve to an external task cache at run time. A
cache location is a deployment setting, not a field in a released task ID. A
typical external layout is:

```text
<task_cache_root>/
`-- swebench-multilingual/<dataset-revision>/<instance-id>/
    |-- source-record.json       # evaluator-only
    |-- materializer-lock.json
    `-- optional downloaded data
```

The cache is read by the Pack compiler/materializer and verifier, never mounted
as a model-readable source directory. The experiment lock records the cache
revision and content hashes so a run can be reconstructed.

The existing Harbor checkout's generated
`datasets/swebench_multilingual/<instance-id>/` directories can be used as a
local materialization cache while developing. They are not the canonical task
records and should not be added as a submodule or copied into this repository.
The runtime configuration may point at that checkout locally; a released lock
must still record the upstream revision, Harbor/materializer commit, and hashes
rather than relying on a machine-specific path.

### 4.5 Mapping the current SWE-bench row

The current dataset exposes the following fields. This mapping is a curation
decision, not a claim that the upstream names become our public schema:

| Upstream field | TaskSpec treatment |
| --- | --- |
| `instance_id` | Stable upstream identity under the source pin |
| `repo` | Repository metadata used by the materializer |
| `base_commit` | Initial-state pin for the evaluator/materializer |
| `version` | Retain as upstream metadata when present |
| `problem_statement` | Cleaned model-visible task text |
| `hints_text` | Omit by default; retain only a reviewed policy/reference |
| `created_at` | Provenance metadata, if needed for audit |
| `patch`, `test_patch` | Evaluator-only cache/reference; never Item input |
| `FAIL_TO_PASS`, `PASS_TO_PASS` | Evaluator-only test oracle/reference |

This keeps the task objective available to the Pack compiler while preventing
the gold solution and grading oracle from becoming accidental prompt context.
The materializer should use an explicit allowlist when projecting the upstream
row into the agent package; loading a raw row object and filtering by convention
is not sufficient for a released run.

## 5. How tasks combine with rules

Task collection stops at `TaskSpec`. Item assembly is a separate, later step.
An Item references one `task_ref` and any number of rule bindings. Each binding
has its own semantic target surface, role, and optional authority metadata; the
rules must not be flattened into one string before the harness adapter sees the
plan.

When several bindings share a surface, the eventual contract may also carry a
stable surface slot/group and an explicit order. That order is part of the
experimental plan and must not be inferred from incidental YAML or filesystem
ordering. The adapter may render a group into one harness channel only after it
has preserved the individual binding identities in its delivery manifest.

The neutral task statement and a rule assigned to `user_message` are separate
logical segments even if the target harness sends them in one user turn. Their
boundaries and hashes should remain distinguishable in the intended-surface
record.

Authority and precedence are an Item-level policy, not an accidental consequence
of string concatenation. A policy can describe the intended relation between
surfaces (for example, a normal user override, a protected project rule, or an
explicit conflict experiment), while a binding can identify the authority class
it is testing. The exact policy vocabulary and ordering are still open. Baseline
and intervention variants must keep the policy fixed unless precedence itself
is the declared intervention.

Non-normative policy examples make the intended distinction concrete:

| Policy intent | Abstract relation | Experimental use |
| --- | --- | --- |
| Normal override | `user_message` may override a general `project_file` rule | Temporary user request |
| Protected project | A declared `project_file` rule outranks a conflicting user request | Repository safety/convention gate |
| Explicit conflict | Two bindings intentionally conflict and the expected winner is declared | Precedence track only |

The relation is evaluated from the effective harness behavior, not assumed from
the table. An unsupported or unexpectedly reordered relation is a delivery or
policy failure that must be recorded separately from rule compliance.

Conceptually (illustrative, not a formal schema):

```text
item
  task_ref: swebench-multilingual/<instance-id>
  rule_bindings:
    - binding_id: b-01
      rule_ref: rule/<id-a>
      role: scored
      target_surface: project_file
    - binding_id: b-02
      rule_ref: rule/<id-b>
      role: observed
      target_surface: system_prompt
  authority_policy: <backend-neutral policy reference>
  tool_set_ref: null  # optional; null means the harness-native/default set
```

The first version should treat one binding as one target surface. If the same
rule is intentionally delivered on two surfaces, represent two explicit
bindings linked by a duplication/group marker. This keeps a rule-surface
opportunity attributable and makes accidental multi-surface delivery visible.
Whether to permit that in the released panel is an open review decision.

An Item may have a baseline/intervention relationship. The baseline uses the
same TaskSpec and all unrelated settings, while omitting or changing only the
declared intervention. Whether the repository stores a separate `Pair` object
or two Item records under a pair ID is a contract decision; neither option
changes TaskSpec storage.

## 6. Boundary with Harbor and StepCLI

Task collection needs to understand the future runtime, but it does not need to
depend on either codebase or generate a runnable package now.

### 6.1 Harbor Pack compiler

`compilers/harbor` consumes a TaskSpec and Item and creates a complete Harbor
task package under the external output root. For SWE-bench, that package will
typically contain `task.toml`, a neutral `instruction.md`, environment setup,
tests, and evaluator hooks. It may obtain hidden patch/test data from the
external task cache.

The compiler owns backend packaging concerns such as task naming, image
selection, and Harbor verifier configuration. It does not decide that a
semantic `project_file` rule means a particular StepCLI filename.

Harbor currently loads one task instruction string; `extra_instruction_paths`
append more text to that same channel. This is useful for the base task and for
simple experiments, but it is not an independent-surface abstraction. The
design must not claim that two separately declared surfaces remain separate
merely because Harbor accepted two files.

### 6.2 StepCLI harness adapter

`harnesses/stepcli` receives the Item's surface plan after Pack/workspace
materialization and maps semantic surfaces to actual StepCLI inputs. That
mapping is deliberately deferred implementation work. It may use system-prompt
configuration, discovered project instruction files, user-message injection,
tool presentation/description configuration, skills, or a future StepCLI API.

The adapter needs a pre-run materialization boundary: given a fresh workspace,
the Pack context, and an Item, it prepares all requested surfaces and the
optional tool set before starting the StepCLI process or making its first model
call, then returns a delivery manifest. Whether this boundary is implemented as
a Harbor setup hook, an agent wrapper, or a StepCLI-native API is a Phase 4
decision.

The adapter must record, for every binding:

1. intended surface and rendering identity from the Item;
2. actual delivery target and content hash;
3. effective surface observed by StepCLI (loaded files, prompt contribution,
   exposed tools, imports, truncation, and precedence);
4. delivery status, including `delivered`, `unsupported`, `truncated`,
   `merged`, `misrouted`, or `infrastructure_failure`.

A delivery failure, including an unintended merge of surfaces, is diagnostic
data and must not be scored as a model rule violation. This is why the Item
remains semantic and the adapter owns the backend-specific mapping.

### 6.3 Future tool-set replacement

The recommended location is an optional, backend-neutral `tool_set_ref` on the
Item (with a backend-specific resolution recorded in the run lock). It is
independent of a rule whose target is `tool_description`.

The reference may eventually identify a complete tool-set definition covering
some or all of:

- tool registry and names;
- input/output schemas and presentations;
- tool descriptions;
- implementation/backend;
- permissions and approval policy.

When a rule binding targets `tool_description`, the future Item/adapter
contract should also be able to identify which exposed tool(s) it concerns and
check that those tools exist in the selected tool set. This relationship is
validated explicitly; it is not encoded by copying tool names into a generic
rule string.

The first implementation need not support any non-native tool set. The default
value means the harness-native tool set. A future StepCLI capability adapter
negotiates and materializes the reference, reports unsupported dimensions, and
records the effective tool set. Item data must not contain StepCLI config keys,
CLI flags, or internal class names, so that replacing the implementation does
not require rewriting the benchmark model.

## 7. What must be designed now versus later

The task collection phase should settle only the contracts needed to make task
references stable and reviewable:

- the upstream dataset revision, selection index, and replacement policy;
- the thin TaskSpec fields, visibility boundary, and content/evaluator hashes;
- the external task-cache interface and the materializer identity recorded in a
  lock manifest;
- neutral opportunity tags and task eligibility status.

It should not depend on a Harbor or StepCLI process. The following belong to the
later execution implementation:

- conversion of a TaskSpec/Item into `task.toml`, `instruction.md`, images,
  tests, and hooks;
- mapping each Item binding to a concrete StepCLI system prompt, instruction
  file, user message, tool description, or skill;
- materializing and validating an optional complete tool set;
- lifecycle hooks, event capture, verifier execution, and analysis.

The only coupling needed now is a documented *reference* to the future
materializer and adapter capabilities. This keeps task curation moving while
making it impossible for a later implementation to silently change what a
selected task means.

## 8. Construction order

The recommended order for the first pilot is:

1. Pin the upstream dataset revision and agree on the sampling policy.
2. Generate a fixed index with about 20 selected IDs plus a reserve list.
3. Fetch only the selected rows and create thin TaskSpec candidates.
4. Review deterministic cleanup, task visibility, evaluator references, and
   opportunity tags.
5. Promote reviewed TaskSpecs into `benchmark/tasks/specs/`.
6. Assemble candidate Items by joining task refs to cleaned rule refs; validate
   surface assignment, authority policy, and verifier coverage.
7. Only then implement the Item/Pack compiler and the StepCLI adapter.

Steps 1--5 do not require a Harbor process, a StepCLI process, or a generated
workspace. A small Harbor/StepCLI smoke trial belongs after the semantic
contracts are reviewed. Runtime Packs, workspaces, logs, and reports remain
under an explicitly configured external `output_root`.

## 9. Decisions for review

The following are the remaining choices that materially affect the first task
manifest. Defaults are recommendations, not silently adopted facts.

| Decision | Recommended default | Why it matters |
| --- | --- | --- |
| Dataset revision | Pin the currently observed revision, then record it in the index | Upstream `main` is mutable |
| Count | Exactly 20 selected tasks plus 5--10 reserve candidates | Makes the pilot and replacement policy concrete |
| Sampling | Language-aware random sampling with a repository cap | Preserves randomization while reducing panel confounds |
| Duplicate repositories | Allow repeats only up to an agreed cap | SWE-bench has multiple rows per repository |
| Problem statement | Store cleaned text inline and retain upstream hash | Keeps the thin spec self-contained and reviewable |
| Hints | Omit `hints_text` by default | Avoids discussion/solution leakage |
| Evaluator cache | External shared/local cache selected by runtime config | Keeps patches and images out of Git and model context |
| Rule cardinality | One target surface per binding; duplicate intentionally via two bindings | Preserves rule-surface attribution |
| Surface vocabulary | Start with backend-neutral names, then approve a fixed v1 enum | Prevents StepCLI details leaking into Items |
| Authority policy | Name explicit normal/override/protected/conflict policies | Makes precedence an experimental factor rather than string order |
| Ambient instructions | Fail or isolate on unexpected pre-existing instructions; preserve only in a declared track | Avoids home/workspace guidance becoming an unmeasured confounder |
| Tool set | Optional top-level Item reference; default is native tools | Leaves room for whole-tool replacement |
| Baseline organization | Stable pair ID over separate baseline/intervention Items | Avoids duplicating TaskSpecs and supports extensions |

The first decisions to confirm before task collection are the sampling
policy/count, whether inline task text is acceptable, and the external
evaluator-cache location. Surface vocabulary and the remaining Item choices can
stay provisional through the TaskSpec collection pass if their metadata is
retained.

Decision timing is therefore:

- **Before task collection:** dataset revision, split, sample count/seed,
  sampling and duplicate-repository policy, and task-text/hints retention;
- **Before Item assembly:** surface vocabulary/cardinality, authority policy,
  baseline representation, and the semantics of `tool_set_ref`;
- **Before execution:** ambient-instruction isolation and the concrete Harbor /
  StepCLI materialization mechanism.

## 10. References used for this boundary

The representation follows the local Harbor and StepCLI implementations as they
exist at the time of writing, not as permanent API guarantees:

- Harbor SWE-bench Multilingual adapter:
  `harbor/adapters/swebench_multilingual/src/swebench_multilingual/adapter.py`
  (builds a full task directory from an upstream row and intentionally keeps
  `instruction.md` thin);
- Harbor Task and Trial lifecycle:
  `harbor/src/harbor/models/task/task.py` and
  `harbor/src/harbor/trial/trial.py` (task package loading, extra instruction
  appending, isolated agent/verifier stages);
- StepCLI instruction discovery and runtime inspection:
  `step-cli/src/bootstrap/prompt/instruction-files.ts` and
  `step-cli/src/runtime/runtime-config.ts`;
- Harness-IF, arXiv:2608.11727, for the separation of task/scenario, rule,
  surface, and item and for rule-level opportunity scoring.

These references justify the boundaries. They do not turn Harbor's current
directory format or StepCLI's current option names into this repository's
canonical schema.
