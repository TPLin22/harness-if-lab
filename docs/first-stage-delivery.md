# First-Stage Delivery Contract

**Status:** implemented smoke path, 2026-08-28

This document records the first executable delivery path. It is an
implementation contract for the current StepCLI/Harbor adapter, not the final
Item or schema specification.

## Scope

The current path supports one semantic Item variant with these two surfaces:

- `user_message`: an additional user-channel instruction fragment;
- `project_file`: a project instruction file discovered by StepCLI.

The semantic Item remains backend-neutral. The concrete filenames, Harbor keys,
and container paths below belong to the StepCLI adapter and Harbor compiler.
Other surfaces are rejected by default until an adapter is implemented for
them. The external StepCLI runtime/package publisher is an input to a future
live run and is outside this repository.

## Data flow

```text
Item pair + rule library + TaskSpec
              |
              v
    StepCliDeliveryAdapter
              |
              +--> delivery/manifest.json
              +--> delivery/user_messages/<binding>.md
              +--> delivery/project_files/<binding>.md
              |
              v
       HarborPackCompiler
              |
              +--> dataset/<task>/instruction.md
              +--> dataset/<task>/environment/.claude/rules/hif-<binding>.md
              +--> launch.yaml
              +--> pack.json
              |
              v
       Harbor agent-stage trial
              |
              v
       StepCLI startup discovery
```

The Pack and all runtime state are written below the caller-provided external
`output_root`. The source repository is never used as a runtime workspace.

## Surface mapping

| Semantic surface | Generated source | Harbor transport | StepCLI effective expectation |
| --- | --- | --- | --- |
| `user_message` | `delivery/user_messages/<binding>.md` | `extra_instruction_paths` | Content is appended to Harbor's task/user instruction channel before the agent starts. It is intentionally not claimed to be an independent system surface. |
| `project_file` | `delivery/project_files/<binding>.md` | agent-stage `upload_files`; source is relative to task `environment/` | `/testbed/.claude/rules/hif-<binding>.md`, discovered as `source=project`, `format=rule`, `activation=startup`. |

The compiler copies each project file into the generated task's
`environment/.claude/rules/` directory. Harbor's `upload_files` hook then
uploads that relative source to the declared absolute container target. The
hook runs at the agent stage, after the environment starts and before StepCLI
runs; a missing source is a trial failure.

`delivery_order` controls the deterministic order of all binding records and
user fragments. It is not authority or precedence. Orders must be positive,
unique integers within an Item. Authority remains an explicit Item policy.

## Manifest and provenance

`delivery/manifest.json` is the handoff between semantic compilation and
execution. For every binding it records, at minimum:

- the rule and binding IDs, role, and intended surface;
- actual surface and delivery status (`planned` for the two supported surfaces,
  `unsupported_surface` otherwise);
- transport, Pack-relative path, target path, delivery order, and content hash;
- Item, TaskSpec, rule-library, adapter, and task-instruction provenance.

The Harbor compiler rewrites the manifest after adding the generated task
environment path for project files. `pack.json` additionally hashes the source
Item, rule library, TaskSpec, manifest, and launch configuration.

## Reproduce the smoke Pack

From the repository root, use the Harbor virtual environment (it supplies the
YAML and test dependencies):

```sh
/home/i-panhaoran/codingspace/harbor/.venv/bin/python \
  -m compilers.harbor.compiler \
  --item examples/smoke/item-pair.yaml \
  --rules benchmark/rules/canonical/phase0-canonical.yaml \
  --task-spec examples/smoke/task-spec.yaml \
  --task-dir examples/smoke/task \
  --output-root /tmp/hif-smoke-output \
  --model openai/REPLACE_ME
```

The compiler refuses to overwrite an existing Pack. Use a new output directory
for each attempt. The generated `launch.yaml` can be passed to Harbor after
the model, runtime artifact, and environment settings have been filled in.

## Verification completed

The following checks are part of the first-stage gate:

```sh
/home/i-panhaoran/codingspace/harbor/.venv/bin/ruff check \
  hif harnesses compilers tests/test_delivery.py
/home/i-panhaoran/codingspace/harbor/.venv/bin/python -m pytest -q \
  tests/test_delivery.py
```

The tests cover separate user/project bindings, baseline omission, unsupported
surface rejection, explicit delivery ordering, duplicate-order rejection, and
Harbor launch/hook materialization. A separate static probe also validates the
generated `launch.yaml` with Harbor's `JobConfig`, validates the generated task,
and runs the current StepCLI `config show --workspace ... --json` against the
generated `.claude/rules` file.

This environment does not have Docker, so no live container or model trial is
claimed by this milestone. A real run additionally needs a pinned StepCLI
runtime from the separate publisher workflow, Harbor credentials/configuration,
and an external output root.

## Deliberate limits

- `system_prompt`, `managed_instruction`, `global_instruction`,
  `tool_description`, and `skill` bindings remain unsupported in this adapter.
- No StepCLI or Harbor source files are modified by this path.
- No effective-surface snapshot is captured from a live StepCLI process yet;
  the manifest is the intended delivery plan, while the pre-model discovery
  probe is the next runtime adapter responsibility.
- Ambient instructions from the process home and task workspace must be checked
  before a scored run. The current smoke fixture is clean; this is not yet a
  general isolation policy for external benchmark tasks.
- Verifiers, trial artifact collection, and cross-run analysis remain future
  phases.

The next implementation boundary is a runner/preflight layer that consumes this
Pack, records the effective StepCLI instruction snapshot and native events, and
then invokes deterministic verification. Only a demonstrated interface gap in
that layer should trigger a change to Harbor or StepCLI.
