# Relevant Repositories

**Status:** maintained coupling ledger (2026-08-31)

This document records changes in repositories that are coupled to a
Harness-IF Lab (HIF) implementation or run. The intended spelling is
**relevant repositories**. HIF owns the semantic benchmark data and the
backend-neutral Item contract; StepCLI and Harbor are external implementation
repositories.

## Why this ledger exists

A HIF change can require a corresponding change in an execution repository.
The two changes must remain independently reviewable, while an experiment must
still be reproducible from exact commits. Every coupled change therefore gets
an entry here with its repository, branch, commit, purpose, and run relevance.

This is a provenance record, not a vendored copy of either repository. Runtime
workspaces, generated Packs, and package build outputs remain external to HIF.

## Current repositories and checkouts

| Repository | Remote | HIF branch | Current checkout (2026-08-31) | Current commit | State |
| --- | --- | --- | --- | --- | --- |
| StepCLI | `git@gitlab.basemind.com:aiagent/step-cli.git` | `feat/hif` | `/home/i-panhaoran/codingspace/step-cli` | `2e28e1cdfa708910e0ea38ba317ca1d26a9817f8` | tracks `origin/feat/hif`; local temporary file is untracked |
| Harbor | `git@gitlab.basemind.com:code-agent/harbor.git` | `i-panhaoran/feat-hif` | `/home/i-panhaoran/codingspace/harbor-hif-toolset-20260829` | `709cde1ef8177ae789bca2b7350c8ea267e627d3` | tracks `origin/i-panhaoran/feat-hif`; clean |

The main Harbor checkout at `/home/i-panhaoran/codingspace/harbor` is on an
unrelated branch and must not be used as the HIF adapter checkout.

## Coupled commit ledger

### StepCLI

These commits form the HIF extension-surface ancestry. The first live run used
the state through `7cd03086`; the two later commits are present on the current
branch but were not part of that run.

| Commit | Change | Run status |
| --- | --- | --- |
| `e3a70bea17dff4ee37c43b37097acc4c739f290b` | Add the `dsh_minimal` extension/tool surface. | Required foundation; included in ancestry. |
| `06ecd91984add75b3df37f2c59aa973ee6ce4d4c` | Document extension-surface integration. | Documentation; included in ancestry. |
| `f1c4e1df54061dc0efaedc0f4f8739e40fc0be75` | Add tool-description surface overrides. | Included in ancestry. |
| `b6fcfbb8d0b811bd9ec75a0cc9ba70242efcd37c` | Preserve DSH tool-description overrides. | Included in ancestry. |
| `61d8d9547d72bc589098bf3ac699c489e17c0a05` | Record adapter-depth/rollout assessment. | Documentation; included in ancestry. |
| `f61c44932eb02848c349b8577498a04c4bb5ddd6` | Support additive host instructions in DSH. | Included in ancestry. |
| `7cd03086dde9b6efb66cecaf92c30fffa0ba4f7c` | Preserve the resolved DSH system prompt in the harness. | **Source commit for live runtime `v20260829.0003`.** |
| `49ef0deadf0423557f03a5eceaec1169237419e4` | Generalize replacement surfaces into a host registry. | Current branch only; not in the recorded live run. |
| `2e28e1cdfa708910e0ea38ba317ca1d26a9817f8` | Add the `pi_minimal` replacement surface. | Current branch only; not in the recorded live run. |

### Harbor

| Commit | Branch/worktree | Change | Run status |
| --- | --- | --- | --- |
| `709cde1ef8177ae789bca2b7350c8ea267e627d3` | `i-panhaoran/feat-hif` / `harbor-hif-toolset-20260829` | Forward StepCLI extension-surface configuration from the Harbor adapter. | **Harbor commit used by the live tool-surface run.** |
| `2d0e33abba2ff22b901443a83eea2d00c254b3e8` | superseded `i-panhaoran/hif-toolset-surface-20260828` / `harbor-hif-toolset` | Same adapter patch on an older `dev` base. | Historical; not the final live-run checkout. |

The separate StepCLI package/build repository is an external input. It is not
modified by HIF work; when a package is used, record its version, checksum, and
source commit in the run record as done in the first-stage delivery record.

## Update procedure

When a HIF change requires a coupled repository change:

1. Make and review the external-repository commit in its own branch/worktree.
2. Append a dated entry to the appropriate ledger above. Record the full
   commit, branch, worktree (if relevant), purpose, and whether it is included
   in a run or only staged for future work.
3. Record the HIF commit or experiment/run identifier that caused the change.
4. Pin the exact external commit in the run lock or delivery record before
   claiming reproducibility.

Do not rewrite historical entries when a branch is renamed or a newer adapter
supersedes an older one. Add a dated note instead. Changes to this ledger are
part of the same HIF documentation change and should be committed alongside
the HIF change that introduced the coupling.

## Change log

| Date | Change |
| --- | --- |
| 2026-08-31 | Renamed the StepCLI HIF branch to `feat/hif` and the Harbor HIF branch to `i-panhaoran/feat-hif`; pushed the new remote refs. The recorded live-run commits remain `7cd03086` and `709cde1ef`. |
| 2026-08-29 | Recorded the first live tool-surface run and its StepCLI/Harbor commit pins. |
