---
title: Methodology and construction plan
description: Adopted methodology, draft data contracts, and construction order for the single-agent StepCLI instruction-following track.
status: active
---

# Methodology and Construction Plan

**Status:** working plan, written 2026-08-26. Replaces the deleted
`docs/implementation-handoff.md`.

This document records the methodology the project adopts, drafts the data
contracts that follow from it, and orders the construction work. It does not
change any boundary in [AGENTS.md](../../AGENTS.md); where a boundary's wording no
longer matches the adopted methodology, this document says so and leaves the
edit to a review decision.

Read [AGENTS.md](../../AGENTS.md), [the overall design](../design.md), and [the
constraints](../constraints.md) first. Those remain authoritative. This document is
subordinate to them.

## 1. Why the previous handoff was removed

`docs/implementation-handoff.md` proposed a first vertical slice built from a
hand-authored fixture, so that one paired trial could run end to end quickly. It
was removed for two reasons.

First, it narrowed an Item to a single rule under a baseline/intervention pair.
That contradicts [`design.md`](../design.md), which lists an Item's inputs as "one
or more rule references and their roles". The single-rule shape was an artifact
of wanting something runnable on day one, not a design decision.

Second, its construction order put the execution layer first and the data
contracts last. The reversed order is cheaper: a wrong Pack compiler costs a
rewrite of code, while a wrong rule format costs a re-review of human-curated
language material. Only the second kind of rework has to be paid twice in
human time.

The handoff's execution-layer observations were verified and remain useful. They
are preserved in [§9 Phase 4](#phase-4-execution-layer) rather than discarded.

## 2. Reference baseline

The methodology below follows the Harness-IF paper, *Harness-IF: Evaluating
Instruction Following Across Instruction Surfaces in Coding Agents*
([arXiv:2608.11727](https://arxiv.org/abs/2608.11727), ByteDance Seed et al.,
2026-07-15). Its reported scale:

| Quantity | Value |
| --- | --- |
| Rule library | 642 atomic constraints |
| Evaluated items | 60, selected from 80 candidates |
| Rules per item | 25–35 injected, 10–27 scorable |
| Rules instantiated / scored | 302 / 256 |
| Scenario library | 13, of which 8 evaluated |
| Surfaces | 6 defined (HD fixed), 5 evaluated: SP, TD, SD, PF, UI |
| Runs | 60 items x 12 models x 3 rounds = 2,160 |
| Rule-level verdicts | 40,104 rows; 37,616 eligible pass/fail |
| Deterministic coverage | 13.3% of eligible verdicts; 86.8% involve a judge |
| Headline metric | AP-Acc over the against-prior subset |

Per [README](../../README.md), the paper is an implementation input, not a
normative schema. Where this project departs from it, the departure is stated.

## 3. Source material

The rule library is extracted from project-instruction and contributor
documents in publicly accessible repositories: `AGENTS.md`, `CLAUDE.md`,
`CONTRIBUTING.md`, style guides, skill descriptions, and tool schemas. Skill
descriptions and tool schemas are in scope as sources even though the first
research track does not yet deliver rules on those surfaces.

### 3.1 Rules are authored, not copied

A canonical rule is a project-authored statement of a behavioral constraint that
was *observed* in source material. It is not a reproduction of the source
wording. Extraction produces a neutral restatement, normalized across the
phrasings different surfaces would use.

This follows the paper's release boundary and removes the need for a licensing
gate during collection: the collected artifact is a fact about a convention, not
an excerpt of expressive text.

### 3.2 Two-tier provenance

Provenance is recorded at two levels, and the level determines who can see it:

| Tier | Contents | Visibility |
| --- | --- | --- |
| Private ledger | repository, commit, path, line range, original phrasing, retrieval date, extraction method, reviewer | internal audit and rights review only |
| Public class | coarse source category, extraction method class, review state | released with the rule |

The public tier must not permit a join from a released rule back to a named
source repository. Long verbatim excerpts are not stored in either tier; the
private ledger keeps the pointer and enough phrasing to audit the restatement.

Reproducibility is unaffected: the private ledger satisfies
[`constraints.md`](../constraints.md)'s provenance requirement, and the pointer is
immutable because the commit is pinned.

### 3.3 Phase 0 source shortlist

The initial source decision is recorded in the durable
[Phase 0 source shortlist](../source-shortlist.md). It contains a
generalization pool of human-facing project/API guidance and a harness-native
calibration pool of real `AGENTS.md`-style instructions. Both pools enter the
same cleaning path. The pool label is retained for later contamination,
product-specificity, and opportunity analysis; it is not an intake-time
exclusion criterion.

## 4. Rule contract (draft)

Per [AGENTS.md](../../AGENTS.md) boundary 10, this is a field-level draft, not a
formal schema. It is an input to the Phase 1 review, not a decision.

A canonical rule expresses one observable behavioral constraint, with scope,
exceptions, and intended evidence, and carries the following annotation axes.
The first six and the two surface fields are adopted from the paper's Appendix A;
`severity` and `scoring_method` from its Appendix B.

| Field | Values |
| --- | --- |
| `family` | professional-writing, output-control, code-style, workflow, quantitative, conditional-logic, tool-use |
| `modality` | require, forbid, conditional-require, limit-max, limit-min, prefer, allow |
| `prior` | align, against, neutral — see [§7](#7-baseline-and-prior-labels) |
| `observability` | surface, structural, behavioral, deep |
| `verifiability` | deterministic, rubric, subjective |
| `universality` | universal, cross-coding, cross-non-coding, specific |
| `surface_fit` | per surface: none, low, medium, high |
| `surface_variants` | one pre-authored rendering per admissible surface, semantics preserved |
| `severity` | must, should, may |
| `scoring_method` | regex, ast, cross-file, command-output, hybrid, llm-judge |

Notes on individual fields:

- `modality` is not redundant with `family`. A forbid and a require over the
  same content are different instructions with different difficulty.
- `surface_fit` is a four-level suitability score, not a boolean. It encodes
  whether a surface's authoring role could plausibly carry the rule in
  deployment: a branch-naming rule fits a project file or system prompt, but not
  a tool schema. It exists to prevent semantically impossible placements.
- `verifiability: subjective` does not disqualify a rule. See
  [§6](#6-item-shape-and-rule-roles).
- `scoring_method` is chosen at authoring time, and constrains `verifiability`.

The axis product `family x modality x prior x observability x verifiability x
universality` gives 7x7x3x4x3x4 = 7,056 cells. The paper's 642 rules populate
roughly 420 after deduplication. This matrix is the mechanism for targeted
expansion: coverage gaps are read off the cell counts rather than estimated.

## 5. Task contract (draft)

A scenario supplies working files for a realistic coding task, its tests, and a
multi-turn user instruction sequence. Per
[`constraints.md`](../constraints.md) the coding objective stays neutral, so that
the rule remains the intended behavioral intervention.

For the first external benchmark pool, use the thin TaskSpec arrangement in
[Task sourcing and representation](../task-sourcing.md). A TaskSpec is a
reviewable source-pinned task reference, not a Harbor task directory. The first
SWE-bench Multilingual pilot should have a fixed selection index (about 20 IDs,
plus a reserve) and one spec per selected upstream instance. The spec keeps the
cleaned problem statement and opportunity annotations, while patch/test oracle
data and generated repositories remain evaluator-only and external.

Draft fields beyond the neutral objective and fixture reference:

- `offers_opportunity` — the observable situations this task creates, paired
  against a rule's `requires_opportunity`. Item assembly is then a matching
  operation over these tags rather than a manual judgment, which turns
  [AGENTS.md](../../AGENTS.md)'s rule/task compatibility gate into something
  computable.
- `language`, `stack`, `edit_kind` — so a panel can be checked for spread.

The paper's scenario library spans backend, frontend, systems, data/ML,
automation, security testing, tool orchestration, and technical documentation.
Treat that spread as the target, not the count.

## 6. Item shape and rule roles

An Item is one scenario plus a set of rule references, each carrying a role.
[`design.md`](../design.md) already provides for this: "one or more rule references
**and their roles**".

Multiple rules per item is the adopted shape. It does not conflict with
[README](../../README.md)'s prohibition on "a permanent Cartesian-product
expansion" — that warns against multiplying every rule by every task. Packing
many rules into few items is the opposite operation, and it is what makes
rule-level scoring affordable: one run yields tens of verdicts.

### 6.1 Roles

Assigned per rule reference, at item authoring time:

| Role | Scored | Purpose |
| --- | --- | --- |
| `scored` | yes, enters the primary denominator | the measurement |
| `distractor` | no | realistic instruction load; attention competition; a home for rules that cannot be scored |
| `observed` | verdict recorded, excluded from the primary denominator | exploratory analysis; rubrics still under calibration |

A rule with `verifiability: subjective`, or with no available
`scoring_method`, is not discarded. It is admitted with role `distractor` or
`observed`. This is the project's explicit design for hard-to-score material,
and it makes deliberate what the paper does implicitly when it injects 25–35
rules and scores 10–27.

Roles are authoring-time declarations. They are distinct from run-time verdict
statuses (`pass`, `fail`, `no_opportunity`, `partial`,
`untestable_design_gap`), which are determined by what the run produced.

### 6.1.1 Rule bindings and surfaces

Each rule reference in an Item is a binding, not just a bare ID. At minimum the
binding identifies:

- the rule reference and authoring role;
- one backend-neutral target surface;
- any authority/precedence label needed by the declared policy;
- an optional rendering variant or capability requirement.

The first binding contract should use one target surface per binding. If a
study intentionally sends the same rule to two surfaces, it creates two
explicit bindings linked by a duplication/group identifier. This prevents the
Item compiler from hiding multi-surface delivery and lets analysis score each
rule-surface opportunity separately. The exact surface vocabulary is still an
open decision.

The binding's semantic surface is not a StepCLI filename or option. Mapping it
to a system prompt, project instruction file, user message, tool description,
skill, or another concrete entry point belongs to `harnesses/stepcli` during
Phase 4. The Harbor compiler packages the task, environment, and evaluator
hooks according to Harbor's visibility boundary; it does not perform that
surface mapping.

An Item may additionally carry an optional top-level backend-neutral
`tool_set_ref` (with backend-specific resolution recorded in the run lock).
This is a condition-level factor separate from a `tool_description` rule
surface. It is reserved for a future complete tool-set replacement (registry,
schemas/presentation, implementation, and permissions); no StepCLI-specific
tool-set schema is introduced in this plan.

### 6.2 Distractor design rules

Distractors change the measurement if they are chosen carelessly. The following
are assembly-time lint requirements, not guidance:

1. **No semantic conflict with any `scored` rule in the same item.** A
   conflicting distractor turns the item into an undeclared precedence
   experiment. Instruction conflict is a separate track and must be declared,
   not arrived at accidentally.
2. **No interference with a `scored` rule's opportunity.** A distractor that
   suppresses an action ("do not add new files") can delete the opportunity a
   scored rule needed. Opportunity interference is checked, not assumed.
3. **Distractors are fixed in the item, not sampled per trial.** Otherwise
   replicates are not comparable and the item is not reproducible.
4. **Distractors count against the harness instruction budget.** StepCLI caps
   all instruction files at 32 KB combined, and the project file is discovered
   last, so it is the first to be truncated. The injected set must be sized
   against that ceiling, distractors included.
5. **Promotion is a version bump.** When a scoring method becomes available for
   a `distractor`, promoting it to `scored` changes the item's identity and
   requires a new version, not a silent edit.

Additionally, each item should carry at least one `must`-severity `scored` rule,
so that every item has a defined floor.

### 6.3 Injection count

Undecided. The paper's anchors are 25–35 injected and 10–27 scorable. Two
mechanisms bound the choice:

- The scorable count is not an authoring decision. It is determined by how many
  opportunities the scenario actually creates; the remainder resolve to
  `no_opportunity` and leave the denominator. What is authored is the injection
  ceiling.
- The injection ceiling is bounded above by the harness instruction budget
  (§6.2 item 4), which must be computed rather than assumed for any count
  materially above the paper's range.

### 6.4 Cost of this shape

Multi-rule items forfeit per-rule causal attribution. Thirty rules in one item
compete for attention and for the instruction budget, and may interact. This is
a real departure from [`design.md`](../design.md)'s "one intended intervention"
principle, and the way to stay honest about it is to not claim single-rule
causality from a multi-rule item. Rule-level verdicts are aggregated across
items; a claim about one rule's causal effect requires the controlled design of
§7, not the main panel.

The cascade handling in [§8](#8-verification-and-denominator-discipline) exists
because this interaction is real rather than hypothetical.

## 7. Baseline and prior labels

**No scheme is decided here.** This section states the problem, the mechanism,
and the options, and records the prerequisites that hold whichever option is
chosen.

### 7.1 The problem

When an agent obeys a rule, it may simply have been going to do that anyway. A
rule requiring docstrings, satisfied by a model that always writes docstrings,
yields a `pass` that carries no information: it demonstrates neither that the
rule was delivered nor that it was followed. Aggregate compliance scores
therefore overstate instruction following by an unknown, model-specific margin.

This is the question [README](../../README.md) opens with — whether a model carries
out a requested behavior "instead of reverting to a learned default" — so the
measurement is not optional.

### 7.2 The mechanism

A baseline observation withholds the target rule and runs the same task, to see
what the model does unprompted. The paper calls this a zero-injection ablation:
same task, target rule absent, run across a probe cohort, with a rule receiving
a consensus label when at least five of nine probe builds agree.

The result is a `prior` label on the rule: `align` (the rule matches the default
tendency), `against` (it pushes against it), or `neutral`. Restricting a metric
to the against-prior subset gives AP-Acc, which is the paper's headline result:
all twelve evaluated models score lower on against-prior rules, by 3.6 to 7.4
points.

### 7.3 Options

| Option | When | Cost | What it buys |
| --- | --- | --- | --- |
| Per-experiment pairing | every intervention run gets a matched baseline run | run count doubles; repeats for every new model | causal attribution for that rule in that experiment |
| Prior labeling, up front | once, before the panel; label stored on the rule | one probe cohort; labels reused indefinitely | AP-Acc as a stratified metric; labels become a reusable rule property |
| Prior labeling, after the fact | derived later from accumulated runs or a dedicated probe | deferred | same as above, if verdict records were retained at sufficient granularity |

Prior labeling does not abandon the baseline. It moves it from a per-experiment
cost to a one-time asset on the rule library, which is consistent with
[README](../../README.md)'s first design decision that rules and tasks are reusable
assets.

[AGENTS.md](../../AGENTS.md) boundary 4 requires pairing whenever a claim depends
on changing default behavior, and forbids reporting an unpaired rule score as a
causal result. Prior labeling satisfies the first clause — the paired
observation is performed, once, and amortized into the label — and AP-Acc
respects the second, because it is a behavioral stratification and is not
reported as a causal claim. [`constraints.md`](../constraints.md) additionally
permits a documented reason why pairing is impossible; doubling a
multi-model, multi-round panel is such a reason if it is stated.

### 7.4 Prerequisites, independent of the choice

These can be settled now without deciding the scheme, and settling them keeps
all three options open:

1. **Field positions exist on the rule.** `prior`, plus `prior_lineage`
   recording where the label came from (`zero_injection`, `curated`, `unknown`).
   The paper reports 44.1% / 46.5% / 9.4% across these three, so mixed lineage
   is the expected state and must be representable, not an error case.
2. **Verdicts are stored at (item, rule, run) granularity with the rule
   identifier retained.** This is what makes after-the-fact labeling possible:
   any prior labeling produced later can slice verdicts that already exist.
   Deferring the decision costs nothing as long as this granularity is not lost.
3. **Probe cohort identity is recorded, and its overlap with the evaluated
   cohort is computable.** Because a prior label is derived from model behavior,
   a probe build that also appears in the evaluated panel makes the label
   partly circular.

### 7.5 A known weakness worth improving on

The paper is explicit that its probe cohort overlaps its evaluated cohort: five
of nine probe builds share an identifier with an evaluated model, and because
only four probe builds sit outside the evaluated set, a 5-of-9 consensus
necessarily includes at least one overlapping build. No zero-injection label is
fully independent of the scored cohort. The paper bounds the exposure rather
than claiming independence.

A probe cohort disjoint from the evaluated cohort would remove this weakness.
That is a design opportunity, and it is a reason to decide the probe cohort
policy before spending probe budget rather than after.

## 8. Verification and denominator discipline

### 8.1 Scoring methods

Six methods, selected per rule at authoring time: `regex`, `ast`, `cross-file`,
`command-output`, `hybrid` (deterministic pre-check narrowing candidates, then
LLM refinement), and `llm-judge` (rubric grading). Judge and hybrid methods use
majority voting over three independent evaluations.

### 8.2 The judge is primary, not a fallback

For this source material, deterministic checks cover a minority of verdicts —
13.3% in the paper, with 86.8% of rows involving a judge. Rules extracted from
project-instruction prose are mostly rubric-shaped, and no amount of verifier
engineering converts "keep explanations concise" into an AST match.

This makes judge reliability a first-class design concern rather than an
afterthought. Required alongside the judge: three-vote majority, a judge-swap
sensitivity analysis, and reported agreement. The paper's judge swap yields
62.1% agreement and kappa = 0.163, which it identifies as the dominant
uncertainty in its measurement — so absolute levels are instrument-specific and
only cross-model comparisons, which share the instrument, carry claims.

**Open wording item.** [AGENTS.md](../../AGENTS.md) boundary 8 and
[`constraints.md`](../constraints.md) state a preference for deterministic
verifiers with an LLM judge as a documented fallback. That preference is
descriptively wrong for this source family. The boundary is not edited here;
it is flagged for a review decision.

### 8.3 Cascade handling

Both mechanisms are adopted from the paper, and both implement
[`constraints.md`](../constraints.md)'s requirement that an incomplete artifact be
visible as missing data rather than silently counted as a model error:

- **Cascade dedup.** One missing artifact can fail many dependent rules at
  once. Retain a single highest-severity failure and convert the dependent
  outcomes to `no_opportunity`, so one missing artifact does not multiply into
  many violations.
- **Cascade fairness audit.** When at least half of the evaluated agents fail to
  produce the artifact a rule needs, promote the rule to
  `untestable_design_gap` and exclude it from denominators. Requires a minimum
  number of tested agents to run.

### 8.4 Verdict classes

Rule-level: `pass`, `fail`, `no_opportunity`, `partial`,
`untestable_design_gap`. Only `pass` and `fail` enter the primary denominator.

This project additionally requires `delivery_failure` and
`infrastructure_failure`, per [AGENTS.md](../../AGENTS.md) boundary 5. The paper
does not need them because it does not study delivery fidelity; this project
does, so a rule that was never loaded must be distinguishable from a rule that
was loaded and ignored.

## 9. Construction order

### Phase 0: hand-authored samples, no code

Use the adopted [source shortlist](../source-shortlist.md) to collect an initial
pool of roughly 40 raw normative units (expected range: 36–47). A raw unit is a
bounded source paragraph or bullet before atomic decomposition; it is not a
canonical rule. From that pool, hand-select 10–15 units and fill in the §4
fields, plus one or two scenarios against §5. Deliberately include difficult
cases: bundled requirements that need splitting, purely stylistic prose, rules
with unclear scope, rules that require a tool or Git event, and rules with no
plausible scoring method.

The output is sample files under `benchmark/sources/` and
`benchmark/rules/candidates/`. The purpose is not to accumulate material. It is
to find out which fields cannot be filled, which constraints cannot be
expressed, and which distinctions collapse in practice. Designing the schema
first and populating it afterwards produces fields nobody can fill.

**Checkpoint 2026-08-27:** the initial intake snapshot is populated with 39 raw
units and 44 provisional candidates from the pinned shortlist. See
[`benchmark/sources/phase0-source-manifest.yaml`](../../benchmark/sources/phase0-source-manifest.yaml),
[`benchmark/sources/phase0-raw-units.yaml`](../../benchmark/sources/phase0-raw-units.yaml),
and [`benchmark/rules/candidates/phase0-candidates.yaml`](../../benchmark/rules/candidates/phase0-candidates.yaml).
An agent review has now accepted all 44 candidates for draft canonicalization,
splitting the bundled tests-and-docs candidate into two records (45 canonical
drafts total). The review ledger is
[`benchmark/rules/candidates/phase0-review.yaml`](../../benchmark/rules/candidates/phase0-review.yaml)
and the draft library is
[`benchmark/rules/canonical/phase0-canonical.yaml`](../../benchmark/rules/canonical/phase0-canonical.yaml).
They remain unqualified and pending human spot-check; the next construction
action is the Phase 0B task-reference pilot.

### Phase 0B: task-reference pilot, no runner

In parallel with the source samples, pin the chosen SWE-bench Multilingual
revision and produce a fixed selection index for approximately 20 tasks. Write
thin TaskSpec candidates containing the upstream ID, source revision, cleaned
problem statement, repository/base commit metadata, opportunity hints, and an
evaluator-only reference. Keep generated Harbor packages, cloned repositories,
patches, and test/oracle records in an external cache. This phase validates the
task representation and selection metadata; it does not require Harbor or
StepCLI.

**Checkpoint 2026-08-27:** the pilot is collected and agent-reviewed. The index
[`benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml`](../../benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml)
pins the `SWE-bench/SWE-bench_Multilingual` test revision
`e5c585e008e2cb5eecc7c64192d855c53279d788`, a 20-task language-stratified
sample, and 8 reserve IDs. The 20 thin specs are under
[`benchmark/tasks/specs/swebench-multilingual/`](../../benchmark/tasks/specs/swebench-multilingual/)
and the deterministic/semantic review is recorded in
[`swebench-multilingual-pilot-20-review.yaml`](../../benchmark/tasks/indexes/swebench-multilingual-pilot-20-review.yaml).
The panel remains `candidate_panel`; no task is promoted to a released split.
The next construction action is Phase 1 contract review followed by candidate
Item assembly. No Harbor or StepCLI source change is part of this checkpoint.

### Phase 1: contracts, reviewed

Derive the rule, scenario, and item contracts from what Phase 0 exposed. Settle
the candidate-to-canonical promotion path including one-to-many decomposition,
the opportunity tag vocabulary, TaskSpec retention/evaluator-cache policy,
surface vocabulary and binding cardinality, and identity, versioning, and
hashing.

[AGENTS.md](../../AGENTS.md) requires this review before broad implementation or
released curation begins. Phase 1 ends at that review.

### Phase 2: collection and cleaning pipeline

First phase with code. Source intake with pinned commits and the two-tier
provenance split; LLM-assisted extraction producing candidates only; dedup,
decomposition, lint, and promotion. Coverage gaps read off the §4 cell matrix.

### Phase 3: item assembly

Opportunity matching, role assignment, and the §6.2 distractor lint. Injection
budget computation against the harness instruction ceiling. Preserve each
rule's target surface as an independent binding and validate any optional
`tool_set_ref` against the selected backend capability declaration; do not map
it to StepCLI config in this phase.

**Candidate checkpoint 2026-08-27:** a deterministic utility now emits 20
`hif.item_pair` candidates, one for each selected task, under
`benchmark/items/pairs/swebench-multilingual/`. Each pair contains a
zero-injection baseline and a two-to-four-binding intervention. Static matching,
reference, role, surface, and leakage checks pass. The panel deliberately keeps
judge-backed rules as `observed` and records a warning because the current task
pool has no reliable `must`-severity scored opportunity. This is a data-shape
checkpoint only; no verifier or live runner has been implemented yet. The first
smoke Pack compiler and StepCLI delivery adapter are now implemented separately
under `compilers/harbor/` and `harnesses/stepcli/`; they do not change Harbor or
StepCLI.

Nothing in Phases 0–3 requires Harbor or StepCLI.

### Phase 4: execution layer

The first delivery slice is implemented for the smoke fixture. The following observations were
verified against the current sibling development trees and are carried over from
the deleted handoff. They are implementation observations, not version
guarantees; re-check them when either dependency moves.

- **Instruction discovery.** StepCLI resolves instruction files from three
  source classes — managed, global, and project — in that order, and exposes the
  resolved list through `step config show --workspace <path> --json` as
  `runtime.instructionFiles`, with a `source`, `format`, `activation`, and
  `imports` per entry. This is a pre-model-call probe: it establishes the
  effective surface without spending a model budget.
  (`step-cli/src/bootstrap/prompt/instruction-files.ts`,
  `src/runtime/runtime-config.ts`, `src/commands/config-command.ts`)
- **Instruction budget.** All instruction files share a 32 KB cap, consumed in
  discovery order, so project files are truncated or skipped first. There is
  currently no configuration or environment switch to restrict discovery to a
  single source class.
- **Source isolation.** Because discovery reads the process home directory, a
  global instruction file there is loaded into every condition. It is the
  treatment that loses budget, not the confounder. The probe detects this: the
  `instructionFiles` list must contain only the expected sources before a run is
  treated as valid. A scoped-discovery switch in StepCLI would both close this
  and serve as the instrument for a future precedence track.
- **Harbor delivery.** Harbor supplies one instruction channel, which reaches
  the agent as a single string. Its `extra_instruction_paths` mechanism appends
  file content to that same text, so it cannot represent an independent surface.
  Surfaces other than task/user instruction must be delivered through the
  workspace or through StepCLI's own configuration layer. The Item compiler and
  Harbor compiler therefore pass a semantic surface plan to the StepCLI
  adapter; they do not flatten it.
  (`harbor/src/harbor/agents/installed/stepcli.py`,
  `harbor/src/harbor/models/task/task.py`)
- **Companion work location.** Harbor-side adaptation belongs on a branch in the
  Harbor repository, not inside this one. Record the commit in the experiment
  lock.

**Candidate checkpoint 2026-08-28:** `user_message` and `project_file` can be
compiled together into an external Harbor Pack. Static validation confirms the
Harbor `JobConfig`, task directory, agent-stage `upload_files` hook, and current
StepCLI project-rule discovery shape. Docker is unavailable in the development
environment, so a live model trial is deliberately not claimed. The next phase
is a runner/preflight that captures effective instruction files and native
events before invoking verification; only an interface gap there should lead to
changes in Harbor or StepCLI.

**Live checkpoint 2026-08-29:** the additive `system_prompt` path and the
`dsh_minimal`/`tool_description` projection were exercised with real glibc
runtime bundles. The tool-surface run used Harbor branch
`i-panhaoran/hif-toolset-surface-20260829` at commit
`709cde1ef8177ae789bca2b7350c8ea267e627d3`, and StepCLI runtime
`v20260829.0003` with SHA-256
`515cb7773dc17f7b24869e468da65241e2a0ef1f69600639939156f5b9d60c56`.
Provider-wire inspection found the project, user, and tool-description
fragments in their intended `system`, `messages`, and `tools` locations across
166 requests. The independent task verifier returned reward `1`. This is
delivery/plumbing evidence only: the item was intervention-only, the tool rule
was `observed`, no paired baseline was run, and no causal or aggregate rule
score is claimed. The external Pack and all runtime artifacts remain outside
the repository; the SWE-bench Multilingual glibc image did not require a musl
bundle.

The interface gap identified in the preceding checkpoint was therefore
resolved in the separately pinned Harbor adapter branch, without changing the
base Harbor checkout. The next construction action is HIF-owned normalized
capture, deterministic rule verification, and analysis; future Harbor or
StepCLI changes are opened only when a new surface or tool-set capability
requires them.

## 10. Open decisions

| Decision | Blocks | Notes |
| --- | --- | --- |
| Zero-injection timing and probe cohort policy | prior labeling; probe budget | §7. Deferrable if §7.4 prerequisites hold. Decide cohort disjointness before spending probe budget. |
| Rule injection ceiling per item | Phase 3 | §6.3. Bounded above by the instruction budget. |
| SWE-bench sample revision/count/sampling policy | Phase 0B | See [`task-sourcing.md`](../task-sourcing.md); final IDs and revision must be frozen before specs are promoted. |
| TaskSpec inline text versus external blob | Phase 1 | Inline cleaned text is recommended for the 20-task pilot; evaluator data remains external either way. |
| Evaluator cache provider/location | Phase 1 | Must be external and addressable by revision/hash; never a repository-local runtime dependency. |
| Rule binding surface cardinality and v1 vocabulary | Phase 1 | One surface per binding is recommended; the current adapter has live evidence for `system_prompt`, `user_message`, `project_file`, and the gated `dsh_minimal`/`tool_description` projection. Other surfaces remain open. |
| Authority/precedence policy vocabulary | Phase 1 | Keep policy explicit and separate from text ordering; conflict experiments get their own condition label. |
| Ambient instruction isolation policy | Phase 4 | Unexpected global/project instructions must be detected and classified before a run is valid. |
| `tool_set_ref` semantics and independence from rule surfaces | Phase 1 | Reserve the reference now; define complete tool-set capabilities only when StepCLI supports them. |
| `AGENTS.md` boundary 8 wording on deterministic verifiers | nothing immediately | §8.2. Descriptively wrong for this source family. |
| `AGENTS.md` opportunity-check timing | Phase 3 lint | Currently written as an authoring-time gate; §6.1 makes opportunity a run-time status. |
| Source repository shortlist for Phase 0 | Resolved | See [`docs/source-shortlist.md`](../source-shortlist.md). Both source pools are eligible for cleaning; later analyses retain `source_pool`. |
