# Curation and Experiment Workflow

The project has three operational modes. Most command groups are still planned;
the first StepCLI/Harbor compile path is available as Python modules for the
smoke fixture. The boundaries below remain the intended workflow.

## Mode A: curate

```text
collect sources
  -> extract candidate rules/tasks
  -> review provenance and license
  -> canonicalize reusable assets
  -> compose candidate Items
  -> lint and qualify
  -> promote a versioned release
```

This mode primarily changes source definitions and review metadata. It may run
small qualification trials, but those trials write to an external output root.

The adopted Phase 0 source set is documented in the
[source shortlist](source-shortlist.md). Intake keeps the generalization and
harness-native calibration pools together for cleaning while retaining their
pool labels. Source selection, contamination, and task opportunity are separate
decisions: a source is not discarded merely because it is agent-specific or
cannot yet be paired with a task.

For external coding benchmarks, task intake has its own small path:

```text
pin upstream revision
  -> freeze selection index (IDs, filters, seed, reserve)
  -> write thin TaskSpec candidates
  -> resolve model-visible text and evaluator-only references
  -> review opportunity tags and eligibility
```

The first SWE-bench Multilingual pilot follows this path. It stores references
and reviewed text in `benchmark/tasks/`; it does not generate Harbor task
directories or workspaces during curation.

The current next step after task intake is candidate Item assembly. The pilot
uses one pair file per task under `benchmark/items/pairs/`: a zero-injection
baseline plus an intervention with multiple rule bindings. The assembly utility
records static opportunity intersections, binding roles, semantic surfaces,
authority metadata, and the reserved `tool_set_ref` without importing Harbor or
StepCLI. A separate StepCLI adapter test fixture now exercises the optional
`dsh_minimal` projection and abstract `tool_refs`; this does not change the
semantic pilot pairs. These pairs remain outside any released split until
verifier and surface-capability review is complete.

### Curation gates

Before an Item can enter a release, check:

- the rule is atomic and behaviorally observable;
- the task is deterministic and gives the rule an opportunity;
- the intended surface is supported by the target harness adapter;
- a verifier and evidence path exist;
- baseline/intervention behavior is meaningfully distinguishable or the Item is
  explicitly labeled non-discriminating;
- model-visible inputs do not contain evaluator secrets;
- provenance, licensing, version, and hashes are present.
- every rule binding has an explicit target surface and the target is supported
  or intentionally marked as an unsupported experiment;
- evaluator-only task data is not reachable from the model-visible workspace.

## Mode B: compile and run

```text
select released Items/Pairs
  -> freeze experiment configuration
  -> resolve TaskSpecs and evaluator cache
  -> compile backend Packs
  -> launch isolated trials
  -> capture intended/effective surfaces and native events
  -> persist external artifacts
```

The experiment lock records the selected source revision, Item hashes, model and
harness configuration, backend version, environment identity, seeds, and output
location. A Pack is immutable for the duration of the experiment.

The runner should support independent baseline and intervention trials while
keeping all unrelated variables fixed. Replicates and retries receive distinct
run identities.

The Pack compiler/materializer and the StepCLI adapter have separate jobs. The
current compiler builds the Harbor package and the current adapter maps
`user_message` and `project_file` to existing Harbor/StepCLI inputs. It also
places a resolved `dsh_minimal`/`tool_description` projection in the generated
agent kwargs; Harbor-side acceptance of that kwarg is a separately gated
integration task. A live effective-surface snapshot and the remaining surfaces
are still future work. See [the first-stage delivery contract](first-stage-delivery.md).

## Mode C: verify and analyze

```text
raw run outputs
  -> artifact completeness checks
  -> deterministic verifier execution
  -> rule/task verdicts
  -> normalized run and opportunity tables
  -> baseline/intervention pairing
  -> metrics, uncertainty, and reports
```

Verification should run as close to the trial as practical so failures are
localized. Analysis should be rerunnable later from the external artifacts and
must not mutate the benchmark source.

## Failure taxonomy

The workflow should preserve the difference between:

- a model choosing the default behavior despite a successfully delivered rule;
- a model violating a rule after seeing it;
- a rule not being delivered, loaded, or exposed as intended;
- a task, environment, or verifier failure;
- an incomplete or ambiguous observation.

Only the first two are direct model behavior outcomes. The others remain useful
diagnostic data but should not silently enter the same denominator.

## Suggested future command groups

Names are placeholders, not an API commitment:

```text
hif source ...
hif rule ...
hif task ...
hif item ...
hif pack compile ...
hif run ...
hif verify ...
hif analyze ...
```

Formal CLI and schema contracts should be designed after the first end-to-end
smoke path is agreed.
