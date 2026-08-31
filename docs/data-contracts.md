# Current Rule and Item Data Contracts

**Status:** maintained current-format reference (2026-08-31)

This document is the single human-readable reference for the Rule and Item
files currently checked into this repository. It documents the shape that the
Phase 0/Phase 1 data and the current compiler actually use. It covers the Rule
library snapshots and review ledger, Item pair files and their indexes/review
ledger, and the boundary to the referenced TaskSpec. The TaskSpec fields
themselves are documented in `docs/task-sourcing.md`.

It is not a JSON Schema and it does not promise that every recorded field is
already consumed by the runtime. The current loaders are intentionally
permissive: a field can be required by a future contract, present in a
candidate, or useful for audit without being required to compile today's smoke
Pack.

When this document conflicts with an older dated plan, this document describes
the current storage shape. The overall boundaries in `AGENTS.md`,
`docs/design.md`, and `docs/constraints.md` remain authoritative for design
decisions that are not field-level details.

## Status vocabulary

Every field below has an implementation status. The status is deliberately
separate from whether a field is useful to the research project.

| Status | Meaning |
| --- | --- |
| `runtime` | The current loader, HIF compiler, or StepCLI adapter consumes the field for validation, identity, routing, or payload generation; it can affect acceptance or generated delivery. |
| `assembly` | The current candidate generator or lint uses the field before a run, but the runtime does not consume it as an instruction. |
| `recorded` | The field is retained for provenance, review, or reproducibility and has no current behavioral effect. |
| `planned` | The field or behavior is described for a future contract but is not implemented in the current data/code path. |

The current YAML files are candidate artifacts. A field being populated does
not mean that it is an experimentally validated factor, and a field being
`recorded` does not mean that it should be deleted: provenance and review data
are still necessary for audit.

## How to read current usage

There are three different questions behind "is a field used?":

1. Is the field required for the current loader to accept a file?
2. Does curation or Item assembly read it to make a candidate or lint decision?
3. Does the delivery compiler use it to change what reaches StepCLI?

The status column answers the second and third questions. Requiredness is
listed separately below because the current loader is intentionally permissive
while the candidate files carry richer review metadata. In particular, a
taxonomy value can be present on every record and still have no experimental
effect.

| Current layer | What is actually working today | What is not yet working |
| --- | --- | --- |
| Stored | Candidate/canonical Rule YAML, TaskSpecs, and Item pair YAML are versioned in Git | No formal machine-readable Rule/Item schema |
| Assembly | Rule/task references, opportunity-tag intersections, surface-fit lint, binding roles, and the must-rule release warning are generated | No empirical prior labels, opportunity witness, or release qualification |
| Delivery | Rule `statement`, selected Item variant, supported `target_surface`, `delivery_order`, and the registered tool projection can affect a generated Pack | No operational authority engine, rule verifier, normalized analysis, or support for the remaining semantic surfaces |

## Storage locations

### Rules

| Path | Contents | Status |
| --- | --- | --- |
| `benchmark/rules/candidates/phase0-candidates.yaml` | LLM-assisted or otherwise provisional rule proposals | Candidate snapshot |
| `benchmark/rules/candidates/phase0-review.yaml` | Candidate-to-canonical review decisions | Review ledger |
| `benchmark/rules/canonical/phase0-canonical.yaml` | Agent-reviewed reusable rule drafts | Canonical draft, not released |
| `benchmark/rules/renderings/` | Reserved for surface-specific renderings | Not implemented |

The current canonical library contains 45 records derived from 44 candidates;
one source candidate was split into two atomic rules. Rules are referenced by
ID from Items; the Item does not normally embed rule text.

### Items

| Path | Contents | Status |
| --- | --- | --- |
| `benchmark/items/pairs/swebench-multilingual/` | One provisional pair file per selected task | Candidate data |
| `benchmark/items/indexes/swebench-multilingual-pilot-20.yaml` | Ordered panel membership and hashes | Candidate index |
| `benchmark/items/indexes/tool-surface-pilot.yaml` | Tool-surface plumbing experiment index | Integration candidate |
| `examples/smoke/*.yaml` | Small executable examples for the current compiler | De facto examples, not normative templates |

An Item file uses `format: hif.item_pair` and keeps a `baseline` and an
`intervention` together. A pair references one TaskSpec and one or more rule
bindings. It contains references and metadata, not a Harbor task directory,
generated prompt files, a live workspace, or evaluator oracle values.

### File-kind map

| File kind | `format` value | Role | Current consumer |
| --- | --- | --- | --- |
| Candidate Rule library | `hif.phase0.rule_candidates` | Provisional extraction output | Curation tools; the delivery loader can read the same `records` shape |
| Rule review ledger | `hif.phase0.rule_review` | Candidate-to-canonical decisions | Human/agent review and audit; not delivery input |
| Canonical Rule library | `hif.phase0.canonical_rules` | Reusable draft Rule records | Item assembly and delivery rule lookup |
| Item pair | `hif.item_pair` | One baseline plus one intervention condition | Item loader, StepCLI delivery adapter, Harbor Pack compiler |
| Item index | `hif.item_index` | Ordered panel membership and file summaries | Curation/review tooling; not a runtime instruction |
| Item review ledger | `hif.item_review` | Candidate disposition and release checks | Human/agent review; not a runtime instruction |

The `format` value is a discriminator, not a versioned schema guarantee. The
current Rule loader checks for a `records` list and `id`/`statement` fields; it
does not enforce the Rule envelope's `format` or `format_version`. The current
Item loader does enforce `format: hif.item_pair`.

### Minimum shape accepted by today's compiler

This is an implementation fact, not the target release schema:

| Input | Required path(s) | Notes |
| --- | --- | --- |
| Rule library passed to `--rules` | `records[]`, `records[].id`, `records[].statement` | Other Rule metadata is preserved but not needed for lookup |
| TaskSpec passed to `--task-spec` | `task_id`, `content.problem_statement` | Full TaskSpec representation is documented separately |
| Item pair passed to `--item` | `format`, `pair_id`, `task_ref`, selected `baseline` or `intervention` mapping | The selected variant must contain `item_id` and a matching `task_ref` |
| Selected Item variant | `rule_bindings[]` (may be omitted, treated as empty) | Each present binding must supply `binding_id`, `rule_ref`, `role`, and `target_surface` |
| Tool-description binding | `tool_refs[]`; optional `description_mode` | Requires a pair-level registered `tool_set_ref`; default mode is `append` |

The compiler gets these three files as explicit command-line arguments. A pair's
`*_ref` and `*_sha256` values are provenance declarations; they are not yet a
resolver or integrity gate.

### Shape sketches

The following sketches show nesting and ownership only; they are deliberately
not copy-and-paste schemas. The checked-in smoke files are the executable
examples.

```yaml
# Rule library
format: hif.phase0.canonical_rules
format_version: 0
records:
  - id: rule-canon-example
    statement: "One observable behavioral constraint."
    # provenance, taxonomy, opportunity, and review fields are optional here
```

```yaml
# Item pair
format: hif.item_pair
format_version: 0
pair_id: example-pair
task_ref: provider/task-id
tool_set_ref: null
baseline:
  item_id: example-pair--baseline
  kind: zero_injection
  task_ref: provider/task-id
  rule_bindings: []
intervention:
  item_id: example-pair--intervention
  kind: rule_injection
  task_ref: provider/task-id
  rule_bindings:
    - binding_id: rb-01
      rule_ref: rule-canon-example
      role: scored
      target_surface: project_file
      delivery_order: 1
```

An intervention may contain multiple bindings. To deliver one Rule to two
surfaces, use two bindings with separate IDs; do not overload
`target_surface` with a list. A `tool_description` binding additionally names
abstract `tool_refs` and requires a non-null, supported `tool_set_ref`.

## Rule library envelope

The outer mapping of a rule library may contain:

| Field | Meaning | Status |
| --- | --- | --- |
| `format` | File discriminator, such as `hif.phase0.rule_candidates` or `hif.phase0.canonical_rules` | `recorded`; not enforced by the current Rule loader |
| `format_version` | Version of the stored snapshot format; currently `0` | `recorded`; not enforced by the current loader |
| `status` | Lifecycle status of the whole file, such as `extracted_unreviewed` or `reviewed_draft` | `recorded` |
| `created_at` | Date on which the snapshot was produced | `recorded` |
| `review_basis` | Summary of the review basis; used in the canonical file | `recorded` |
| `record_count` | Declared number of records | `recorded` |
| `notes` | File-level caveats and scope | `recorded` |
| `records` | List of Rule records | `runtime` loader input; required |

The current delivery loader requires only `records`, and requires `id` and
`statement` on each record. It preserves all other keys when resolving a rule,
but the current adapter only reads the statement. The other fields are used by
curation, audit, or future verification rather than by current delivery.

## Rule record

### Identity and provenance

| Field | Meaning | Current use |
| --- | --- | --- |
| `id` | Stable ID of the record in its current library; canonical IDs use the `rule-canon-*` prefix | `runtime`: Item lookup; required |
| `candidate_ref` | ID of the source candidate from which a canonical record was promoted | `recorded` |
| `source_ref` | ID of the source document/repository in `benchmark/sources` | `recorded` |
| `source_pool` | Provenance pool, currently `generalization` or `harness_native_calibration` | `recorded`; retained for later contamination analysis |
| `raw_unit_ref` | Bounded raw excerpt that produced the candidate | `recorded` |
| `source_locator` | Human-readable location in the source | `recorded` |
| `extraction_method` | How the candidate or restatement was produced | `recorded` |

`source_ref` identifies the source document or repository-level intake record;
`raw_unit_ref` identifies the bounded excerpt within that source that was
processed. Neither field is the rule text itself. The normalized behavioral
text is `statement`; the source excerpt and its provenance remain in the source
area when licensing permits.

### Core behavioral meaning

| Field | Meaning | Current use |
| --- | --- | --- |
| `title` | Short human-readable label | `recorded`; not sent to the model |
| `statement` | One atomic behavioral constraint. This is the text currently delivered by the adapter | `runtime`: rendered text; required |
| `family` | Provisional behavior family, such as `code-style`, `workflow`, `tool-use`, or `conditional-logic` | `recorded` annotation; no downstream balancing or scoring yet |
| `modality` | Logical force: `require`, `forbid`, `conditional-require`, `limit-min`, `limit-max`, `prefer`, or `allow` | `recorded` annotation; no current runtime branching |
| `severity` | Normative importance: `must`, `should`, or `may` | `assembly`: used for the current must-rule release-floor warning; not a behavior score |
| `scope` | Actor/object/code area/process to which the rule applies | `recorded`; not interpreted separately by the current adapter |
| `exceptions` | Conditions under which the rule does not apply | `recorded`; must be represented in `statement` if the model needs to see it |

`modality` and `severity` are intentionally different. `modality` describes
what the rule asks the agent to do; `severity` describes how strongly the rule
is treated in curation or release policy.

### Opportunity and evaluation annotations

| Field | Meaning | Current use |
| --- | --- | --- |
| `requires_opportunity` | Task tags that should be present before the rule can be considered scoreable | `assembly`: compared with TaskSpec `offers_opportunity` |
| `expected_evidence` | Evidence that a future verifier should inspect, such as a diff, AST, test result, or command output | `assembly`: copied into Item metadata; no rule verifier yet |
| `observability` | Where the behavior can be observed: `surface`, `structural`, `behavioral`, or `deep` | `recorded`; no current analyzer |
| `verifiability` | Expected reliability of judging the behavior: `deterministic`, `rubric`, or `subjective` | `assembly`: copied into the binding plan; no current scorer |
| `scoring_method` | Proposed checker family: `regex`, `ast`, `cross-file`, `command-output`, `hybrid`, or `llm-judge` | `assembly`: copied into the binding plan; implementations are pending |
| `universality` | Intended transfer range: `universal`, `cross-coding`, `cross-non-coding`, or `specific` | `recorded`; no current holdout/stratified analysis |
| `surface_fit` | Map from semantic surface to `none`, `low`, `medium`, or `high`, indicating suitability rather than actual delivery | `assembly`: used as a low-fit lint for scored bindings; not an automatic surface selector |
| `surface_variants` | Pre-authored equivalent renderings for different surfaces | `planned`; not present in the current YAML |

`prior` and `prior_lineage` are also part of the intended evaluation annotation:

| Field | Meaning | Current use |
| --- | --- | --- |
| `prior` | Hypothesis that the rule aligns with, opposes, or is neutral to the model's no-injection behavior (`align`, `against`, `neutral`) | `recorded` slot only; all current records are unset |
| `prior_lineage` | How the prior label was obtained, such as `zero_injection`, `curated`, or `unknown` | `recorded`; all current records are `unknown` |

An unset prior is not evidence for `neutral`. A zero-injection probe and its
cohort must exist before an `against` or `align` label is treated as empirical.

### Rule lifecycle review

| Field | Meaning | Current use |
| --- | --- | --- |
| `review_state` | Extraction/canonicalization state of the record | `recorded` |
| `qualification` | Whether task matching and later qualification are complete | `recorded`; current canonical values are pending |
| `contamination_status` | Training-data contamination assessment | `recorded`; currently `not_assessed` |
| `review.decision` | Candidate promotion decision, for example `accept_unchanged`, `accept_with_restatement`, or `split_into_atomic_rules` | `recorded` |
| `review.note` | Explanation of the review decision | `recorded` |

The separate `phase0-review.yaml` ledger additionally records
`candidate_ref`, `decision`, `canonical_refs`, `changed_fields`, and `note`.
Those are review-ledger fields, not part of the behavioral Rule itself.

## Item pair envelope

The current pair files may contain the following outer fields:

| Field | Meaning | Current use |
| --- | --- | --- |
| `format` | Must be `hif.item_pair` for the current loader | `runtime`: loader validation; required |
| `format_version` | Pair format version; currently `0` | `recorded`; not currently range-validated |
| `status` | Curation or plumbing lifecycle, such as `candidate` or `candidate_toolset_integration` | `recorded` |
| `created_at` | Pair creation date | `recorded` |
| `pair_id` | Stable identity shared by baseline and intervention | `runtime`: loader/manifest identity; required |
| `task_ref` | Reference to exactly one TaskSpec | `runtime`: matched against the supplied TaskSpec; required |
| `task_spec_sha256` | Expected TaskSpec snapshot hash | `recorded` integrity metadata; not checked against the supplied path today |
| `rule_library_ref` | Human/provenance reference to the Rule library snapshot | `recorded`; the compiler receives the Rule path separately and does not resolve this field |
| `rule_library_sha256` | Expected Rule-library snapshot hash | `recorded` integrity metadata; not checked against the supplied path today |
| `authority_policy` | Declared authority/conflict policy | `recorded`; no precedence engine yet |
| `tool_set_ref` | Pair-level tool-set condition; `null` means native/default in the current StepCLI adapter | `runtime` for the supported tool projection |
| `baseline` | Zero-injection variant | `runtime` when explicitly selected for compilation |
| `intervention` | Rule-injection variant | `runtime` when explicitly selected for compilation |
| `qualification` | Pair-level curation and release checks | `assembly`/`recorded`; not a run verdict |
| `provenance` | Generator, task/index, authoring, and hash references | `recorded` |
| `notes` | Human-readable caveats | `recorded` |

The current loader requires `format`, `pair_id`, `task_ref`, the selected
variant, and the variant's `item_id`/`task_ref`. A selected variant's
`rule_bindings` key may be omitted and is treated as an empty list. It does not
require or validate the pair's hashes, status, policy, qualification, or
provenance fields. The Harbor compiler likewise takes `--rules` and
`--task-spec` paths as explicit inputs; those command-line paths are the actual
files used for compilation.

## Authority policy

`authority_policy` currently has this shape:

| Field | Meaning | Current use |
| --- | --- | --- |
| `id` | Name of the policy, currently `no_intentional_conflict_v0` | `recorded` |
| `mode` | Policy mode, currently `no_intentional_conflict` | `recorded` |
| `precedence_held_constant_across_pair` | Whether the pair is intended to keep the policy fixed | `recorded` |
| `description` | Human explanation | `recorded` |

The per-binding `authority_class` is currently a semantic label derived from
the selected surface (`user_request`, `general_instruction`, or
`project_context`). It is not an operational precedence rule. In particular,
`delivery_order` must not be interpreted as authority priority.

## Variants

Each pair normally contains:

| Field | Meaning | Current use |
| --- | --- | --- |
| `item_id` | Stable ID for this variant | `runtime`/provenance; required |
| `kind` | `zero_injection` for baseline or `rule_injection` for intervention | `recorded`; current loader does not validate the enum |
| `task_ref` | Repeated task reference for consistency checking | `runtime` validation; required and must equal the pair value |
| `rule_bindings` | Ordered list of rule bindings | `runtime` delivery input; optional in the loader and defaults to `[]` |
| `difference_from_intervention` / `difference_from_baseline` | Declared contrast between the two variants | `recorded`; not a complete causal validator |

The intended contrast is that baseline and intervention share the task, policy,
tool-set factor, model settings, runtime, and budget, while only declared rule
bindings differ. The repository has not yet run matched baseline/intervention
trials for the live checkpoints.

## Rule binding

A binding is the association of one canonical rule with one semantic target
surface in one Item. The current generated pilot uses these fields:

| Field | Meaning | Current use |
| --- | --- | --- |
| `binding_id` | Unique identifier within the variant | `runtime`/manifest identity; required and unique |
| `rule_ref` | Canonical Rule `id` | `runtime`: resolves `statement`; required |
| `role` | `scored`, `observed`, or `distractor` | `assembly`/manifest metadata; required syntactically, but the delivery adapter does not score it or enforce the enum |
| `target_surface` | Backend-neutral intended surface | `runtime` routing for supported surfaces; required; unsupported surfaces are rejected unless explicitly allowed |
| `authority_class` | Per-binding authority annotation | `recorded` only |
| `rendering_ref` | Optional reference to a surface-specific rendering | `planned` in practice; current value is usually `null` |
| `surface_fit` | Snapshot of the selected Rule's surface suitability | `assembly` lint/annotation |
| `delivery_order` | Positive, unique deterministic materialization order | `runtime` ordering; defaults to list order when omitted; never precedence |
| `opportunity_match` | Static task/rule tag match described below | `assembly`; optional for plumbing-only Item records |
| `selection_rationale` | Why the generator/author selected this rule | `recorded` |
| `verification` | Per-binding verifier plan | `recorded`/`planned`; no automated rule verdict |
| `tool_refs` | Abstract tool roles, such as `shell` or `editor`; valid only for `tool_description` | `runtime` in the supported StepCLI tool projection; required for a tool-description binding |
| `description_mode` | `append`, `prepend`, or `replace` for a tool description override | `runtime` in the supported projection; defaults to `append` |

One binding has one `target_surface`. Intentional delivery of the same Rule to
two surfaces should be represented by two explicit bindings; a duplication
group field is described in design notes but is not present in the current
files.

## `opportunity_match`

This is a pre-run static compatibility record, not a behavior verdict. The
current generator computes it as follows:

```text
required = rule.requires_opportunity
offered  = task.curation.offers_opportunity
matched  = required intersect offered
```

It stores:

| Field | Meaning |
| --- | --- |
| `required` | Opportunity tags declared by the Rule |
| `offered` | Opportunity tags declared by the TaskSpec |
| `matched` | Tags present on both sides, preserving the Rule order |
| `status` | `not_required`, `full`, `partial`, or `none` |
| `derivation` | Current method label: static intersection of task hints and rule requirements |

`status: full` means all declared tags matched. It does not prove that the
actor, object, trigger, scope, exception, or evidence path is actually present.
The richer `opportunity_witness` needed for a score-bearing Item is future
work. A `must-scored` opportunity requires a demonstrated trigger and a healthy
verifier; it is stronger than `opportunity_match.status: full`.

## Binding qualification fields

### `verification`

The current nested object contains:

| Field | Meaning | Current status |
| --- | --- | --- |
| `status` | Verifier implementation state, usually `pending_verifier_implementation` | Not implemented for rule-level scoring |
| `scoring_method` | Method inherited from or selected for the Rule | Declaration only |
| `verifiability` | Expected judgment reliability | Declaration only |
| `expected_evidence` | Evidence the future verifier should consume | Declaration only |

### `qualification`

The generated pilot adds fields such as:

| Field | Meaning | Current status |
| --- | --- | --- |
| `status` | Candidate/review lifecycle | Recorded candidate state |
| `task_review_flags` | Flags inherited from task review | Recorded |
| `binding_count` | Number of intervention bindings | Generated summary |
| `scored_binding_count` | Number of bindings declared `scored` | Generated summary |
| `must_scored_binding_count` | Number of scored bindings whose Rule severity is `must` | Generated summary; currently zero in the pilot |
| `release_floor` | Requirement and warning for at least one must-scored rule | Assembly warning only |
| `surface_support` | Whether adapter support has been reviewed | Pending for most pilot surfaces |
| `verifier_coverage` | Whether verifier coverage exists | Pending for rule-level checks |
| `leakage_check` | Model-visible/evaluator-only separation result | Static candidate check |

These fields are useful for release gating, but they are not evidence that a
model followed a rule.

## Review ledgers and indexes

These files are part of the curation record, but they are not alternative
representations of a Rule or an Item and are never sent to the model.

### Rule review ledger

`benchmark/rules/candidates/phase0-review.yaml` uses
`format: hif.phase0.rule_review`. Its envelope records `format_version`,
`status`, `reviewed_at`, `reviewer`, candidate/canonical counts, and review
`criteria`/`notes`. Each
`records` entry contains:

| Field | Meaning | Current use |
| --- | --- | --- |
| `candidate_ref` | Candidate Rule being reviewed | Review lookup |
| `decision` | Promotion disposition, such as `accept_unchanged`, `accept_with_restatement`, or `split_into_atomic_rules` | Review record |
| `canonical_refs` | Canonical Rule IDs produced by the decision | Review-to-library linkage |
| `changed_fields` | Candidate fields changed during canonicalization | Audit of restatement |
| `note` | Reviewer rationale and caveats | Human audit |

The ledger's counts (`candidate_count`, `accepted_candidate_count`,
`split_candidate_count`, `canonical_record_count`, and `held_candidate_count`)
are summaries and are not independently used by delivery.

### Item panel index

`benchmark/items/indexes/swebench-multilingual-pilot-20.yaml` uses
`format: hif.item_index`. Its envelope records `format_version`, `status`,
`created_at`, `task_panel_ref`, `task_panel_sha256`, `task_review_ref`,
`task_review_sha256`, the Rule library `rule_library_ref` and
`rule_library_sha256`, the `sampling` method and generator hash, `pair_count`,
`pair_ids`, and a `pairs` summary list. A summary entry contains `pair_id`,
pair-file `path`, pair-file `sha256`, `task_ref`, `binding_count`, and
`scored_binding_count`. `surface_vocabulary`,
`role_vocabulary`, and `tool_set_policy` declare the candidate panel's allowed
semantic vocabulary. `notes` records non-release caveats.

The index is a selection manifest. It does not cause a pair to be run, and its
hashes are not checked by the current delivery compiler. Within `sampling`,
`method` names the deterministic selection procedure, `generator` identifies
the program that produced the index, `version` is that generator's version,
and `sha256` is the generator-file hash. The top-level references and hashes
identify the task panel, task review ledger, and Rule library snapshot used to
assemble the panel; they are audit metadata rather than automatic resolvers.

### Item review ledger

`benchmark/items/indexes/swebench-multilingual-pilot-20-review.yaml` uses
`format: hif.item_review`. Its envelope records the review date/reviewer,
`format_version`, `status`, `reviewed_at`, `reviewer`, `pair_count`, a
`decision_summary`, review `criteria`, and `notes`. The
`decision_summary` contains `retained_candidate_count`, `held_count`,
`static_error_count`, and `release_status`; these are aggregate review counts,
not execution results. Each pair record contains `pair_id`, pair-file
`path`/`sha256`, `task_ref`, `decision`, `flags`, binding counts, and a review
`note`. `decision` and `flags` describe candidate disposition only; they are
not runtime gates or model verdicts.

The separate `tool-surface-pilot.yaml` is an integration index rather than a
benchmark panel. Its `experiment` block contains an experiment `id`, purpose,
backend, harness, `tool_set_ref`, and non-release `score_status`; `pairs`
identifies the pair files, task reference, file hash, and tested `variants`;
`checks` lists plumbing assertions. It uses the same `hif.item_index`
discriminator while carrying this narrower experiment metadata.

## Semantic surfaces and tool factor

The semantic vocabulary is:

```text
system_prompt
managed_instruction
global_instruction
project_file
user_message
tool_description
skill
```

Current StepCLI delivery status:

| Surface | Current behavior |
| --- | --- |
| `system_prompt` | Additive host instruction via `stepcli_instruction_prompt`; multiple fragments are joined in `delivery_order` |
| `user_message` | Additional user/task-channel fragment via Harbor `extra_instruction_paths` |
| `project_file` | Generated project rule file discovered by StepCLI at startup |
| `tool_description` | Supported only with the registered `dsh_minimal` tool projection |
| `managed_instruction` | Semantic target only; no HIF-controlled injection |
| `global_instruction` | Semantic target only; no HIF-controlled injection; ambient global files are a possible confounder |
| `skill` | Semantic target only; no current adapter projection |

`tool_set_ref` is pair-level and separate from a `tool_description` binding:

- `null` requests the native/default StepCLI tool set;
- `dsh_minimal` selects the only projection currently registered by the
  StepCLI adapter, mapping `shell -> bash` and `editor -> str_replace_editor`;
- another reference is unsupported until a corresponding adapter projection is
  registered;
- `tool_refs` can target one or more tools within the selected set. Selecting a
  set does not imply that every tool description is overridden.

The current adapter therefore supports a targeted description override such as
`tool_refs: [shell]`; it does not infer a whole-set override.

## Classification versus consumption

The current data does contain annotations, but most are provisional labels for
curation and future analysis rather than active experimental factors.

| Annotation or field | Current population | Current consumer | What it does **not** do yet |
| --- | --- | --- | --- |
| `family`, `modality`, `observability`, `universality` | Populated on all 44 candidates and all 45 canonical drafts | Human review and descriptive inspection | No balancing, difficulty stratification, or scoring branch |
| `severity` | Populated (`must`/`should`; no `may` in this snapshot) | Item assembly counts must-scored bindings and emits a release-floor warning | It is not a model-behavior score or a runtime priority |
| `verifiability`, `scoring_method`, `expected_evidence` | Populated on every draft and copied into bindings | Item assembly records a proposed verifier plan | No rule-level verifier or automatic score exists |
| `requires_opportunity` | Populated on every draft | Item assembly computes the static `opportunity_match` intersection | It does not establish that the trigger or evidence is present in the actual task |
| `surface_fit` | Populated on every draft and snapshotted on bindings | Item lint rejects low-fit scored bindings in the pilot generator | It does not select or materialize a surface |
| `prior`, `prior_lineage` | All current candidates/drafts have `prior: null`, `prior_lineage: unknown` | None | No zero-injection prior classification has been performed |
| binding `role` | Populated on pilot pairs as `scored`, `observed`, or `distractor` | Review/index summaries and manifest metadata | No formal denominator or verdict computation exists |
| binding `target_surface` | Populated on every pilot binding | Delivery routing for supported surfaces | Semantic support does not imply that every surface is implemented |

The pilot generator currently chooses a small fixed set of canonical Rule IDs
based on task opportunity tags. It does not select rules by `family`,
`modality`, or a learned difficulty score. This is intentional scaffolding and
should remain visible until a future experiment defines and validates those
factors.

## Implementation status by layer

| Layer | Current state |
| --- | --- |
| Source intake and raw provenance | Implemented for the Phase 0 batch |
| Candidate and canonical Rule files | 44 candidates and 45 agent-reviewed canonical drafts; human spot check and release qualification pending |
| Rule taxonomy | Populated provisionally; mostly descriptive annotations, not independently consumed factors |
| TaskSpecs and pilot index | 20 thin SWE-bench Multilingual candidates collected and indexed |
| Item assembly | Implemented; emits 20 candidate pair files with static opportunity matching |
| Item format validation | Partial; current loader/generator checks the fields needed by the current path, not a formal schema or all declared metadata |
| StepCLI/Harbor delivery | Implemented for `user_message`, `project_file`, additive `system_prompt`, and the registered `dsh_minimal`/`tool_description` projection |
| Other surfaces | Representable semantically but unsupported by the current adapter |
| Rule-level verifier | Not implemented; `verification` is a plan |
| Baseline execution and pairing | Structure exists; live checkpoints are intervention-only |
| Normalized analysis and reporting | Not implemented |
| Machine-readable schema | Not implemented; `schemas/` is reserved for future contracts |

The current runtime code consumes a much smaller subset than the stored files:

| Runtime input | Effect in the current path |
| --- | --- |
| Pair `format`, `pair_id`, `task_ref`; variant `item_id`, `task_ref`, and `rule_bindings` | Loader validation, identity, and selection of the task/variant |
| Rule `id` and `statement` | Rule lookup and text rendered into delivery payloads |
| Binding `target_surface` | Selects a supported delivery route or produces an unsupported-surface error |
| Binding `delivery_order` | Orders materialized fragments; omitted values fall back to list order |
| Pair `tool_set_ref` | Selects the adapter's tool-set projection, or native/default when `null` |
| Binding `tool_refs` and `description_mode` | Selects concrete tools and override mode within a supported projection |

`role`, `authority_policy`, hashes, `qualification`, `opportunity_match`, and
the taxonomy/provenance fields may be copied into manifests or used by
assembly/lint, but they do not currently change the model-visible delivery or
produce a rule verdict. The remaining fields should not be described as runtime
controls until a consumer and an experiment use them.

## Format-change procedure

A change to any Rule or Item storage contract includes a change to this
document in the same change. This includes:

- adding, removing, renaming, or moving a field;
- changing a field's meaning, requiredness, type, enum, or nesting;
- changing the interpretation of a surface, role, tool-set reference, or
  opportunity status;
- changing an example or generator output that is intended to represent the
  current format.

The change must also update affected examples, generators, loaders, and tests.
Every format change appends one entry to the change log below using the full
calendar date `YYYY-MM-DD`; existing entries are not rewritten or removed.

## Change log

### 2026-08-31

- Added the maintained current-format reference for Rule libraries and Item
  pairs.
- Recorded the distinction between runtime, assembly, recorded, and planned
  fields.
- Documented the distinction between static opportunity tag matching and a
  complete opportunity witness.
- Recorded current StepCLI tool-set and surface support boundaries.
- Added the file-kind map, current loader minimum, review-ledger/index
  boundaries, and the classification-versus-consumption inventory.
