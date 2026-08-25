# Curation and Experiment Workflow

The project has three operational modes. The scaffold does not implement their
commands yet; the boundaries below are the intended workflow.

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

## Mode B: compile and run

```text
select released Items/Pairs
  -> freeze experiment configuration
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
