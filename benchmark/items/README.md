# Item And Pair Candidates

An Item is an experimental condition that joins one thin TaskSpec to one or
more canonical rule references. This directory stores the first candidate
representation for that join. It is semantic input for a future compiler; it is
not a prompt, a StepCLI configuration, a Harbor task directory, or a runtime
workspace.

## Current pilot

The pilot contains 20 files under
[`pairs/swebench-multilingual/`](pairs/swebench-multilingual/), indexed by
[`indexes/swebench-multilingual-pilot-20.yaml`](indexes/swebench-multilingual-pilot-20.yaml).
Each file is an `hif.item_pair` record with:

- one `task_ref` and its TaskSpec content hash;
- a zero-injection `baseline` Item;
- an `intervention` Item with two to four independently bound rules;
- one `role`, semantic `target_surface`, authority class, and opportunity match
  per binding, plus a deterministic delivery order (which is not authority
  precedence);
- an explicit no-conflict authority policy and `tool_set_ref: null`;
- qualification and provenance metadata, including the task review flags.

The pair review ledger is
[`indexes/swebench-multilingual-pilot-20-review.yaml`](indexes/swebench-multilingual-pilot-20-review.yaml).
All 20 pairs pass structural composition checks and remain candidates. No pair
is a released benchmark item: verifier implementations, surface capability,
prior labels, interference checks, and the release floor are still pending.

## Why a pair file

The baseline and intervention are kept together so their shared task, policy,
tool-set factor, and provenance cannot drift. The baseline omits every rule
binding; the intervention differs only by the declared bindings. This is a
zero-injection baseline for aggregate comparison. It does not support a
single-rule causal claim when several rules are injected together; such claims
need a controlled one-rule or factorial design later.

Roles are deliberately separate from run-time verdicts:

| Role | Meaning in this candidate panel |
| --- | --- |
| `scored` | Eligible for the primary denominator after an opportunity and verifier pass |
| `observed` | Record a possible behavior, but exclude from the primary denominator for now |
| `distractor` | Fixed instruction load, intentionally not scored |

The semantic surface vocabulary is the backend-neutral set used by the design:
`system_prompt`, `managed_instruction`, `global_instruction`, `project_file`,
`user_message`, `tool_description`, and `skill`. A target surface says what the
experiment intends to vary. It does not name a StepCLI filename, CLI option, or
prompt concatenation strategy. The StepCLI adapter owns that mapping later and
must report the effective surface separately.

`tool_set_ref` is reserved at the pair level so a future condition can replace a
complete tool registry, implementation, presentation, and permission policy.
It is null in this pilot and must remain backend-neutral until that contract is
implemented.

## Candidate assembly

The deterministic assembly utility is
[`generators/assemble_swebench_pilot.py`](generators/assemble_swebench_pilot.py).
It reads the task panel and canonical rule draft, checks file hashes, computes
static opportunity intersections, and writes pair files plus the two indexes.

The opportunity hints used here are evaluator-derived curation metadata only;
they are not model-visible and do not prove that a behavior will occur in a
future run. Final qualification must audit the task statement and the actual
trial evidence separately.

```sh
python3 benchmark/items/generators/assemble_swebench_pilot.py \
  --root . \
  --output-dir benchmark/items \
  --overwrite
```

The utility uses only checked-in semantic metadata. It does not import Harbor or
StepCLI, materialize a repository, resolve hidden tests, or write packs/logs.
`--overwrite` is intentionally explicit because it replaces generated candidate
files.

The current assignment is conservative: `rule-canon-p0-027` is the primary
scored rule because every selected task has the static `behavior_change` and
`test_authoring` hints. Rust match rules can be scored when their exact hint is
present; comment and Rust API rules remain observed because they need judge or
additional verifier work. A style-check rule is used as a fixed distractor when
no second opportunity rule is available. These are curation proposals, not
claims that a future run will produce those events.

## Qualification gate

Before promotion to a released split, reviewers must rerun the static lint and
then resolve, at minimum:

1. whether each task really creates the claimed observable opportunity;
2. whether suggested solutions, workarounds, and issue-template residue should
   be removed from the model-visible statement;
3. whether the assigned surface is supported and remains distinct in the target
   harness;
4. whether a deterministic verifier can produce evidence for every `scored`
   binding, with an LLM judge documented as a fallback;
5. whether at least one `must`-severity scored rule is present, or an explicit
   reviewed exception replaces that floor;
6. whether baseline and intervention differ only in the intended factor and
   have a reproducible pair identity.

No step in this candidate assembly requires changing Harbor or StepCLI. Their
adaptation begins only when a future compiler and harness adapter are built.
