# Implementation Handoff: First Vertical Slice

**Status:** temporary construction plan, written 2026-08-26.

This document lets a new developer begin implementation without treating the
early scaffold as a frozen benchmark specification. It resolves only the
decisions necessary for the first end-to-end slice. Replace its temporary
decisions with reviewed contracts once the slice has established which data and
runtime facts must be represented.

Read [AGENTS.md](../AGENTS.md), [the overall design](design.md), and [the
constraints](constraints.md) before making changes. This handoff is the
implementation entry point for the initial single-agent StepCLI track.

## 1. The Direct Answer

The existing documents explain the research goal, entity boundaries, and output
ownership well. They intentionally leave several implementation decisions open:
the first supported surface, the first end-to-end deliverable, the exact Harbor
integration boundary, developer environment, and acceptance gates. That is the
right state for a design scaffold, but it is not enough for an unfamiliar
developer to start construction without making research-significant choices.

For the first vertical slice, make the following working decisions:

| Topic | Working decision | Reason |
| --- | --- | --- |
| Control plane | Build the Lab control plane as a Python 3.12+ package managed with `uv`. | Harbor is a Python project; compiling Packs, launching trials, and reading Harbor artifacts are orchestration work. StepCLI remains an external runtime. |
| Execution backend | Use Harbor, not a new container runner. | It already provides isolated tasks, environments, tests, job lifecycle, and a StepCLI installed-agent adapter. |
| Harness target | StepCLI only. | StepCLI is the controlled harness in the first research phase. |
| First tested surface | A root project instruction file, `AGENTS.md`, in the agent workspace. | It is a real StepCLI-supported surface and can be made visible independently from the user task message. |
| Task delivery | Harbor `instruction.md` supplies only the task/user instruction. | Do not emulate a project rule by appending it to Harbor's instruction string. |
| Rule delivery | The H1 intervention materializes the target rule in `/testbed/AGENTS.md`; H0 has no target rule there. | This makes the physical delivery mechanism observable and keeps the single intended intervention clear. |
| First verifier | A deterministic repository/test/diff verifier. | The first slice must establish trustworthy evidence before adding LLM judging. |
| Runtime data | Use a required external `HIF_OUTPUT_ROOT`. | Packs, workspaces, native logs, and reports are not source assets. |

These are implementation decisions for the first slice, not a claim that
`AGENTS.md` is the only meaningful harness surface or that Harbor is the final
runner.

## 2. First Deliverable

Deliver one reproducible paired smoke experiment:

```text
one synthetic micro-repository
  x one neutral coding task
  x one observable project-instruction rule
  x H0/H1 paired conditions
  x one StepCLI model/harness configuration
  x one deterministic verifier
  -> one external experiment directory with inspectable evidence
```

H0 and H1 use the same fixture, task prompt, model configuration, Harbor
configuration, execution limits, and verifier. The intended difference is only
the target project instruction. The first task and rule are development
fixtures, not a released benchmark item and not a substitute for the later
source-curation process.

The development task must allow task success through more than one observable
implementation path: H0 and H1 should both be able to satisfy the neutral task,
while the rule verifier can distinguish the requested constrained behavior from
the default-compatible alternative. A task whose ordinary correctness tests
already force the rule's behavior is not an instruction-following measurement.

The first slice is complete only when a reviewer can inspect the output and
answer all of these questions without reading model prose:

1. Which task and target rule were selected?
2. What exact project instruction was intended for H1?
3. Did StepCLI discover that file before its first model call?
4. What user/task instruction did Harbor give the agent?
5. What changed in the workspace, and did the task succeed?
6. Did the rule pass, fail, or fail to be delivered?
7. Which model, harness build, Harbor build, Pack, seed, and replicate produced
   the result?

## 3. Why This Slice Uses a Project Instruction

The current local implementations make this the narrowest faithful starting
point.

StepCLI discovers project instruction entrypoints in its workspace, including
`CLAUDE.md`, `.claude/CLAUDE.md`, and `AGENTS.md`, and records discovered
instruction-file metadata. It also discovers managed and global instruction
files, expands imports, and enforces a total instruction-file budget. See the
following StepCLI implementation references:

- `src/bootstrap/prompt/instruction-files.ts`
- `src/runtime/runtime-config.ts`
- `src/commands/config-command.ts`

In the current implementation, `step config show --workspace /testbed --json`
exposes the resolved `instructionFiles` list without making a model request.
Use it as the initial effective-surface probe, but invoke it with the same
StepCLI entrypoint, workspace, explicit config path, and non-secret runtime
environment that the subsequent agent run will use.

By contrast, Harbor's task model supplies an `instruction.md`, and its
`extra_instruction_paths` mechanism appends file content to that same
instruction text. Its current StepCLI agent `run()` method receives a single
instruction string. See:

- `harbor/src/harbor/models/task/task.py`
- `harbor/src/harbor/agents/installed/stepcli.py`

Therefore, **do not use `extra_instruction_paths` to represent a project,
system, tool, or user surface in the first slice.** It would make the experiment
look multi-surface while actually testing a flattened prompt.

StepCLI's project-file loader is still eventually assembled into the harness
prompt. That is acceptable here because the experiment claims a project-file
delivery mechanism and proves that mechanism with the effective-surface probe.
It must not be described as a test of an independently controllable provider
system-message API.

## 4. Scope and Non-Goals

### In scope

- A small Python package and developer tooling in this repository.
- A temporary development fixture and paired H0/H1 construction path.
- Compilation from a semantic internal representation into a Harbor task Pack.
- Harbor execution through its existing StepCLI installed-agent adapter.
- Pre-run capture of the intended and effective project-instruction surface.
- External run artifacts, one deterministic verifier, and minimal paired-result
  normalization.
- Unit tests plus one guarded integration/smoke path.

### Explicitly out of scope

- A final `RuleSpec`, `TaskSpec`, `Item`, `Pack`, `Run`, or `Verdict` schema.
- A released rule corpus, task corpus, dataset split, or LLM-assisted curation
  pipeline.
- System-prompt, tool-description, skill, managed/global instruction, and
  authority-conflict experiments.
- Pi, Codex, or any other harness adapter.
- Multi-agent execution, sub-agent communication, or orchestration metrics.
- LLM judging as the primary verifier.
- A custom container runner, distributed scheduling, web UI, or artifact store.
- Copying the Harbor or StepCLI source trees into this repository.

## 5. Ownership and Repository Boundaries

```text
harness-if-lab                         Harbor                         StepCLI
-------------------------------        -------------------------      -------------------------
semantic benchmark intent              task/environment isolation     instruction discovery
paired experiment selection            job and trial lifecycle        prompt/surface resolution
Pack compilation                       StepCLI process execution      agent loop and tools
artifact normalization                 native Harbor logs             native session events
deterministic verifier                 test execution                 config inspection
cross-run analysis
```

The Lab owns the research semantics and the experiment evidence model. Harbor
owns the execution backend. StepCLI owns actual harness behavior. Do not copy
Harbor's task model into canonical benchmark data, and do not reimplement
StepCLI instruction loading in the Lab.

The current sibling `harbor` and `step-cli` worktrees are development trees,
not release pins. Before a real experiment, record the exact commits and any
required patches in the experiment lock. Do not treat source observations in
this document as a permanent compatibility guarantee.

## 6. Construction Order

Build in this order. Do not start broad rule/task collection before the first
slice proves that the data can be delivered and measured faithfully.

### Milestone 0: establish the local developer baseline

Add the minimal Python project tooling in this repository:

- `pyproject.toml` with Python 3.12+ and `uv` usage;
- a small importable package under `src/`;
- a `hif` CLI entry point or equivalent developer command group;
- formatting, linting, type checking, and unit-test commands;
- a required `HIF_OUTPUT_ROOT` configuration value;
- a guard that rejects an output root inside the source repository.

Do not create a final public CLI surface or a general plugin system. The first
commands only need to support a smoke compile, smoke run, verify, and inspect
path.

### Milestone 1: prove the surface before calling a model

Create a non-model surface probe that materializes a tiny fixture in a fresh
Harbor-compatible workspace and then runs the equivalent of:

```text
<same-step-entrypoint> config show \
  --workspace /testbed \
  [--config <same-explicit-config>] \
  --json
```

The capture must inherit the same non-secret environment and configuration
layers as the later StepCLI agent invocation. The only permitted omission is a
credential that config inspection does not need. Record the capture command and
its configuration provenance with the result.

The probe must prove all of the following:

- `/testbed/AGENTS.md` is the intended project instruction entrypoint for H1;
- no fixture `CLAUDE.md` or `.claude/CLAUDE.md` takes precedence over it;
- there are no imports or path-scoped rules in the first slice;
- the target file is within a conservative size budget, well below StepCLI's
  current aggregate instruction-file limit;
- the process has a fresh, experiment-controlled `HOME` and explicit config
  state, so a global `~/.codex/AGENTS.md`, `~/.step-cli/AGENTS.md`, or
  `~/.claude/CLAUDE.md` cannot become an unrecorded confounder;
- the effective inspection records the expected project file and no unexpected
  instruction source.

Keep the rendered development rule small and do not use imports. A future
surface experiment may deliberately study discovery order, imports, or
truncation, but the first slice must exclude them.

If the probe cannot establish the file was loaded, classify the condition as
`delivery_failure` and do not run it as a scientific H1 trial.

### Milestone 2: compile an external Harbor Pack

Implement the smallest Pack compiler under `compilers/harbor/`. Its output is
external and disposable. It should materialize:

- the neutral task/user prompt as Harbor `instruction.md`;
- a reproducible synthetic fixture/environment whose agent workspace is
  `/testbed`;
- H1's project instruction at `/testbed/AGENTS.md`, or H0's absence of the
  target instruction;
- a deterministic test/verifier entry point;
- a public, non-secret intent record for the runner;
- evaluator-only material outside the model-readable workspace;
- enough provenance to relate the generated directory back to the source
  revision and selected development assets.

The compiler must be deterministic: repeated compilation from the same input
and version should yield the same logical Pack hash. A Pack is never the
canonical research Item and is never checked into Git.

### Milestone 3: run with Harbor and capture evidence

Use Harbor's StepCLI installed-agent path. Set the StepCLI workspace explicitly
to `/testbed`; do not rely on a dataset-specific default. Keep Harbor's task
instruction and the project instruction physically separate.

Each condition and replicate needs a fresh workspace, clean experiment home,
fresh StepCLI storage/session state, and a separately materialized Pack. Never
start H1 from an H0 workspace, reuse a prior agent session, or let a previous
trial's generated instruction files survive into the next trial.

The existing Harbor adapter already captures useful native files, including the
task prompt copy, pre-run runtime metadata, a StepCLI native storage directory,
and an events JSONL file. The first integration should preserve those files and
add a pre-first-model-call effective-surface probe.

The preferred implementation is a small, explicit, opt-in Harbor StepCLI
adapter extension that:

1. receives a public Lab manifest or capture request;
2. captures config inspection after workspace materialization and before the
   agent invocation, using the same StepCLI entrypoint, workspace, config path,
   and non-secret environment as the agent;
3. stores the capture with the other agent logs; and
4. leaves ordinary Harbor StepCLI runs unchanged.

Keep this patch isolated and tested in the Harbor repository. Record its commit
or patch identity in the Lab experiment lock. Do not hide this requirement in a
shell string or make the Lab scrape unversioned temporary files after the fact.

If the existing adapter cannot expose a pre-run capture safely, stop and make
that adapter capability explicit before reporting model results. Do not replace
the missing evidence with an assumption that the intended file was loaded.

### Milestone 4: normalize a single trial

The Lab writes a normalized, research-owned artifact under the external output
root. File names are provisional, but a reviewer must find equivalent evidence
to this layout:

```text
<output_root>/<experiment_id>/artifacts/<run_id>/
├── run-manifest.json
├── surface/
│   ├── intended-surface.json
│   └── effective-surface.json
├── trace/
│   ├── task-prompt.txt
│   ├── stepcli-runtime-pre.json
│   └── stepcli-events.jsonl
├── workspace/
│   ├── before-manifest.json
│   ├── after-manifest.json
│   └── diff.patch
└── verifier/
    ├── task-verdict.json
    └── rule-verdict.json
```

Use references or links to Harbor's raw job directory when that avoids
duplicating large logs. The normalized artifact is evidence required by the
research, not a wholesale copy of every Harbor workspace snapshot.

At minimum, `run-manifest` carries identifiers/hashes for the selected pair,
condition, Pack, task fixture, rule rendering, model/provider settings, Harbor
revision, StepCLI revision/runtime bundle, environment, seed, replicate, and
retry. These are information requirements, not yet a serialized schema.

### Milestone 5: verify and compare H0/H1

Implement a deterministic verifier that evaluates the actual final workspace
and declared test output. It must emit a separate task result and rule result.

For the first slice, use only these result classes:

```text
rule_satisfied
rule_violated
delivery_failure
task_failure
infrastructure_failure
inconclusive
```

The analysis code should ingest one H0/H1 pair and report the two conditions
side by side, including whether the H1 effective-surface probe succeeded. It
does not need population statistics yet. The important invariant is that it
never folds delivery or infrastructure failures into a rule-violation score.

### Milestone 6: make the slice hard to regress

Add tests for:

- output-root rejection when it points at the source checkout;
- deterministic Pack compilation and Pack hash stability;
- H0/H1 invariants: same task/user prompt/fixture/verifier, only the target
  project instruction differs;
- fixture linting that rejects conflicting instruction entrypoints and imports;
- public/private material separation;
- artifact completeness and provenance checks;
- verdict denominator behavior for every result class;
- one guarded integration test that exercises the real surface probe and,
  where credentials and a sandbox are available, one real StepCLI trial.

## 7. Required Evidence and Failure Handling

An intent record says what the compiler tried to deliver. An effective-surface
record says what StepCLI actually resolved. These are distinct artifacts.

Use this decision table during implementation and review:

| Observation | Classification | Scoring treatment |
| --- | --- | --- |
| H1 `AGENTS.md` is not listed by the pre-run probe | `delivery_failure` | Exclude from rule-following denominator; investigate compiler/adapter/environment. |
| An unexpected global or managed instruction is listed | `delivery_failure` or invalid experiment setup | Do not compare with clean conditions until isolation is restored. |
| The task environment or agent process fails before evidence exists | `infrastructure_failure` | Preserve logs; do not call it model noncompliance. |
| Task cannot complete, but the rule evidence is still valid | `task_failure` plus the independently supported rule verdict | Report both; do not infer one from the other. |
| The task succeeds and deterministic evidence supports the requested behavior | `rule_satisfied` | Include in paired analysis. |
| The task succeeds and deterministic evidence contradicts the requested behavior | `rule_violated` | Include in paired analysis. |
| Evidence cannot distinguish outcomes | `inconclusive` | Retain and report separately. |

Never infer rule satisfaction from the model's final text alone. Never infer a
model violation merely because an instruction was absent, truncated, shadowed,
or delivered through the wrong surface.

## 8. Compatibility Checks Before Any Real Run

Before using a model budget, run and record a compatibility check against the
specific Harbor and StepCLI revisions planned for the experiment:

1. Harbor can build and execute the generated task Pack.
2. The agent's working directory is `/testbed` and contains the expected
   fixture and H1 project instruction.
3. StepCLI's config inspection sees only the expected instruction file sources.
4. Harbor keeps the pre-run capture, prompt copy, runtime metadata, and native
   events in a retrievable job output.
5. The verifier receives an untouched evaluator-side test/oracle path.
6. The artifact normalizer can reproduce a complete run record without reading
   the source checkout or model credentials.

The current StepCLI source supports `step config show --workspace ... --json`
and project instruction discovery. The current Harbor StepCLI adapter captures
native event data. Both are implementation observations, not versionless
promises; re-run this checklist when either dependency changes.

## 9. Decisions a Developer Must Not Make Alone

Pause for a design review rather than silently selecting any of the following:

- the permanent authored format or field-level schema for Rules, Tasks, Items,
  Packs, Runs, or Verdicts;
- a new canonical surface vocabulary or authority/precedence semantics;
- a rule family, source license policy, or released benchmark split;
- an LLM judge, score threshold, or qualification criterion used in reporting;
- changing the scientific scope from project instruction to system/user/tool or
  multi-agent behavior;
- a direct StepCLI core change rather than an adapter-level solution;
- a custom runner that replaces Harbor for the initial phase;
- an artifact retention policy that loses required provenance or raw evidence.

Escalate immediately if a first-slice requirement cannot be met without
flattening surfaces, exposing evaluator data, or treating delivery failure as
model behavior.

## 10. Handoff Checklist

The developer taking this work should be able to mark these in order:

- [ ] Read `AGENTS.md`, `docs/design.md`, `docs/constraints.md`, and this file.
- [ ] Set up the Python/`uv` development baseline and external output-root guard.
- [ ] Build a no-model project-instruction surface probe.
- [ ] Confirm the Harbor Pack places the fixture and `AGENTS.md` in `/testbed`.
- [ ] Add the isolated, opt-in Harbor pre-run evidence capture if needed.
- [ ] Compile and execute one H0/H1 development pair through StepCLI.
- [ ] Produce complete external artifacts and deterministic verdicts.
- [ ] Write the minimal paired comparison and regression tests.
- [ ] Review the observed artifacts with the research owner before designing
      permanent schemas or curating real rules/tasks.

## 11. What Comes Next

After the slice is accepted, use the observed manifests and artifact needs to
design the actual contracts. The expected next review order is:

```text
Rule + Rendering
  -> Task + Fixture
  -> Item + Pair
  -> Pack
  -> Run + Verdict
  -> Experiment lock and analysis tables
```

Only then expand to additional project-instruction rules, other surfaces, larger
fixtures, stronger qualification runs, Pi/Codex adapters, or multi-agent tracks.
