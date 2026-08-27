# Phase 0 Source Shortlist

**Status:** adopted shortlist; source intake has not started. Reviewed 2026-08-26.

This document records the initial source pool for rule curation. It is a source
selection decision, not a rule catalog, a formal schema, or an execution plan.
It is an internal curation record and is not the public provenance tier of a
released rule, so it may name the repositories being considered.
The files below are discovery links to the current default branches. Before an
intake record is created, resolve each branch to an immutable repository commit
and retain the source file content hash.

## Decision

Use two labeled pools in the same initial cleaning batch:

- **Generalization pool:** human-facing project, contributor, and API guidance
  that can be restated without a product or harness name.
- **Harness-native calibration pool:** real `AGENTS.md` or equivalent agent
  instructions. These are useful for testing extraction and surface rendering,
  but their results should remain separately identifiable until contamination,
  product specificity, and opportunity have been reviewed.

Both pools are eligible for cleaning. The calibration label is not a rejection
decision and does not prevent a later rule from entering a task or Item.

The target is approximately 40 raw normative units (a range of 36--47 is
expected from the quotas below). A raw unit is a bounded paragraph or bullet
before atomic decomposition; one unit may produce more than one candidate rule.
This is deliberately larger than the 10--15 candidates that Phase 0 asks us to
fully annotate. The remaining units are a reserve for finding specification
gaps, not a released benchmark.

## Generalization pool

| ID | Source and license | Target raw units | Primary signal and evidence | Main risk |
| --- | --- | ---: | --- | --- |
| G1 | [pandas `contributing_codebase.rst`](https://github.com/pandas-dev/pandas/blob/main/doc/source/development/contributing_codebase.rst) (BSD-3-Clause) | 4--5 | Optional dependencies, backward compatibility, TDD, test placement, pytest idioms; AST, test, and diff evidence | Many recommendations and exceptions; preserve modality |
| G2 | [scikit-learn `develop.rst`](https://github.com/scikit-learn/scikit-learn/blob/main/doc/developers/develop.rst) (BSD-3-Clause) | 4--5 | Naming/import rules and estimator `__init__`/`fit` contracts; AST and API tests | Python/estimator-specific scope |
| G3 | [Django `committing-code.txt`](https://github.com/django/django/blob/main/docs/internals/contributing/committing-code.txt) (BSD-3-Clause) | 3--4 | Logical commits, tests/docs after each commit, message format, force-push policy; Git/event evidence | Several rules require a commit or remote event |
| G4 | [Rust rustc-dev-guide `contributing.md`](https://github.com/rust-lang/rust/blob/main/src/doc/rustc-dev-guide/src/contributing.md) (Apache-2.0/MIT) | 3--4 | PR scope, review/rebase workflow, documentation style, CI expectations; diff/Git/event evidence | Compiler-specific process and soft recommendations |
| G5 | [Node.js `pull-requests.md`](https://github.com/nodejs/node/blob/main/doc/contributing/pull-requests.md) (MIT) | 3--4 | Lint, documentation YAML, commit messages, sign-off, and tests; AST/Git/test evidence | Some requirements only make sense in a PR workflow |
| G6 | [Kubernetes API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md) (Apache-2.0) | 3--4 | `kind`/`apiVersion`, naming, metadata, `spec`/`status`, and numeric types; schema/API evidence | Large, domain-specific document; select bounded static sections |

The generalization pool contributes 20--26 raw units. Canonical renderings must
remove repository names and paths unless the experiment explicitly tests a
product-specific rule; the original source pointer remains in private
provenance.

## Harness-native calibration pool

| ID | Source and license | Target raw units | Primary signal and evidence | Main risk |
| --- | --- | ---: | --- | --- |
| C1 | [Kubernetes `AGENTS.md`](https://github.com/kubernetes/kubernetes/blob/master/AGENTS.md) (Apache-2.0) | 3--4 | Generated-file protection, staging as source of truth, dependency/update commands, boilerplate, package naming; path/diff/command evidence | Repository-specific paths |
| C2 | [Airflow `AGENTS.md`](https://github.com/apache/airflow/blob/main/AGENTS.md) (Apache-2.0) | 4--5 | Command routing, architecture boundaries, exception/style rules, test and documentation coupling; tool-event/AST evidence | Exclude the generated command block and internal-only material |
| C3 | [Codex `AGENTS.md`](https://github.com/openai/codex/blob/main/AGENTS.md) (Apache-2.0) | 4--5 | `just` versus direct tool commands, context bounds, Rust API shape, module size, TUI conventions; event/AST/lint evidence | High target-model familiarity and contamination risk; do not use alone for headline generalization |
| C4 | [Node.js `AGENTS.md`](https://github.com/nodejs/node/blob/main/AGENTS.md) (MIT) | 3--4 | Human oversight, no autonomous push, sign-off, AI disclosure, and test responsibility; authority/event evidence | Governance rules need an explicit actor and opportunity |
| C5 | [Rust `AGENTS.md`](https://github.com/rust-lang/rust/blob/main/AGENTS.md) (Apache-2.0/MIT) | 2--3 | Stop/reviewer gates, test-before-implementation, tool restrictions, and module-size guidance; event/diff evidence | Keep LLM policy and prohibited-text material out of the first coding sample |

The calibration pool contributes 16--21 raw units. Its rules enter the same
candidate cleaning path, but `source_pool` must remain available for later
stratification and contamination analysis.

## Snapshot evidence

The following Git blob IDs were observed for the files above on 2026-08-26.
They identify the content read during this review; they are not repository
commit IDs and do not replace the commit pin required by the eventual source
manifest.

```text
G1 pandas/doc/source/development/contributing_codebase.rst 0625b6cca293a0e399cbe17af14b823bdaee9111
G2 scikit-learn/doc/developers/develop.rst                3a77c3c28d96114ea53b5faf5df9936b8bed9a50
G3 django/docs/internals/contributing/committing-code.txt 2a41fe60cfe9e8552b6c5c7e19d800075538943c
G4 rust/src/doc/rustc-dev-guide/src/contributing.md       ef6c98cb6d97891e4a70b0a0ed25a26f3be18480
G5 node/doc/contributing/pull-requests.md                 77b9148213b76bf256674088b282136468fb24e8
G6 kubernetes/community/.../api-conventions.md            8ee6e2488c7040eeacdcf98d4fc3c0ed10c8243c
C1 kubernetes/AGENTS.md                                   5fd40c37ce365414e213c3dfd99914232040261b
C2 airflow/AGENTS.md                                      c414057ac1fef074f2c0fea9a700b7d69a8afe0b
C3 openai/codex/AGENTS.md                                 faa57cc0db48123e1011f1eb47692cd3bbbcfc3a
C4 node/AGENTS.md                                         79e1d1b688b811edf4722720137e3b402f7c5bd0
C5 rust/AGENTS.md                                         af1ad378bebddcadc8bde50ce54f9ccdba5a8c3a
```

## Intake rules

The first intake pass should retain, conceptually, the following metadata. This
is a checklist for the later contract review, not a formal schema:

- repository, immutable commit, path, section heading, and retrieval date;
- source kind (`human_project_guide`, `api_convention`, or
  `agent_instruction`);
- repository/organization cluster for leakage-aware splits;
- license and file-level notice where applicable;
- content hash, raw excerpt or permitted pointer, and surrounding context;
- scope hints, modality, exceptions, and the likely actor/object;
- generated-file and alias/import flags;
- extraction method and review state;
- an initial opportunity/evidence hint, without treating it as a final task
  match.

Long source snapshots stay external. A short permitted excerpt or a private
provenance pointer may be retained according to the repository's provenance and
licensing rules. `CLAUDE.md` files that only include or point to `AGENTS.md`
must be content-deduplicated; the alias can still be recorded as a separate
harness surface later.

## Phase 0 use

Use the following order after the shortlist is accepted:

1. Collect raw units from both pools without deciding yet whether they are
   release-eligible, contaminated, or task-compatible.
2. Select 12--15 units for complete candidate records. Deliberately include a
   bundled requirement, a style-only recommendation, an unclear-scope rule,
   and a rule with no obvious verifier.
3. Preserve a parent link when a bundled unit is split into multiple atomic
   candidates. Do not silently rewrite `should`, `prefer`, or exceptions into a
   hard requirement.
4. Use one or two small scenarios only to test the candidate contracts and
   opportunity vocabulary. Do not construct the Cartesian product or an Item
   release in this phase.
5. Defer baseline behavior, training-contamination judgment, and final task
   qualification until the later cleaning/qualification pass. A future
   zero-injection probe may record a conflict hypothesis; that hypothesis is
   not a property of the source text itself.

The source repository is therefore expected to contain source metadata and
candidate records after Phase 0, but no runner, Pack, live workspace, or runtime
artifact.

## Known qualification boundaries

Rules about commits, remote pushes, review waiting periods, or communication
with maintainers are useful edge cases, but they require explicit event
opportunities. If the first task cannot expose that event, retain the candidate
with an unavailable-opportunity status rather than scoring it as a model
violation.

The shortlist intentionally includes both deterministic and judge-heavy prose.
This is needed to test the current verifier contract, but results must report
the evidence type and judge uncertainty separately. Rules that mention a named
agent, internal path, or one project's command should first be treated as
product-specific or calibration material, not silently generalized.

## Deferred or reserve sources

- React's root `CONTRIBUTING.md` is currently an external link with little
  extractable content, and its root `CLAUDE.md` is too thin for the first batch.
- PyTorch's contributor and Claude files are rich but mix build instructions,
  policy, and platform-specific details; license and scope review should happen
  before intake.
- CPython's root repository points toward the separate `python/devguide`, which
  would add another source repository and licensing boundary.
- LLVM's root contributor file is primarily an entry point; a bounded coding
  standards source should be selected only after its exact path and license
  notice are verified.

These are reserves, not negative judgments about the projects. They can be
added after the first schema review exposes which source families are missing.
