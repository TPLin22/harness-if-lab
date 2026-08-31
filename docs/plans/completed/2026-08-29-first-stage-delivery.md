---
title: First-stage delivery record
description: Historical record of the first StepCLI/Harbor delivery checkpoint and its live evidence.
status: completed
---

# First-Stage Delivery Record

> Historical stage record. The maintained description of the current Rule and
> Item storage format is [the data contract](../../data-contracts.md).

**Status:** user/project, additive `system_prompt`, and the registered
`dsh_minimal`/`tool_description` plumbing paths have live glibc evidence
(2026-08-29). The latest four-surface run completed delivery successfully but
did not pass the coding-task verifier. These runs are integration checkpoints,
not released or rule-scored evaluations.

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
  configuration. The Harbor feature branch used for the live plumbing run
  explicitly accepts and forwards that configuration to StepCLI. Only the
  registered `dsh_minimal` projection is covered; this is not yet a complete
  tool-set replacement contract.

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

The live tool-surface checkpoint used Harbor branch
`i-panhaoran/hif-toolset-surface-20260829` at commit
`709cde1ef8177ae789bca2b7350c8ea267e627d3`. The branch is an execution adapter
change only; Harbor packaging is outside this repository and outside the
checkpoint.

## Surface mapping

| Semantic surface | Generated source | Harbor transport | StepCLI effective expectation |
| --- | --- | --- | --- |
| `system_prompt` | `delivery/system_prompts/<binding>.md` | `agents[0].kwargs.stepcli_instruction_prompt` | StepCLI writes the value as the host `instructionPrompt`; multiple fragments are joined in `delivery_order` before the first model call and remain separate in the manifest/files. |
| `user_message` | `delivery/user_messages/<binding>.md` | `extra_instruction_paths` | Content is appended to Harbor's task/user instruction channel before the agent starts. It is intentionally not claimed to be an independent system surface. |
| `project_file` | `delivery/project_files/<binding>.md` | agent-stage `upload_files`; source is relative to task `environment/` | `/testbed/.claude/rules/hif-<binding>.md`, discovered as `source=project`, `format=rule`, `activation=startup`. |
| `tool_description` with `tool_set_ref: dsh_minimal` | no standalone file; adapter projection in `manifest.json` | `agents[0].kwargs.stepcli_extension_surface` in generated launch config; consumed by the Harbor feature branch | `extensions.surface.active=dsh_minimal`; abstract refs such as `shell` resolve to model-visible names such as `bash` and receive `descriptionOverrides` in the provider `tools` payload. |

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
`agents[0].kwargs.stepcli_extension_surface`. The base Harbor checkout accepts
unknown extra kwargs but does not consume this field. The live checkpoint used
the separate Harbor feature branch named above, where `StepCli` explicitly
forwards it into the StepCLI config. A launch produced for base Harbor must
therefore be treated as a delivery failure until its adapter branch is pinned;
silent omission is never a rule-delivery verdict.

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

## Glibc system-prompt regression run

The supported three-surface intervention pair was run with the published glibc
StepCLI runtime. This is the first live check that the HIF `system_prompt`
binding reaches the provider's `system` field while the existing
`user_message` and `project_file` paths remain intact. The skill binding was
kept in the Item manifest as `unsupported_surface`, so this remains a
partial-delivery integration run rather than a four-surface evaluation.

Run provenance:

| Field | Value |
| --- | --- |
| External Pack | `/mnt/ws-jfs/i-panhaoran/harness-if-lab-runs/live-20260828-glibc-system-v0004-2330/swebench-multilingual-pilot-20--uutils__coreutils-6377--intervention` |
| Harbor job | `hif-live__glibc-system-v0004__uutils-6377-0828` |
| Trial | `uutils__coreutils-6377__SuXuYDd` |
| Model | `anthropic/deepseek-v4-flash` |
| StepCLI runtime | `v20260828.0004`, SHA-256 `09c1890995ff71bfd51f0eab7f52452e2347a3d358b06b617c432bbf0db2434b` (source commit `f61c44932eb02848c349b8577498a04c4bb5ddd6`) |
| Harbor execution | rlaunch quota group `swift_agent`; StepFun `acs`; `stream_file_transfers`, FastAPI capture, and anti-hack enabled |
| Provider trace | 351 HTTP 200 ledger records, including 117 `anthropic_messages` requests; all 117 carried the intervention context |
| Agent execution | 2026-08-28 15:58:48Z to 16:13:26Z |
| Verifier | reward `1`; 62 tests passed, 0 failed; SWE-bench Multilingual verifier reported `PASSED` |

The earlier `v20260828.0003` glibc distribution was found to contain stale
compiled distribution output and cannot establish system-surface delivery.
The `v20260828.0004` bundle was independently hash-checked in the task image,
its required runtime files and Node version were validated, and its source
commit is recorded above. The Harbor transport itself was unchanged.

### Effective context evidence

The wire-level source of truth is
`<trial>/agent/fastapi_logs/ledger.jsonl`:

- The first provider request has one Anthropic `system` block containing the
  host instruction text from `rb-03`, followed by the project-file marker
  `<!-- /testbed/.claude/rules/hif-rb-02.md -->` and the `rb-02` text.
- The same request has `messages[0]` with the `rb-01` user fragment. The
  request payload contains the benchmark task in the same user-channel
  history, but the HIF fragment remains identifiable by its exact text and
  manifest hash.
- All 117 provider requests contain the `rb-03` text, the `rb-02` marker/text,
  and the `rb-01` text. The serialized system prompt has one stable hash across
  those requests, while the user message history grows as the agent works.
- `<trial>/agent/stepcli-storage/sessions/harbor-session/session.json`
  independently records the merged system prompt (`systemPrompt`, 12,379
  bytes), the project-file instruction, and the current user-turn memory.
- The agent-stage log records the upload to
  `/testbed/.claude/rules/hif-rb-02.md`; `stepcli-runtime.pre.json` records the
  runtime path, version, and SHA used by the process.

These observations establish delivery fidelity. They do not by themselves
establish that a rule changed behavior; that is the separate rule-level review
below.

### Task and rule observations

The independent verifier accepted the task, but the rule verdicts are manual
and provisional:

- `rb-01` (`A bug fix or feature should include a test ...`) was followed. The
  native StepCLI session records additions to `tests/by-util/test_env.rs` and
  repeated successful env test runs. Harbor's verifier replay treats
  `tests/by-util/test_env.rs` as a gold-test path, so the collected source patch
  intentionally contains only the implementation/docs files; the native trace
  is the evidence for this rule opportunity.
- `rb-02` (`When possible, make match statements exhaustive and avoid wildcard
  arms.`) was followed in the submitted implementation: the new implementation
  path does not add a wildcard match arm. This is a source review, not an
  automated semantic proof.
- `rb-03` (`Avoid boolean or ambiguous option parameters ...`) was not
  followed. The implementation introduces `ignore_all_signals: bool` and a
  boolean return component from `parse_ignore_signal_args`, where an enum or
  named state could have represented the mode more explicitly.

The task reward and these rule observations must remain separate. No baseline
counterpart was run, so this trial cannot provide a paired causal estimate.

### Anti-hack note

The anti-hack hook blocked one attempted upstream raw-GitHub fetch with
`BLOCKED_BY_PLUGIN` (`fetch_raw_github`). No upstream source content was
returned. The run is therefore auditable as a task pass with a blocked
external-source attempt, not as evidence of a clean no-cheat score.

For direct inspection, define `<job>` as
`jobs/hif-live__glibc-system-v0004__uutils-6377-0828` and `<trial>` as
`<job>/uutils__coreutils-6377__SuXuYDd` under the Pack root:

| Evidence | Path |
| --- | --- |
| Job/trial result | `<job>/result.json` and `<trial>/result.json` |
| Wire-level provider ledger | `<trial>/agent/fastapi_logs/ledger.jsonl` |
| Effective StepCLI session | `<trial>/agent/stepcli-storage/sessions/harbor-session/session.json` |
| Runtime preflight | `<trial>/agent/stepcli-runtime.pre.json` |
| Native trajectory | `<trial>/agent/trajectory.json` |
| Normalized FastAPI trajectory | `<trial>/agent/fastapi_trajectories/all.trajectory.json` |
| Verifier result | `<trial>/verifier/reward.txt` and `<trial>/verifier/test-stdout.txt` |
| Agent source patch | `<trial>/artifacts/logs/artifacts/patch.diff` |

## Glibc tool-description regression run

The three-binding tool-surface pair was run with the published glibc StepCLI
runtime and the Harbor feature branch recorded above. This is the first live
end-to-end check of the optional `dsh_minimal` projection: the HIF adapter's
abstract `shell` reference is resolved to StepCLI's `bash` tool, and the
`tool_description` text is appended to that tool's model-visible description.
The pair is a plumbing candidate, not a released benchmark condition; the
`tool_description` binding is `observed` and has no formal rule verifier yet.

Run provenance:

| Field | Value |
| --- | --- |
| External Pack | `/mnt/ws-jfs/i-panhaoran/harness-if-lab-runs/live-20260829-glibc-toolset-fixed-0003/swebench-multilingual-tool-surface-1--uutils__coreutils-6377--intervention` |
| Worker config | `<pack>/launch-worker.yaml` |
| Harbor job | `hif-live__glibc-toolset-fixed-0003__uutils-6377-0829` |
| Trial | `uutils__coreutils-6377__8U64RJZ` |
| RJob | `ws-a91dbc35128b2329-jlaunch-xx5mt` |
| Model / environment | `anthropic/deepseek-v4-flash` / StepFun `acs` |
| Quota and capture | `swift_agent`; FastAPI capture, anti-hack, and `stream_file_transfers` enabled |
| StepCLI runtime | `v20260829.0003`, SHA-256 `515cb7773dc17f7b24869e468da65241e2a0ef1f69600639939156f5b9d60c56`, source commit `7cd03086dde9b6efb66cecaf92c30fffa0ba4f7c` |
| Tool set | `dsh_minimal`; `shell -> bash`, with an append-mode description override |
| Verifier | reward `1`; SWE-bench Multilingual verifier reported `PASSED` |

The runtime preflight verified the bundle hash, unpacked the glibc runtime,
checked its required files and Node version, and wrote the resolved extension
configuration to `agent/stepcli-runtime.pre.json`. The Harbor agent-stage log
records the project-rule upload. The run completed with HTTP 200 provider
responses; no musl runtime was needed for this glibc-backed SWE-bench image.

### Effective surface evidence

The evidence has four distinct meanings and must not be collapsed into one
score:

1. **Intended delivery:** `delivery/manifest.json` and `launch-worker.yaml`
   describe the requested bindings. Manifest `status: planned` is the
   compiler's delivery plan, not a claim that the model ignored the rule.
2. **Harness transport:** the Harbor job log and `stepcli-runtime.pre.json`
   show that the project file, runtime bundle, and extension config reached the
   agent process. The Harbor feature branch commit is part of this provenance.
3. **Provider wire context:** the external
   `agent/fastapi_logs/ledger.jsonl` contains 166 provider requests; all 166
   include the project rule in `request.system`, the user rule in
   `request.messages`, and the tool-description text in `request.tools`.
   The first request shows the project marker
   `<!-- /testbed/.claude/rules/hif-rb-project-match.md -->`, the user text
   `A bug fix or feature should include a test that exercises the changed behavior.`,
   and the bash description addition
   `Add comments only to explain non-obvious reasoning; do not restate what the code already says.`.
4. **StepCLI snapshot:**
   `agent/stepcli-storage/sessions/harbor-session/session.json` records a
   276-byte project-inclusive `systemPrompt` and two model-visible tools,
   `bash` and `str_replace_editor`; the `bash` description contains the
   injected text. This independently corroborates the provider ledger.

Together these records establish delivery and effective-context fidelity. They
do not establish that the model followed a rule, nor that the intervention
caused a behavior change.

### Task and rule observations

- `rb-user-test` (`A bug fix or feature should include a test ...`) was
  provisionally judged followed: the native trace shows a behavior test added
  and the relevant tests run.
- `rb-project-match` (`When possible, make match statements exhaustive and
  avoid wildcard arms.`) was provisionally judged not followed: the submitted
  implementation contains a catch-all fallback arm. This is a rule-level
  observation, while the independent task verifier still awarded reward `1`.
- `rb-tool-comments` is an observed plumbing binding. Its delivery is proven by
  the `tools` payload, but no behavior verdict is recorded yet.

No baseline counterpart was run. These observations therefore cannot be used
for a paired causal estimate, and the task reward must remain separate from
the rule-level observations.

For direct inspection, define `<pack>` as the External Pack above, `<job>` as
`jobs/hif-live__glibc-toolset-fixed-0003__uutils-6377-0829`, and `<trial>` as
`<job>/uutils__coreutils-6377__8U64RJZ`:

| Evidence | Path |
| --- | --- |
| Worker/job configuration | `<pack>/launch-worker.yaml`, `<pack>/launch.yaml`, `<pack>/pack.json` |
| Delivery manifest and rendered inputs | `<pack>/delivery/manifest.json`, `<pack>/delivery/project_files/`, `<pack>/delivery/user_messages/` |
| Harbor job/trial result | `<job>/result.json` and `<trial>/result.json` |
| Harbor transport/preflight | `<job>/job.log`, `<trial>/agent/stepcli-runtime.pre.json`, `<trial>/agent/pre_agent_run.log` |
| Provider wire ledger | `<trial>/agent/fastapi_logs/ledger.jsonl` |
| Effective StepCLI session | `<trial>/agent/stepcli-storage/sessions/harbor-session/session.json` |
| Native and normalized trajectories | `<trial>/agent/trajectory.json`, `<trial>/agent/fastapi_trajectories/` |
| Task verifier | `<trial>/verifier/reward.txt`, `<trial>/verifier/test-stdout.txt` |
| Agent patch/artifacts | `<trial>/artifacts/logs/artifacts/patch.diff`, `<trial>/artifacts/manifest.json` |

## Glibc four-surface tool-set run

The four-binding `candidate_toolset_integration` pair was run after the
tool-description adapter was pinned. This run combines the existing
`user_message`, `project_file`, and `system_prompt` deliveries with the
registered `dsh_minimal` tool-set projection. It is a delivery/plumbing
checkpoint only: the pair has no matched baseline run, the two scored
bindings still have no automated rule verifier, and the two tool/system
bindings are observed rather than released score-bearing factors.

The SWE-bench Multilingual uutils image is glibc-backed. The published glibc
runtime was therefore sufficient; no musl runtime or musl-specific package was
needed for this trial.

Run provenance:

| Field | Value |
| --- | --- |
| External Pack | `/mnt/ws-jfs/i-panhaoran/harness-if-lab-runs/live-20260829-glibc-toolset-full-0005/swebench-multilingual-toolset-full-1--uutils__coreutils-6377--intervention` |
| Worker config | `<pack>/launch-worker.yaml` |
| Harbor job | `hif-live__glibc-toolset-full-0005__uutils-6377-0829` |
| Trial | `uutils__coreutils-6377__9pCv7BX` |
| RJob | `ws-a91dbc35128b2329-jlaunch-kd9xv` |
| Model / environment | `anthropic/deepseek-v4-flash` / StepFun `acs` |
| Quota and capture | `swift_agent`; FastAPI capture, anti-hack, and `stream_file_transfers` enabled |
| StepCLI runtime | `v20260829.0003`, SHA-256 `515cb7773dc17f7b24869e468da65241e2a0ef1f69600639939156f5b9d60c56`, source commit `7cd03086dde9b6efb66cecaf92c30fffa0ba4f7c` |
| Tool set | `dsh_minimal`; abstract `shell` resolved to model-visible `bash` |
| Harbor adapter | `i-panhaoran/hif-toolset-surface-20260829` at `709cde1ef8177ae789bca2b7350c8ea267e627d3` |
| Harbor outcome | 1 completed trial, 0 errored trials; no Harbor exception or retry |
| Verifier | reward `0`; 61 tests passed and 1 failed (`test_env::test_env_arg_ignore_signal_valid_signals`) |

### Delivery evidence

The runtime preflight record at
`<trial>/agent/stepcli-runtime.pre.json` confirms the exact runtime bundle and
SHA, the `instructionPrompt`, `extensions.surface.active: dsh_minimal`, the
`bash` append-mode description override, and the anti-hack hook. The generated
worker configuration and Harbor job log separately record the project-file
upload to `/testbed/.claude/rules/hif-rb-project-match.md`.

The wire-level ledger at `<trial>/agent/fastapi_logs/ledger.jsonl` contains 360
records: 180 `/v1/messages/count_tokens` records and 180 `/v1/messages` records.
All 360 responses returned HTTP 200. Every one of the 180 model requests
contains all four intended rule payloads in the following effective locations:

| Binding | Effective location in the provider request |
| --- | --- |
| `rb-system-api` | `request.system` (the `instructionPrompt` text) |
| `rb-user-test` | `request.messages` (the added user-channel fragment) |
| `rb-project-match` | `request.system`, after the project-file marker `<!-- /testbed/.claude/rules/hif-rb-project-match.md -->` |
| `rb-tool-comments` | `request.tools`, in the `bash` description appended with `mode: append` |

The StepCLI session at
`<trial>/agent/stepcli-storage/sessions/harbor-session/session.json`
independently records a system prompt containing the system and project rules,
the user rule in memory, and exactly two model-visible tools (`bash` and
`str_replace_editor`) with the modified `bash` description. The native session
contains 362 messages, including 150 `bash` calls and 31
`str_replace_editor` calls. These records establish transport and effective
context fidelity; they are not rule-compliance judgments.

### Task outcome and interpretation

The agent completed normally and the Harbor job has no exception, but the
separate SWE-bench verifier returned reward `0`. Its output reports 61 passing
tests and one failing test:

```text
test_env::test_env_arg_ignore_signal_valid_signals
assertion failed: target.is_alive()
```

The captured native session shows the agent editing and running tests,
including a test file that separate-mode verifier replay removes before
applying its evaluator patch. The replayed patch therefore contains only
`src/uu/env/env.md` and `src/uu/env/src/env.rs`; this is an artifact of the
verifier's gold-test isolation, not evidence that the agent never touched the
test file.

This result must be reported as two separate facts: delivery/plumbing
successful, coding-task verification failed. There was no matched baseline
trial, so it provides no causal estimate and no released rule score. The
observed rule bindings may be inspected in the native trace, but their
provisional behavior labels must not be combined with the task reward.

For direct inspection, define `<pack>` as the External Pack above, `<job>` as
`jobs/hif-live__glibc-toolset-full-0005__uutils-6377-0829`, and `<trial>` as
`<job>/uutils__coreutils-6377__9pCv7BX`:

| Evidence | Path |
| --- | --- |
| Worker/job configuration | `<pack>/launch-worker.yaml`, `<pack>/launch.yaml`, `<pack>/pack.json` |
| Delivery manifest and rendered inputs | `<pack>/delivery/manifest.json`, `<pack>/delivery/project_files/`, `<pack>/delivery/system_prompts/`, `<pack>/delivery/user_messages/` |
| Harbor job/trial result | `<job>/result.json` and `<trial>/result.json` |
| Harbor transport/preflight | `<job>/job.log`, `<trial>/agent/stepcli-runtime.pre.json`, `<trial>/agent/pre_agent_run.log` |
| Provider wire ledger | `<trial>/agent/fastapi_logs/ledger.jsonl` |
| Effective StepCLI session | `<trial>/agent/stepcli-storage/sessions/harbor-session/session.json` |
| Native and normalized trajectories | `<trial>/agent/trajectory.json`, `<trial>/agent/fastapi_trajectories/` |
| Task verifier | `<trial>/verifier/reward.txt`, `<trial>/verifier/test-stdout.txt` |
| Agent patch/artifacts | `<trial>/artifacts/logs/artifacts/patch.diff`, `<trial>/artifacts/manifest.json` |

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
`.claude/rules` file. The tool-surface live run additionally validates the
Harbor feature-branch kwarg forwarding and provider `tools` evidence.

The local environment does not have Docker, so the checks above do not replace
the live container path. The live trial above used a pinned StepCLI runtime from
the separate publisher workflow, Harbor credentials/configuration, and an
external output root.

## Deliberate limits

- `managed_instruction`, `global_instruction`, and `skill` bindings remain
  unsupported in this adapter.
- `tool_description` is supported only as a resolved `dsh_minimal` projection;
  other tool sets and complete tool-set replacement remain unsupported.
- No StepCLI or Harbor source files are modified by this path.
- The adapter still does not emit a normalized effective-surface snapshot or an
  automated rule verdict. The manifest remains the intended delivery plan;
  normalized capture and deterministic rule verifiers are the next HIF-owned
  layer.
- Ambient instructions from the process home and task workspace must be checked
  before a scored run. The current smoke fixture is clean; this is not yet a
  general isolation policy for external benchmark tasks.
- Verifiers, trial artifact collection, and cross-run analysis remain future
  phases.

The next implementation boundary is an HIF-owned runner/preflight layer that
consumes this Pack, normalizes effective surfaces and native events, and then
invokes deterministic rule/task verification. Any future Harbor change must be
made on a separately pinned branch; Harbor packaging is not part of this work.
