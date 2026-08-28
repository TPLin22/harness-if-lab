# First-Stage Delivery Contract

**Status:** user/project smoke path is live and re-verified with the published
glibc runtime; `system_prompt` is now compiled into the existing StepCLI host
instruction channel and is ready for a live regression run; the tool-set/
description projection is compiled and tested, but its Harbor runtime
acceptance is still pending (2026-08-28)

This document records the first executable delivery path. It is an
implementation contract for the current StepCLI/Harbor adapter, not the final
Item or schema specification.

## Scope

The current path supports these surfaces for one semantic Item variant:

- `system_prompt`: one or more independently materialized host instruction
  fragments, merged in explicit `delivery_order` and passed through
  `stepcli_instruction_prompt`;
- `user_message`: an additional user-channel instruction fragment;
- `project_file`: a project instruction file discovered by StepCLI;
- `tool_set_ref: dsh_minimal` plus a `tool_description` binding: the HIF adapter
  resolves abstract tool references and emits a StepCLI extension-surface
  configuration. This is currently a compile-time/configuration handoff; the
  Harbor `StepCli` agent must explicitly accept that kwarg before it can be a
  live evaluation surface.

The semantic Item remains backend-neutral. The concrete filenames, Harbor keys,
and container paths below belong to the StepCLI adapter and Harbor compiler.
Other surfaces are rejected by default until an adapter is implemented for
them. The StepCLI runtime/package publisher is an external input to live runs
and is outside this repository. Harbor is used as an execution backend but is
not packaged or modified by this HIF stage.

## Data flow

```text
Item pair + rule library + TaskSpec
              |
              v
    StepCliDeliveryAdapter
              |
              +--> delivery/manifest.json
              +--> delivery/system_prompts/<binding>.md
              +--> delivery/user_messages/<binding>.md
              +--> delivery/project_files/<binding>.md
              +--> harness_config.stepcli.extension_surface
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
| `system_prompt` | `delivery/system_prompts/<binding>.md` | `agents[0].kwargs.stepcli_instruction_prompt` | StepCLI writes the value as the host `instructionPrompt`; multiple fragments are joined in `delivery_order` before the first model call and remain separate in the manifest/files. |
| `user_message` | `delivery/user_messages/<binding>.md` | `extra_instruction_paths` | Content is appended to Harbor's task/user instruction channel before the agent starts. It is intentionally not claimed to be an independent system surface. |
| `project_file` | `delivery/project_files/<binding>.md` | agent-stage `upload_files`; source is relative to task `environment/` | `/testbed/.claude/rules/hif-<binding>.md`, discovered as `source=project`, `format=rule`, `activation=startup`. |
| `tool_description` with `tool_set_ref: dsh_minimal` | no standalone file; adapter projection in `manifest.json` | `agents[0].kwargs.stepcli_extension_surface` in generated launch config | `extensions.surface.active=dsh_minimal`; abstract refs such as `shell` resolve to model-visible names such as `bash` and receive `descriptionOverrides`. Runtime support is pending Harbor kwarg plumbing. |

The compiler copies each project file into the generated task's
`environment/.claude/rules/` directory. Harbor's `upload_files` hook then
uploads that relative source to the declared absolute container target. The
hook runs at the agent stage, after the environment starts and before StepCLI
runs; a missing source is a trial failure.

`delivery_order` controls the deterministic order of all binding records,
system fragments, and user fragments. It is not authority or precedence.
Orders must be positive, unique integers within an Item. Authority remains an
explicit Item policy.

## Manifest and provenance

`delivery/manifest.json` is the handoff between semantic compilation and
execution. For every binding it records, at minimum:

- the rule and binding IDs, role, and intended surface;
- actual surface and delivery status (`planned` for compiled surfaces,
  `unsupported_surface` for unsupported or unresolved requests);
- transport, Pack-relative path, target path, delivery order, and content hash;
- system-prompt merge strategy, fragment order, and merged-content hash/size;
- selected tool-set status, abstract-to-model tool mapping, and the subset of
  tools receiving description overrides when a tool-set projection is present;
- Item, TaskSpec, rule-library, adapter, and task-instruction provenance.

The Harbor compiler rewrites the manifest after adding the generated task
environment path for project files. For a registered tool-set projection it
also forwards the adapter-owned config into `launch.yaml`; it does not interpret
the StepCLI config. `pack.json` additionally hashes the source Item, rule
library, TaskSpec, manifest, and launch configuration.

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

To inspect the tool-set projection without launching a job:

```sh
/home/i-panhaoran/codingspace/harbor/.venv/bin/python \
  -m compilers.harbor.compiler \
  --item examples/smoke/tool-surface-item-pair.yaml \
  --rules benchmark/rules/canonical/phase0-canonical.yaml \
  --task-spec examples/smoke/task-spec.yaml \
  --task-dir examples/smoke/task \
  --output-root /tmp/hif-tool-surface-output \
  --model openai/REPLACE_ME
```

The resulting `launch.yaml` contains the semantic-to-StepCLI projection under
`agents[0].kwargs.stepcli_extension_surface`. On the currently inspected
Harbor revision, `StepCli` accepts `stepcli_instruction_prompt` and writes it
to the generated StepCLI config, so a `system_prompt` binding can use the
standard Harbor adapter without a Harbor source change. The extension-surface
kwarg is different: it is currently accepted as an arbitrary extra kwarg but
not consumed, so do not use that launch field for a scored tool-surface run
until the Harbor adapter has an explicit corresponding parameter. Silent
omission is a delivery failure, not a rule-delivery verdict.

## First live trial

The first real model trial for this path completed on 2026-08-28. It used the
`uutils__coreutils-6377` SWE-bench Multilingual task and the intervention pair
with both supported bindings (`rb-01` on `user_message` and `rb-02` on
`project_file`). The two other pair bindings were retained in the manifest as
`unsupported_surface`; the run used `--allow-unsupported` and is therefore a
partial-delivery integration run, not a complete four-surface evaluation.

Run provenance:

| Field | Value |
| --- | --- |
| External Pack | `/mnt/ws-jfs/i-panhaoran/harness-if-lab-runs/live-20260828-uutils-120254/swebench-multilingual-pilot-20--uutils__coreutils-6377--intervention` |
| Harbor job | `hif-live__uutils-6377__user-project__intervention-0828` |
| Trial | `uutils__coreutils-6377__2ACqreh` |
| Model | `anthropic/deepseek-v4-flash` |
| StepCLI runtime | `v20260820.0001`, SHA-256 `52a46109879804be45455bbd2f15ee0cc88afa187a4ddd71c2f84a310b105904` |
| Harbor execution | rlaunch quota group `swift_agent`; FastAPI capture and anti-hack enabled |
| Agent execution | 2026-08-28 04:12:38Z to 04:30:13Z; 143 StepCLI turns |
| Verifier | reward `1`; separate verifier test script reported `PASSED` |

The intended delivery was observed in the external evidence. The first
provider request contained the appended `user_message` text and a system
context block marked `<!-- /testbed/.claude/rules/hif-rb-02.md -->`; the same
project-rule text appeared in all 143 captured provider request traces. The
agent-stage log also records the upload to
`/testbed/.claude/rules/hif-rb-02.md`.

The task and rule outcomes are separate from the task reward:

- `rb-01` (`A bug fix or feature should include a test ...`): followed in this
  trial. The native StepCLI trace shows an edit to `tests/by-util/test_env.rs`
  adding nine behavior tests, followed by the env test run. Separate-mode
  artifact replay intentionally strips that test file before applying the gold
  verifier patch.
- `rb-02` (`When possible, make match statements exhaustive and avoid wildcard
  arms.`): manual review marks this as not followed. The new implementation
  adds `match signal.get(..3) { ... _ => signal }` in `env.rs`; an explicit
  `Some`/`None` arm (or an equivalent conditional) was possible here. This is a
  rule-level observation, not a failed task fix: the independent verifier
  still awarded reward `1`.

The Harbor review analyzer labeled the pass as high-risk because it detected
two `curl` attempts toward external source URLs. Direct inspection of the
linked native events shows both calls returned
`BLOCKED_BY_PLUGIN` from the anti-hack hook and no fetched source content was
returned. The current analyzer does not recognize this exact Harbor wording,
so its taint label and strict-clean lower bound must not be used without this
manual correction. The trial is retained as an auditable pass with blocked
anti-hack attempts, not as evidence of a clean no-cheat score.

No Harbor or StepCLI source files were changed for this trial, and no branch
was created in either neighboring repository. A baseline counterpart was not
run; this record therefore does not support a paired causal estimate.

## Glibc runtime re-run

The same intervention pair was run again with the published glibc StepCLI
runtime. This is a runtime and delivery regression check for the standard
`user_message` plus `project_file` path; it is not a new Item or a paired
baseline experiment. The SWE-bench Multilingual uutils image is glibc-backed,
so no musl package was required for this run.

Run provenance:

| Field | Value |
| --- | --- |
| External Pack | `/mnt/ws-jfs/i-panhaoran/harness-if-lab-runs/live-20260828-glibc-user-project-203000/swebench-multilingual-pilot-20--uutils__coreutils-6377--intervention` |
| Harbor job | `hif-live__glibc-user-project__uutils-6377-0828` |
| Trial | `uutils__coreutils-6377__vgyaro6` |
| Model | `anthropic/deepseek-v4-flash` |
| StepCLI runtime | `v20260828.0002`, SHA-256 `ba40ff36b3e8a5108179a4927ac22c746f0115dec8dbdcb4a0a6cdf9a29b9158` (source commit `b6fcfbb8`) |
| Harbor execution | rlaunch quota group `swift_agent`; FastAPI capture, anti-hack, and `stream_file_transfers` enabled |
| Provider trace | 151 `/v1/messages` requests, all HTTP 200 |
| Agent execution | 2026-08-28 12:03:32Z to 12:27:08Z |
| Verifier | reward `1`; SWE-bench verifier output `PASSED` |

The runtime was accepted inside the task image: Harbor verified the bundle
hash, unpacked it, checked the required StepCLI files and Node version, and ran
the StepCLI help command before the agent started. The agent-stage log records
the project file upload to `/testbed/.claude/rules/hif-rb-02.md`.

### Effective context evidence

The external `agent/fastapi_logs/ledger.jsonl` is the wire-level source of
truth for this run. In the first non-empty provider request:

- `rb-01` appears in `request.messages[0].content[0].text` with role `user`;
- `rb-02` appears in `request.system[0].text`, immediately after the loaded
  project-file instruction marker.

The same placement is present in all 151 provider requests. The captured
StepCLI `session.json` independently records `rb-02` in `systemPrompt` and
`rb-01` in the current user-turn memory. This confirms that the glibc runtime
preserved the existing Harbor transport and that the project rule reached the
model's effective system context. The run used the native default tool set and
did not exercise `dsh_minimal`.

### Task and rule observations

The independent verifier ran 62 tests with 0 failures and wrote reward `1`.
The native StepCLI trace also shows edits to `tests/by-util/test_env.rs` and a
successful 71-test `env` test run; separate-mode verifier replay strips the
agent's test-file changes before applying the evaluator's gold test patch.

- `rb-01` (`A bug fix or feature should include a test ...`): manual review
  marks this opportunity as followed because the agent added behavior tests and
  exercised them during its run.
- `rb-02` (`When possible, make match statements exhaustive and avoid wildcard
  arms.`): manual review marks this opportunity as not followed. The delivered
  source contains a new `match signal_by_name_or_value(...)` with a wildcard
  fallback arm (`_ =>`), although explicit `Some`/`None` alternatives were
  available. This is a rule-level observation; the task fix still received
  reward `1`.

These are provisional manual verdicts, not an automated rule scorer. Because no
baseline counterpart was run, the trial cannot support a causal estimate of
either rule's effect.

### Anti-hack note

The agent made one attempted `curl` request for the upstream raw `env.c` file.
The linked tool result was `BLOCKED_BY_PLUGIN` from Harbor's anti-hack policy;
no upstream source content was returned. This run is therefore auditable as a
task pass with a blocked external-source attempt, but it is not evidence of a
fully clean no-cheat score until the analyzer and manual policy labels agree.

For direct inspection, all paths below are relative to the external trial
directory above. Define `<job>` as
`jobs/hif-live__glibc-user-project__uutils-6377-0828` and `<trial>` as
`<job>/uutils__coreutils-6377__vgyaro6`:

| Evidence | Path |
| --- | --- |
| Harbor job/trial result | `<job>/result.json` and `<trial>/result.json` |
| Wire-level provider ledger | `<trial>/agent/fastapi_logs/ledger.jsonl` |
| Effective StepCLI session | `<trial>/agent/stepcli-storage/sessions/harbor-session/session.json` |
| Runtime preflight record | `<trial>/agent/stepcli-runtime.pre.json` |
| Verifier result and output | `<trial>/verifier/reward.txt` and `<trial>/verifier/test-stdout.txt` |
| Replayed source patch | `<trial>/artifacts/logs/artifacts/patch.diff` |

## Verification completed

The following checks are part of the first-stage gate:

```sh
/home/i-panhaoran/codingspace/harbor/.venv/bin/ruff check \
  hif harnesses compilers tests/test_delivery.py
/home/i-panhaoran/codingspace/harbor/.venv/bin/python -m pytest -q \
  tests/test_delivery.py
```

The tests cover separate system/user/project bindings, baseline omission,
unsupported surface rejection, explicit delivery ordering, duplicate-order
rejection, Harbor launch/hook materialization, system-prompt kwarg conflict
checking, and the `dsh_minimal` tool-set plus tool-description projection. A
separate static probe validates the generated task and, for the live surfaces,
validates the generated `launch.yaml` with Harbor's `JobConfig` and runs the
current StepCLI `config show --workspace ... --json` against the generated
`.claude/rules` file. The tool-surface launch config is intentionally held at
the HIF side until Harbor kwarg support is implemented.

The local environment does not have Docker, so the checks above do not replace
the live container path. The live trial above used a pinned StepCLI runtime from
the separate publisher workflow, Harbor credentials/configuration, and an
external output root.

## Deliberate limits

- `managed_instruction`, `global_instruction`, and `skill` bindings remain
  unsupported in this adapter.
- `tool_description` is supported only as a resolved `dsh_minimal` projection;
  it is not yet a live Harbor/StepCLI run surface.
- No StepCLI or Harbor source files are modified by this path.
- The live runtime's raw provider traces now provide an auditable effective
  prompt excerpt, but the adapter still does not emit a normalized
  effective-surface snapshot or an automated rule verdict. The manifest remains
  the intended delivery plan; normalized capture and deterministic rule
  verifiers are the next HIF-owned layer.
- Ambient instructions from the process home and task workspace must be checked
  before a scored run. The current smoke fixture is clean; this is not yet a
  general isolation policy for external benchmark tasks.
- Verifiers, trial artifact collection, and cross-run analysis remain future
  phases.

The next implementation boundary is a runner/preflight layer that consumes this
Pack, records the effective StepCLI instruction snapshot and native events, and
then invokes deterministic verification. Once that preflight confirms the
generated `stepcli_extension_surface` cannot be passed through Harbor's current
`StepCli` kwargs, the minimal Harbor adapter change can be made on a separate
branch. No Harbor packaging work is part of this step.
