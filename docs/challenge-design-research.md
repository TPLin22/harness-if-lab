# Challenge Design Research

**Status:** durable research note; design guidance, not a frozen schema

**Research snapshot:** 2026-08-29 (Asia/Hong_Kong)

This document records evidence and design decisions for making Harness-IF Lab
rules, coding tasks, and combined Items genuinely challenging. It is about data
curation and measurement. It is not an implementation specification for a
particular agent harness.

## Executive Summary

A rule is not useful merely because it sounds unusual, is long, or comes from a
well-known project. It is useful for this study when all of the following are
true:

1. The rule asks for one observable behavior and is not already guaranteed by
   the task's ordinary solution.
2. The task creates a real opportunity to perform, violate, or intentionally
   decline that behavior.
3. The rule has an auditable witness and a verifier whose uncertainty is known.
4. The intervention can be compared with a like-for-like no-injection
   condition.
5. The rule remains meaningful when its wording, repository, and task are
   changed.

The main practical implication is that difficulty must be represented as a
vector, not a single score. At minimum we need separate evidence for:

- **rule difficulty:** modality, conflict with an observed default, semantic
  implicitness, scope, and verifier difficulty;
- **opportunity:** whether the task actually exposes the actor, object, trigger,
  and exception needed to judge the rule;
- **composition:** independent rules versus dependency chains, persistent
  obligations, shared behavior resources, and deliberate priority conflicts;
- **task/execution difficulty:** repository exploration, work units, dependency
  depth, integration and regression obligations, and environment stability;
- **measurement difficulty:** deterministic coverage, judge reliability,
  missing artifacts, partial outcomes, and cascade failures.

The first pilot should therefore use parent Items and a pre-registered
difficulty ladder. Keep the task fixture fixed while adding one interpretable
factor at a time. Report task success, each rule's pass/fail/no-opportunity
verdict, joint success, and verifier health separately. Do not promote an Item
to a score-bearing release just because a pilot happened to separate a few
models; that creates selection optimism.

## 1. Research Question

The target phenomenon is instruction following under a declared rule, rather
than generic coding competence:

> When a task naturally admits a behavior, can the agent carry out a supplied
> constraint instead of reverting to a learned, habitual, or otherwise
> preferred behavior?

This wording has two consequences.

First, a rule that agrees with the default solution can produce a high score
without testing responsiveness. Such a rule can still be useful as an
`align_prior` control, but it should not be the only kind of rule in a study.

Second, a rule can be hard for the wrong reason. If the task never requires a
match arm, a commit trailer, a documentation build, or a second integration
path, a failure to observe that behavior is not a model violation. It is a
design failure or a `no_opportunity` outcome.

### 1.1 What counts as a challenging rule

The following are useful signals, but none is sufficient alone:

- the instruction opposes a stable no-injection behavior (`against_prior`);
- it uses a command or prohibition (`require` / `forbid`) rather than a loose
  preference;
- it is conditional, quantitative, or negative (for example, a maximum, an
  exception, or a prohibition on an otherwise convenient shortcut);
- it requires cross-file, temporal, causal, or repository-topology reasoning;
- it must persist across multiple turns or development stages;
- the obvious local patch can pass a narrow test while violating the broader
  requirement;
- the evidence is observable but requires more than a single regular
  expression, such as an AST, diff, command trace, or functional chain.

These signals should be recorded as hypotheses and then checked against a
baseline, an opportunity witness, and actual verifier behavior. They should not
be collapsed into an unsupported `hard` label.

### 1.2 What does not count as evidence of difficulty

Do not infer challenge from any one of the following:

- word count or number of clauses in the rule text;
- a source document's use of `hard`, `important`, or emphatic typography;
- task length, number of turns, lines of code, or number of files alone;
- a model failing a task when the rule was not delivered or the artifact was
  missing;
- a single LLM judge score without calibration;
- a high failure rate caused by a flaky environment or a broken hidden test;
- selecting only the Items that separated models during an exploratory pilot.

## 2. Evidence From Recent Work

The papers below are used as construction and measurement references. Their
reported numbers describe their own datasets and protocols; they are not
assumptions about the HIF Lab corpus.

For a one-year-first reading relative to this snapshot (2025-08-29 through
2026-08-29), the 2026 papers and SWE-Bench Pro are the primary evidence. The
2025 instruction-following papers retained below predate that window, but are
kept as narrowly scoped foundational comparators because they contain directly
useful constraint-construction and verifier methods. They should not be used
to imply that their model-capability results describe current flagship models.

### 2.1 Harness-IF (primary reference)

**Generalizing Instruction Following in Agent Harnesses**, arXiv:2608.11727,
<https://arxiv.org/abs/2608.11727> (version reviewed 2026-08-29).

The paper is the closest methodological precedent for this project. Its
construction section states that candidate constraints must be **“atomic,
verifiable, non-trivial, and suitable for coding-agent tasks.”** The reported
pipeline is:

1. survey public project-instruction and contributor material;
2. atomize and normalize recurring requirements;
3. use reviewed LLM proposals to fill taxonomy gaps;
4. assemble rules with coding fixtures and surface assignments;
5. review and filter Items before evaluation;
6. retain rule-level evidence, not just a task reward.

The released coding panel reports 80 working candidates reduced to 60 quality-
audited Items. Its library contains 642 atomic constraints. Each Item injects
25--35 rules, of which 10--27 are scorable when the task creates an applicable
opportunity. Across the panel, 302 distinct library rules are instantiated and
256 receive at least one verdict. The evaluation is 12 model builds by 60
Items over three rounds (2,160 runs).

The most important construction result is the prior distinction. The paper
labels a rule `align-prior`, `against-prior`, or `neutral`, and uses a
zero-injection probe to estimate the behavior that appears without the target
instruction. A label from nine probe builds is treated as a consensus when at
least five agree. Every evaluated model performs worse on the against-prior
subset; the reported mean aggregate-versus-against-prior gap is 5.81 percentage
points. Per-rule pass-rate vectors also correlate across models (reported range
0.57--0.89, mean 0.80), suggesting a shared difficulty ordering even when
aggregate model scores differ.

The paper's modality and family breakdown gives useful hypotheses for HIF:

- commanding (`require` / `forbid`): 76.0% accuracy;
- numeric limits: 79.4%;
- conditional requirements: 79.7%;
- preferences: 90.6%;
- output-control family: 70.9%, the lowest family for 11 of 12 models;
- quantitative family: 82.6%.

These results support oversampling command, output-control, workflow, and
counter-default rules, while retaining aligned preferences as controls. They
do not justify assigning a difficulty label from modality alone.

The scoring appendix is equally relevant. It uses regex, AST, cross-file,
command-output, hybrid, and LLM-judge methods. LLM/hybrid checks use three
votes. `no-opportunity` is excluded from the pass/fail denominator. A missing
artifact that causes many dependent rules to fail is handled by cascade
deduplication, and a rule is marked `untestable-design-gap` when at least 50%
of tested agents lack the artifact needed to evaluate it. The reported judge-
swap agreement is only 62.1% (Cohen's kappa 0.163 on the paired clean subset),
so judge uncertainty is a first-class result rather than a footnote.

Finally, the authors warn that selecting Items for pilot difficulty or
discriminativeness can produce **selection optimism**. HIF should preserve the
full candidate disposition and use a holdout or pre-registered calibration
split before reporting a headline score.

### 2.2 Instruction-following data construction

**IFBench / Generalizing Verifiable Instruction Following**, arXiv:2507.02833,
<https://arxiv.org/abs/2507.02833>.

The useful idea is to separate unseen prompts from unseen constraints and to
make the constraint executable where possible. Its filtering and evaluation
emphasize conflict checking, parameter-range extrapolation, and avoiding
template saturation. For HIF, a rule should be held out by wording and by
semantic family, not merely paraphrased from a training template.

**MultiCodeIF / ConstraGen**, arXiv:2507.00699,
<https://arxiv.org/abs/2507.00699>.

Constragen increases the number of constraints progressively, adding one
constraint per level. This makes the marginal effect of composition visible.
It also shows why an arbitrary Cartesian product is unsafe: independently
valid constraints may become incoherent or jointly unverifiable. Explicit
constraints are easier than implicit or abstract ones, so a challenging panel
needs both, with the latter receiving stronger evidence requirements.

**CodeIF**, arXiv:2502.19166,
<https://arxiv.org/abs/2502.19166>.

This work emphasizes atomic constraints, a multi-family taxonomy, and an
explicit dependency between an instruction and a code opportunity. Its harder
set uses more constraints and more complex combinations. The transfer lesson
is to curate the opportunity together with the rule; do not attach a generic
style sentence to a task after the fact.

**CodeIF-Bench**, arXiv:2503.22688,
<https://arxiv.org/abs/2503.22688>.

The benchmark derives strategies from real code-review comments and gives each
instruction an independent assertion or test. It treats repository context
and multi-round interaction as separate difficulty axes. HIF should similarly
retain rule-level assertions and avoid letting the overall SWE-bench reward
stand in for a rule verdict.

### 2.3 Coding-agent benchmark construction

**SWE-Bench Pro**, arXiv:2509.16941,
<https://arxiv.org/abs/2509.16941>.

The benchmark removes trivial 1--10 line tasks, favors multi-file work and
larger patches, and uses both fail-to-pass and pass-to-pass tests. It filters
flaky runs through repeated execution, removes irrelevant or overly broad
tests, and uses public, held-out, and commercial splits to reduce contamination.
For HIF, a rule challenge should not be accepted when the base task itself is
trivial or when the verifier's signal is unstable.

**LoopsBench**, arXiv:2608.00267,
<https://arxiv.org/abs/2608.00267>, repository
<https://github.com/microsoft/Loopsbench>.

LoopsBench represents a long task as a dependency DAG of development units.
Tests for the ready frontier are released as work progresses, while completed
units continue to generate regression obligations. The repository stores a
task manifest, unit and module DAGs, solutions, test scripts, and source
provenance. HIF can use the same distinction between shallow independent rule
opportunities and deep rules whose earlier choices constrain later stages.

**Benchmarking the Residual**, arXiv:2607.27283,
<https://arxiv.org/abs/2607.27283>.

This work cautions that long trajectories are not automatically hard. It
separates local stage difficulty, workload, dependency depth, and intrinsic
action horizon. A useful diagnostic is to record local success probabilities
`q_i`, compare the product `P_expected = product(q_i)` with the observed
long-horizon success, and retain `N_work`, `H_dep`, and the intrinsic horizon.
HIF should not use turns, LOC, or token count as a substitute for these
quantities.

**CodeSpec**, arXiv:2607.26777,
<https://arxiv.org/abs/2607.26777>, repository
<https://github.com/zhu-zhu-ding/CodeSpec>.

CodeSpec links a natural-language requirement to repository evidence, a
functional chain, and executable architecture/behavior specifications. The
lesson is especially important for cross-file rules: a local patch can pass a
unit test while leaving the feature chain broken. Every such rule needs a
requirement-to-evidence map and more than one verification layer.

**SWE-Doctor**, arXiv:2607.00990,
<https://arxiv.org/abs/2607.00990>.

The authors show that a single reproduction test often covers only one
manifestation of a bug, allowing a partial patch to look complete. Their
multi-faceted tests, runtime diagnosis, and completeness checks motivate a
HIF `rule x affected-behavior-path` coverage matrix. A rule pass should mean
all relevant facets were checked, not merely that one visible test passed.

**SWE-Refactor-Bench**, arXiv:2608.23564,
<https://arxiv.org/abs/2608.23564>, repository
<https://github.com/Einsia/SWE-Refactor-Bench>.

Its three-stage protocol audits the migration, checks behavior, and then uses
adversarial verification. The purpose is to catch agents that retain the old
implementation, edit only tests, or make a superficial replacement. This is
a direct model for HIF's anti-shortcut gate and for separating “task behavior
is correct” from “the requested constraint was genuinely applied.”

### 2.4 Additional evaluation safeguards

**AI Harness Engineering**, arXiv:2605.13357,
<https://arxiv.org/abs/2605.13357>.

This paper treats the model, environment, context, tools, and verification
protocol as one experimental system and recommends deterministic checks,
reproduction, and failure attribution. Its episode-level outcome vocabulary
distinguishes verified success, assisted success, unverified success, failure,
and unsafe/invalid outcomes. HIF should preserve equivalent distinctions in
its trial evidence, without turning them into a harness-specific schema here.

**RAMP**, arXiv:2605.27492,
<https://arxiv.org/abs/2605.27492>.

RAMP's persistent repository workflow and recovery artifacts distinguish a
current-stage failure from a downstream cascade caused by an earlier mistake.
This supports recording recovery/no-recovery conditions and keeping upstream
artifact failures separate from rule violations.

**Cross-Benchmark Generalization in Long-Horizon Agents**, arXiv:2608.00181,
<https://arxiv.org/abs/2608.00181>.

The reported cross-benchmark transfer is evidence that useful generalization
can be studied through behavior such as local-goal formation, maintaining a
parent goal after repair, and explicit completion verification. For HIF this
supports cross-repository and semantic holdouts rather than judging
generalization from a shared Markdown format.

## 3. Real Repository Constraint Evidence

The following excerpts were reviewed from official upstream documents on
2026-08-29. They are source evidence and examples for curation, not yet
canonical HIF rules. Each entry records a short excerpt, why it may be
challenging, and a possible observable opportunity. The source repository,
path, license, and retrieval date must remain in the eventual provenance
record.

### R1. Linux kernel: one problem per patch

- **Source:** `torvalds/linux`,
  `Documentation/process/submitting-patches.rst`, “The canonical patch
  format”; GPL-2.0 WITH Linux-syscall-note (`COPYING`).
- **Pinned snapshot:** commit
  `cf72cbb39da84b6f02f90c07f33b102fc10b16f0`, content SHA-256
  `d8192ff9d09e394e63d724a2201ca1bf5a7d64c8c3ab404294992914272c821a`;
  lines 81--83; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/torvalds/linux/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/Documentation/process/submitting-patches.rst>
- **Excerpt:** “Solve only one problem per patch. If your description starts
  to get long, that's a sign that you probably need to split up your patch.”
- **Why it is challenging:** The agent must distinguish coupled changes from
  unrelated scope, not merely count files or lines.
- **Observable opportunity:** A task with two tempting fixes can require a
  split patch or a structured explanation of the split. Evidence can combine
  commit/diff structure and the final description.
- **Likely verifier:** diff partition plus a rubric for causal scope; avoid
  scoring if the task has only one inseparable change.

### R2. Linux kernel: Developer's Certificate of Origin

- **Source:** same document, “Sign your work - Developer's Certificate of
  Origin”; GPL-2.0 WITH Linux-syscall-note.
- **Pinned snapshot:** the same commit and content hash as R1; retrieved
  2026-08-29 (DCO text at lines 404--407; trailer example at lines
  435--440).
- **URL:** <https://raw.githubusercontent.com/torvalds/linux/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/Documentation/process/submitting-patches.rst>
- **Excerpt:** “The sign-off is a simple line at the end of the explanation ...
  certifies that you wrote it or otherwise have the right to pass it on as an
  open-source patch.”
- **Why it is challenging:** This is provenance and metadata reasoning, not a
  code-style check; the actor and event must be explicit.
- **Observable opportunity:** A patch submission fixture can require a valid
  `Signed-off-by` trailer whose identity matches the configured author.
- **Likely verifier:** commit trailer parser plus identity consistency. Do not
  score it in a task that never creates a commit or submission event.

### R3. Linux kernel: indentation semantics

- **Source:** `torvalds/linux`, `Documentation/process/coding-style.rst`,
  “Indentation”; GPL-2.0 WITH Linux-syscall-note.
- **Pinned snapshot:** commit
  `cf72cbb39da84b6f02f90c07f33b102fc10b16f0`, content SHA-256
  `332454d2ab9a0462dd9f292c52291cf3b5e1afcd638aa06df15f557c47a126f5`;
  lines 15--23; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/torvalds/linux/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/Documentation/process/coding-style.rst>
- **Excerpt:** “Tabs are 8 characters, and thus indentations are also 8
  characters.”
- **Why it is challenging:** Visual width, tab bytes, and structural nesting
  can disagree; a formatter-only shortcut may alter unrelated code.
- **Observable opportunity:** A focused patch with nested code and a checker
  that examines raw whitespace and nesting depth.
- **Likely verifier:** deterministic whitespace/AST checks, with surrounding
  context retained so a broad reformat is detectable.

### R4. LLVM: follow local style

- **Source:** `llvm/llvm-project`, `llvm/docs/CodingStandards.md`, “The Golden
  Rule”; Apache-2.0 WITH LLVM-exception (`LICENSE.TXT`).
- **Pinned snapshot:** commit
  `b6fee078ec05d30da7bb749a9d3deb83f2a52065`, content SHA-256
  `d5a32c3cfba2f6bc8e09fdc3e59f5466406bc6661c83081ddbe279f7128d0522`;
  lines 18--20 and 26--33; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/llvm/llvm-project/b6fee078ec05d30da7bb749a9d3deb83f2a52065/llvm/docs/CodingStandards.md>
- **Excerpt:** “If you are extending, enhancing, or bug fixing already
  implemented code, use the style that is already being used so that the
  source is uniform and easy to follow.”
- **Why it is challenging:** The correct style is contextual. A global linter
  cannot decide the local convention or whether a reformat is justified.
- **Observable opportunity:** A repository fixture with intentionally mixed
  local conventions, where the touched region has a clear neighboring style.
- **Likely verifier:** changed-line versus surrounding-line AST/text features,
  plus a separate broad-reformat audit.

### R5. LLVM: prefer project support libraries

- **Source:** `llvm/llvm-project`, `llvm/docs/CodingStandards.md`, “C++
  Standard Library”; Apache-2.0 WITH LLVM-exception.
- **Pinned snapshot:** the same commit and content hash as R4; retrieved
  2026-08-29 (C++ library guidance at lines 96--104).
- **URL:** <https://raw.githubusercontent.com/llvm/llvm-project/b6fee078ec05d30da7bb749a9d3deb83f2a52065/llvm/docs/CodingStandards.md>
- **Excerpt:** “When both C++ and the LLVM support libraries provide similar
  functionality ... preferable to use the LLVM library.” The examples state
  that `llvm::DenseMap` should almost always be used instead of `std::map`.
- **Why it is challenging:** API choice depends on project semantics,
  ownership, performance, and local convention; it is not a generic C++ rule.
- **Observable opportunity:** A task that introduces or replaces a container
  in an LLVM-style component, with an architecture/performance rationale.
- **Likely verifier:** AST/API check plus a compile and behavior check; do not
  penalize a justified exception without an explicit opportunity.

### R6. PyTorch: run the project lint path

- **Source:** `pytorch/pytorch`, `CONTRIBUTING.md`, “Linting before committing”;
  BSD-3-Clause (`LICENSE`).
- **Pinned snapshot:** commit
  `3c844ed711e65bdb162f11e7dabf177aeca433fc`, content SHA-256
  `42f2d4eeca2aec9ac564f52ed3490dc6b8f3b6f20596957d24a9306f4c7722a8`;
  lines 1253--1274; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/pytorch/pytorch/3c844ed711e65bdb162f11e7dabf177aeca433fc/CONTRIBUTING.md>
- **Excerpt:** “All linting (clang-tidy, flake8, formatting, and more) is run
  through lintrunner ... Fix the code so that no errors are reported when you
  re-run the above check again, and then commit the fix.”
- **Why it is challenging:** The required check is heterogeneous and its
  changed-file selection depends on the merge base; running one familiar tool
  is insufficient.
- **Observable opportunity:** A multi-language patch where the project command
  reports an initial error and a clean rerun is required before completion.
- **Likely verifier:** command output, exit status, and commit/event trace.

### R7. PyTorch: version-coupled documentation build

- **Source:** `pytorch/pytorch`, `CONTRIBUTING.md`, “Building documentation”;
  BSD-3-Clause.
- **Pinned snapshot:** the same commit and content hash as R6; retrieved
  2026-08-29 (documentation-build guidance at lines 571--606 and Doxygen
  check at lines 638--640).
- **URL:** <https://raw.githubusercontent.com/pytorch/pytorch/3c844ed711e65bdb162f11e7dabf177aeca433fc/CONTRIBUTING.md>
- **Excerpt:** The instructions couple a supported Python version with Node,
  KaTeX, `make html`, and `./check-doxygen.sh` checks.
- **Why it is challenging:** The behavior spans environment preflight,
  generated output, documentation, and CI rather than one source file.
- **Observable opportunity:** A docs change whose local build succeeds only
  with the declared versions and whose generated/API checks must also pass.
- **Likely verifier:** version preflight, command output, generated-file diff,
  and Doxygen validity.

### R8. CPython: branch, compatibility, and review policy

- **Source:** `python/devguide`,
  `getting-started/pull-request-lifecycle.rst`; CC0 1.0 Universal (the
  `python/devguide` repository's `LICENSE`, not CPython's PSF-2.0 license).
- **Pinned snapshot:** commit
  `261dc2116ca81985c5c0cfc59db5a251d2c8db96`, content SHA-256
  `b6b9d15adc659fd702d0e77c1f16eebab37075b9f3135724afc8ab0556e96982`;
  lines 49--53 and 156--175; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/python/devguide/261dc2116ca81985c5c0cfc59db5a251d2c8db96/getting-started/pull-request-lifecycle.rst>
- **Excerpt:** “In general all changes are made against the main branch first”;
  systematic PEP 8/PEP 7 deviations can put a PR on hold, and formatting-only
  PRs are usually rejected.
- **Why it is challenging:** Branch target, backward compatibility, tests,
  style exceptions, and review intent interact. A formatting-only patch can be
  locally clean while still violating project policy.
- **Observable opportunity:** A PR fixture with a maintenance branch, a
  compatibility concern, and a tempting formatting-only change.
- **Likely verifier:** branch metadata, tests, diff classification, and a
  compatibility note; process events must be present before scoring.

### R9. PostgreSQL: design and evidence before submission

- **Source:** `postgres/postgres` wiki, “Submitting a Patch”; PostgreSQL
  License under the wiki copyright policy.
- **Pinned snapshot:** wiki revision `38858` (2024-04-30); the oldid raw
  endpoint was not reachable from the audit environment, so the revision ID
  and retrieval date are the authoritative locator. Retrieved 2026-08-29.
- **URL:** <https://wiki.postgresql.org/index.php?title=Submitting_a_Patch&oldid=38858&action=raw>
- **Excerpt:** “Get community buy-in at this level of detail before you start
  coding ...” and “Resist the temptation to build a giant patch all at once.”
  The checklist also asks for tests, documentation, platform/build status,
  rationale, and reproducible performance evidence.
- **Why it is challenging:** The rule spans social design review, patch scope,
  tests, docs, and performance claims. It is not meaningful without a review
  or submission opportunity.
- **Observable opportunity:** A workflow fixture with a review gate and a
  performance claim that requires a reproducible measurement artifact.
- **Likely verifier:** event log, changed-file scope, test/docs evidence, and
  benchmark reproducibility. Keep this in a workflow/calibration track unless
  the event is fully simulated.

### R10. Rust: changes belong to the owning subrepository

- **Source:** `rust-lang/rust`, `CONTRIBUTING.md`, “Making changes to subtrees
  and submodules”; Apache-2.0/MIT (`LICENSE-APACHE`, `LICENSE-MIT`).
- **Pinned snapshot:** commit
  `58ae2c4315128abc40be24b429dfb68bf27510b3`, content SHA-256
  `814cdb2341ab5f49a0033bc850b8458fab2ba84636f1b33e89d3bcaa5435880f`;
  lines 15--22; retrieved 2026-08-29.
- **URL:** <https://raw.githubusercontent.com/rust-lang/rust/58ae2c4315128abc40be24b429dfb68bf27510b3/CONTRIBUTING.md>
- **Excerpt:** “For submodules, changes need to be made against the repository
  corresponding to the submodule, and not the main rust-lang/rust repository.”
- **Why it is challenging:** The agent must understand repository topology and
  route a change to the correct owner; a source edit in the wrong checkout can
  look locally successful but be unmergeable.
- **Observable opportunity:** A fixture with a submodule or gitlink and a task
  that requires a change in the owned repository plus a pointer update.
- **Likely verifier:** gitlink/path ownership and cross-repository diff checks.

### 3.1 Additional task patterns reviewed

The `harbor-framework/terminal-bench-2-1` repository is a useful source of
task-level opportunities rather than canonical rules:
<https://github.com/harbor-framework/terminal-bench-2-1>.

- `constraints-scheduling` combines hard availability constraints with
  preference tie-breakers, UTC conversion, read-only inputs, and a structured
  ICS artifact.
- `cancel-async-tasks` combines concurrency limits, keyboard interruption,
  cleanup semantics, and queued-task edge cases.
- `fix-code-vulnerability` combines a code fix, CWE identification, an exact
  `/app/report.jsonl` schema, and both original and additional tests.

These examples are valuable because they expose multiple observable outputs
and anti-shortcut opportunities. Their task metadata, however, is not by
itself proof of difficulty; each candidate still needs a fixture, witness, and
verifier review.

## 4. A Five-Dimensional Difficulty Model

The following is a design vocabulary, not a formal schema. It is intentionally
factorized so later analyses can ask which dimension caused a failure.

### 4.1 Rule intrinsic difficulty

Record at least:

- `modality`: require, forbid, conditional-require, limit-min,
  limit-max, prefer, or allow;
- `prior_hypothesis`: align, against, neutral, or unknown, with the probe
  protocol and cohort recorded separately;
- `negative_or_counterintuitive`: whether compliance means suppressing an
  otherwise attractive action;
- `semantic_implicitness`: explicit, contextual, or causal/intent-level;
- `scope`: line, file, repository, process, or multi-stage;
- `exception_count` and trigger complexity;
- `observability`: final text, diff, AST, command/event, runtime behavior, or
  a combination;
- `verifier_type` and expected false-positive/false-negative risk.

`against_prior` is an empirical hypothesis, not a statement about training
data. A zero-injection probe can support it, but the probe cohort may overlap
the evaluated models. Preserve that lineage and report the limitation.

### 4.2 Task opportunity and exposure

For every scored rule, identify an opportunity witness with:

- actor: who can perform the behavior;
- object: which file, command, API, artifact, or event is affected;
- trigger: what task condition makes the behavior relevant;
- scope: where and for how long it applies;
- exception: when the rule does not apply;
- expected evidence: the exact diff, event, output, or runtime state that can
  prove pass or fail.

An opportunity witness may be a fixture, a hidden test, a command trace, a
trajectory event, or a structured review artifact. If it cannot be reproduced
without reading the evaluator's private oracle, the rule is not ready for a
score-bearing Item.

Use `no_opportunity` when the trigger never occurs. Do not turn it into a
failure, and do not silently remove it from the review ledger. A high
no-opportunity rate is evidence that the task/rule pairing is poor.

A **must-scored opportunity** is a stronger, pre-registered form of exposure:
the fixture guarantees that the rule's trigger occurs, the relevant actor and
object are available, and the verifier can identify the expected evidence. If
the agent omits the required behavior in that situation, the outcome is a
scorable failure (subject to delivery and artifact-health checks), not
`no_opportunity`. A rule should not be marked `must_scored` merely because a
reviewer can imagine a possible trigger; the guarantee must be demonstrated
by the task fixture or an auditable execution path. Items without at least one
healthy must-scored rule remain calibration or plumbing candidates.

### 4.3 Composition difficulty

Classify a rule set before running it:

- **independent:** each rule uses a separate behavior resource;
- **dependency chain:** an earlier decision changes a later opportunity;
- **shared resource:** several rules constrain the same output, API, or file;
- **persistent:** a rule remains active across stages or turns;
- **deliberate precedence:** two authorities intentionally conflict under a
  declared policy;
- **accidental incoherence:** the combination is not jointly satisfiable and
  should be rejected.

Rule count is only a weak proxy. Record dependency depth, number of branches,
shared resources, required ordering, and the size of the smallest jointly
valid solution. Do not generate an unrestricted Cartesian product of rules.

### 4.4 Task and execution difficulty

Record, where applicable:

- repository exploration breadth and relevant modules;
- number of independently testable work units (`N_work`);
- dependency depth (`H_dep`) and intrinsic action horizon;
- modified-file count and patch size, as descriptive—not decisive—variables;
- behavior reproduction and integration paths;
- regression obligations after an earlier unit is complete;
- test/build/toolchain setup cost;
- environment stability and timeout/resource risk.

For long tasks, estimate local stage success `q_i` and compare the expected
product with natural long-horizon success. This distinguishes a genuinely deep
dependency chain from a sequence that is merely verbose.

### 4.5 Measurement difficulty

Store separately:

- rule verdict: `pass`, `fail`, `partial`, `no_opportunity`, `unknown`, or
  `delivery_failure`;
- task verdict and joint verdict;
- evidence type and artifact hashes;
- deterministic checker result, judge result, and judge confidence;
- repeatability/flakiness results;
- missing-artifact and cascade status;
- judge-swap or human-reference calibration where applicable.

The measurement vector is part of the Item's qualification. A rule that is
intrinsically interesting but cannot be measured reliably should remain a
calibration candidate, not silently enter the main denominator.

## 5. Rule, Task, and Item Construction

### 5.1 Rule admission

For each source paragraph:

1. retain the raw source pointer, license, retrieval date, and short permitted
   excerpt;
2. split bundled prose into atomic candidate behaviors;
3. preserve modality (`must`, `should`, `prefer`, exceptions) rather than
   strengthening it during paraphrase;
4. write a neutral canonical statement without a product or harness name when
   generalization is intended;
5. describe the actor, object, trigger, scope, exception, and evidence;
6. assign a provisional family/modality and a possible prior hypothesis;
7. list plausible shortcut implementations and false-positive cases;
8. have a reviewer reject duplicates, incoherent wording, or rules with no
   plausible opportunity.

Source-grounded does not mean release-ready. A real project may state a rule
that is socially meaningful but impossible to expose in a coding task. Keep
such candidates with an explicit `unavailable_opportunity` disposition.

### 5.2 Task profiling

Before composing an Item, profile the task independently of model outcomes:

- pin the repository/base revision and evaluator revision;
- clean benchmark framing while preserving the neutral coding objective;
- list affected modules and plausible behavior paths;
- identify work units, dependency edges, and regression obligations;
- write the opportunity witness for each proposed rule family;
- identify tempting shortcuts and incomplete patches;
- confirm that answer, gold patch, hidden tests, and evaluator internals are
  not model-visible;
- run the task verifier repeatedly enough to identify flaky tests.

Do not choose tasks because a preliminary intervention score is low or high.
That makes task selection post-treatment. Task selection and rule
qualification must be separate ledgers.

### 5.3 Item composition

Use a parent Item where possible:

- hold repository, task statement, model settings, budget, and verifier fixed;
- start with one scored rule and a no-injection counterpart;
- add one independent rule to test simple composition;
- add one dependency or persistence edge to test interaction;
- add a cross-file, conditional, or quantitative rule;
- only then test a deliberate authority/precedence condition.

Every added rule should have a reason, an opportunity witness, and a verifier.
If adding a rule makes the set unsatisfiable, the result is a composition
rejection, not a hard Item. Keep `observed` plumbing or exploratory rules out
of the score denominator.

The usual release floor should require at least one `must_scored` rule with a
real opportunity and a deterministic or structurally auditable verifier. An
Item with no such rule may still be useful for plumbing or calibration, but it
must be labeled accordingly.

### 5.4 Difficulty ladder

The following ladder is a starting point for preregistration:

| Level | Added factor | Required evidence |
| --- | --- | --- |
| `L0` | One ordinary rule with one clear opportunity | deterministic witness and paired baseline |
| `L1` | Two or three independent rules | separate verdicts and joint satisfiability check |
| `L2` | A dependency chain or persistent obligation | unit DAG, order, and regression obligation |
| `L3` | Cross-file, conditional, or exact quantitative behavior | coverage matrix plus structural/behavior checks |
| `L4` | An against-prior or counter-intuitive rule | zero-injection prior evidence and behavior-diff probe |
| `L5` | Multiple surfaces or a deliberate precedence condition | explicit authority policy, conflict witness, and independent surface delivery evidence |

Use the same task fixture for neighboring levels whenever possible. If the
fixture must change, record the change as a separate factor. The ladder is not
a universal ranking; it makes the source of an observed difficulty difference
inspectable.

## 6. Verification and Scoring

### 6.1 Evidence hierarchy

Prefer, in order:

1. exact command output or exit status;
2. AST or structured-file validation;
3. cross-file and git/diff checks;
4. behavior and integration tests;
5. a constrained LLM judge for residual semantic ambiguity.

An LLM judge can be appropriate for intent, rationale, or contextual style,
but it should not replace a deterministic check that the task makes possible.
Use independent votes, freeze the rubric, retain the individual decisions,
and measure judge-swap or human-reference agreement on a calibration sample.

### 6.2 Separate denominators

At minimum report:

- `task_success`: the independent coding-task verifier passed;
- `rule_pass_rate`: pass over applicable pass/fail opportunities only;
- `joint_success`: task success and all `must_scored` rules passed;
- `no_opportunity_rate`;
- `delivery_failure_rate`;
- `verifier_failure_rate`;
- `partial_rate`;
- baseline/intervention difference, only when the pair is actually run.

Do not use task reward as a rule verdict. A task can pass while a style or
workflow rule fails, and a task can fail for an implementation bug while the
rule was delivered and followed.

### 6.3 Coverage and partial compliance

For each rule, maintain a matrix of affected behavior paths and evidence
checks. Use `partial` when only some required facets are satisfied. Examples:

- a test is added but one required path remains untested;
- a migration changes the new API but leaves one old dependency;
- one branch uses the required exhaustive match while another retains a
  wildcard;
- a workflow artifact is correct but the required review event is absent.

This prevents a single happy-path test or final message from masking partial
compliance.

### 6.4 Cascade handling

If one missing artifact causes several dependent checks to fail, retain the
root failure and mark dependent checks as `no_opportunity` or cascade-linked,
rather than multiplying the same failure. If at least half of tested agents
lack the artifact needed to evaluate a rule, flag `untestable-design-gap` and
exclude it from the release denominator until the design is repaired.

### 6.5 Baselines and causal interpretation

An intervention pair should keep task, repository revision, model, tool set,
budget, environment, and verifier constant while changing only the declared
rule injection. A zero-injection baseline is required for claims about
departing from default behavior. A missing baseline may remain a candidate,
but its result is descriptive delivery evidence, not a causal estimate.

For prior studies, use a withheld-rule or zero-injection probe and report:

- probe cohort and overlap with evaluated models;
- consensus threshold and unresolved labels;
- baseline behavior evidence;
- intervention behavior difference;
- sensitivity to the prior-label threshold.

## 7. Qualification Gates

The following gates should be checked before an Item becomes score-bearing.
They are review gates, not an implementation schema.

### Gate 1: provenance and rights

The source URL/path, immutable revision or content hash, license, retrieval
date, excerpt, and transformation lineage are recorded. A generalization rule
does not retain unnecessary product or harness names in its model-visible
wording. Calibration material remains labeled as such.

### Gate 2: prior-conflict and behavior-diff

There is stable evidence of a no-injection behavior when a counter-default
claim is made, and adding the rule can change an observable behavior. If no
behavior difference is possible, classify the rule as an aligned control or
reject it for a counter-default study.

### Gate 3: opportunity

The task creates the actor/object/trigger/scope needed for the rule, and the
opportunity witness is reproducible without evaluator leakage. The expected
opportunity rate and exception cases are written down before running models.

### Gate 4: coverage and verifier

Every scored rule has at least one deterministic, structural, or calibrated
semantic verifier. Cross-file or cross-module rules have a coverage matrix,
not just one reproduction test. False-positive, false-negative, and flaky
paths are tested.

### Gate 5: dependency and horizon

The Item records `N_work`, `H_dep`, intrinsic horizon, ordering, and regression
obligations. Neighboring ladder levels differ by an identified factor rather
than an uncontrolled change in task size.

### Gate 6: anti-shortcut

Review for test-only edits, copying the old implementation, changing inputs
to avoid the requirement, leaving an old dependency in place, superficial
renames, broad formatting, and any other path that can satisfy a narrow
checker without satisfying the rule.

### Gate 7: causal comparability

The paired baseline and intervention use the same task, revision, model,
environment, budget, and verifier. The intended change is isolated. Without a
run baseline, retain `candidate` status and do not publish a causal rule
score.

### Gate 8: measurement health

The trial distinguishes delivery failure, task failure, rule failure, partial,
no-opportunity, missing artifact, and unknown. Repeated runs expose flakiness;
judge calibration and cascade handling are recorded.

### Gate 9: calibration and discrimination

The pilot is not uniformly passed or uniformly failed. It includes controls,
against-prior rules, and at least one interaction level. Any selection based
on pilot discrimination is applied only to a pre-registered calibration split;
the release or holdout remains untouched.

## 8. Suggested Data Vocabulary (Illustrative)

This section deliberately does not freeze the project's future YAML schema.
It lists information that should survive into the eventual contracts.

### 8.1 Rule record

```yaml
rule:
  source_ref: <repo/path/revision-or-content-hash>
  source_pool: generalization | calibration
  statement: <one observable constraint>
  modality: require | forbid | conditional-require | limit-min | limit-max | prefer | allow
  scope: <actor/object/scope>
  exceptions: [<explicit exception>]
  prior_hypothesis: align | against | neutral | unknown
  opportunity_tags: [<behavior family>]
  verifier_type: regex | ast | cross-file | command-output | hybrid | llm-judge
  shortcut_risks: [<known bypass>]
  status: candidate | calibration | release-eligible | released
```

### 8.2 Task profile

```yaml
task:
  source_revision: <immutable dataset/repository reference>
  objective: <cleaned neutral coding objective>
  work_units: [<unit id>]
  dependency_edges: [[<before>, <after>]]
  regression_obligations: [<unit or behavior path>]
  opportunity_witnesses: [<rule family and evidence>]
  hidden_oracle_policy: <what is not model-visible>
  shortcut_audit: <review record>
  environment_repeatability: <trial evidence>
```

### 8.3 Item qualification

```yaml
item:
  task_ref: <task id>
  rule_bindings: [<rule id, role, declared surface/policy>]
  composition_class: independent | dependency | persistent | precedence
  difficulty_hypotheses: <factorized record, not one hard label>
  baseline_ref: <paired zero-injection item>
  opportunity_review: <witness and expected exposure>
  verifier_review: <coverage and reliability>
  qualification_status: candidate | calibration | release-eligible | released
```

### 8.4 Trial evidence

```yaml
trial:
  intended_delivery: <what was requested>
  effective_delivery: <what was observed>
  task_verdict: pass | fail | unknown
  rule_verdicts: [pass | fail | partial | no_opportunity | delivery_failure | unknown]
  joint_verdict: pass | fail | unknown
  artifact_refs: [<hash/path>]
  cascade_refs: [<root failure>]
  judge_calibration_ref: <optional>
```

## 9. Recommended End-to-End Workflow

### Phase A: source intake

Collect real normative text from diverse repositories, preserve provenance and
license, and label generalization versus calibration. Do not decide release
eligibility at extraction time.

### Phase B: atomicization and review

Split bundled paragraphs, normalize without strengthening modality, deduplicate
semantic equivalents, and attach an initial opportunity/verifier hypothesis.
Use LLMs for proposals; use deterministic checks and human review for
promotion.

### Phase C: task profiling

Pin a task population independently, clean the model-visible objective, map
work units and behavior paths, and write witnesses and shortcut audits before
looking at intervention outcomes.

### Phase D: parent-Item assembly

Create zero-injection/intervention pairs. Start with L0/L1 combinations,
reject incoherent products, then add dependency, cross-file, persistence, and
counter-default factors one at a time.

### Phase E: static qualification

Run provenance, opportunity, coverage, dependency, anti-shortcut, and leakage
checks. Items that lack a must-scored opportunity remain calibration or
plumbing candidates.

### Phase F: pilot calibration

Use a small, fixed model and replication matrix. Include aligned controls,
against-prior rules, independent combinations, dependency chains, and at least
one multi-facet verifier. Estimate exposure, task success, rule pass rates,
joint success, verifier failures, and model discrimination.

### Phase G: release and holdout

Freeze the qualified definitions and provenance before using pilot outcomes to
select a final panel. Keep a semantic/repository holdout, report selection
rules and exclusions, and publish uncertainty and unresolved candidates rather
than silently dropping them.

## 10. Implications for the Current HIF Repository

The current Phase 0 source intake contains 39 raw units, 44 provisional
candidates, and 45 draft canonical records from project and contributor
documents. The task area contains a source-pinned 20-task SWE-bench Multilingual
candidate panel and Item pairs. These are useful inputs, but none should be
called a hard benchmark rule or released challenging Item solely because it
has a real source or a `difficulty=hard` upstream label.

The next data-curation step should be a review ledger that adds, for a bounded
subset:

- rule modality and prior hypothesis;
- a concrete opportunity witness for each task;
- affected behavior paths and dependency depth;
- deterministic/semantic verifier plan;
- anti-shortcut cases;
- expected baseline/intervention comparison;
- calibration versus release status.

Then construct a few parent ladders using the same task fixtures. The first
pilot should answer which factors actually create a measurable compliance gap
before the project expands the full rule/task combination space. Existing
source and task records should remain intact while these qualification fields
are reviewed; qualification is a new layer, not a reason to rewrite provenance.

## 11. Risks and Explicit Non-Claims

- **Contamination:** a rule's public wording or repository may have appeared in
  training. A source pointer cannot establish non-contamination; use semantic
  holdouts and report the limitation.
- **Prior-label dependence:** zero-injection probes can overlap evaluated
  models or vendors. Preserve cohort overlap and sensitivity analyses.
- **Selection optimism:** choosing Items after observing model separation
  inflates apparent difficulty. Freeze the selection protocol and protect a
  holdout.
- **Reward hacking:** hidden tests may miss test-only edits, stale dependencies,
  copied implementations, or superficial migrations. Use independent audits
  and adversarial checks.
- **Opportunity confounding:** no trigger or missing artifact is not a model
  failure. Track it explicitly and repair the Item.
- **Judge instability:** a single LLM judge is not ground truth. Retain votes,
  calibrate, and avoid narrow model rankings when agreement is weak.
- **Task/rule confounding:** a difficult base task can hide a rule effect, while
  an easy task can make every rule look solved. Report task and rule outcomes
  separately and use parent Items.
- **Process-rule mismatch:** review, commit, identity, and communication rules
  need simulated events. Do not score them in a plain coding task with no such
  event.

This document therefore makes no claim that the current 20-task panel or Phase
0 rule library is already sufficiently difficult. It defines the evidence that
must be collected before making that claim.

## References

The primary literature links are listed inline above. For the source excerpts,
the repository/license references reviewed on 2026-08-29 were:

- Linux kernel: <https://raw.githubusercontent.com/torvalds/linux/master/COPYING>
- LLVM: <https://raw.githubusercontent.com/llvm/llvm-project/main/LICENSE.TXT>
- PyTorch: <https://raw.githubusercontent.com/pytorch/pytorch/main/LICENSE>
- CPython/devguide: <https://raw.githubusercontent.com/python/devguide/261dc2116ca81985c5c0cfc59db5a251d2c8db96/LICENSE>
  (CC0 1.0 Universal; this is distinct from CPython's license.)
- Rust: <https://raw.githubusercontent.com/rust-lang/rust/master/LICENSE-APACHE>
  and <https://raw.githubusercontent.com/rust-lang/rust/master/LICENSE-MIT>
- PostgreSQL wiki: <https://wiki.postgresql.org/wiki/PostgreSQL_wiki:Copyrights>
  (PostgreSQL License; the wiki page's policy is distinct from the source
  repository's `COPYRIGHT` file.)

The current HIF source intake and task records remain the authoritative local
provenance for the first collection batch:

- [`docs/source-shortlist.md`](source-shortlist.md)
- [`benchmark/sources/phase0-source-manifest.yaml`](../benchmark/sources/phase0-source-manifest.yaml)
- [`benchmark/sources/phase0-raw-units.yaml`](../benchmark/sources/phase0-raw-units.yaml)
- [`docs/task-sourcing.md`](task-sourcing.md)
