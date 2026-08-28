# User-message + project-file smoke

This fixture is intentionally tiny and is not a benchmark release.  It checks
that one Item can deliver two independent rule bindings through the first
implemented StepCLI surfaces:

- `user_message` becomes a Harbor `extra_instruction_paths` fragment;
- `project_file` becomes a per-binding `.claude/rules/*.md` file uploaded by an
  agent-stage `upload_files` hook.

Compile an external Pack from the repository root:

```sh
python3 -m compilers.harbor.compiler \
  --item examples/smoke/item-pair.yaml \
  --rules benchmark/rules/canonical/phase0-canonical.yaml \
  --task-spec examples/smoke/task-spec.yaml \
  --task-dir examples/smoke/task \
  --output-root /tmp/hif-smoke-output \
  --model openai/REPLACE_ME
```

The command writes `launch.yaml`, `delivery/manifest.json`, and a copied task
under the external output root.  It never writes a Pack into this repository.
Edit the generated model/runtime settings before launching Harbor.  For a real
StepCLI run, supply the runtime artifact/configuration available in the
separate StepCLI publisher workflow; this fixture does not build binaries.

## Tool-set projection smoke

[`tool-surface-item-pair.yaml`](tool-surface-item-pair.yaml) keeps the same
task but requests the backend-neutral `tool_set_ref: dsh_minimal` and adds one
`tool_description` binding targeting the abstract `shell` role. The StepCLI
adapter resolves that role to `bash` and writes an `append` description
override under `agents[0].kwargs.stepcli_extension_surface` in the generated
launch config. This fixture verifies HIF-side compilation; Harbor support for
that agent kwarg is deliberately a later integration change.
