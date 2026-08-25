# Project Constraints

This document records constraints for the first version of Harness-IF Lab. It
is a design contract, not a formal data schema.

## Research scope

- Measure rule following inside an agent harness, not generic instruction
  following in a chat-only setting.
- Treat learned defaults and preferred coding patterns as the comparison point.
- Start with single-agent StepCLI runs.
- Keep sub-agent orchestration and communication as a later, separately labeled
  track.
- Avoid treating a higher raw accuracy number as sufficient evidence of a
  stronger harness-following capability.

## Repository boundary

- Git stores source definitions, documentation, future code, small fixtures, and
  reviewed benchmark metadata.
- Git does not store live workspaces, generated Packs, model transcripts, raw
  Harbor job directories, or experiment reports.
- A repository-local output directory is considered accidental and is ignored by
  default; callers must configure an external `output_root`.
- Large task snapshots and source archives are external, license-aware, and
  pinned by immutable revision or checksum.

## Rule constraints

- A canonical rule should describe one observable behavioral constraint.
- Scope, exceptions, authority, and expected evidence must be explicit before a
  rule is released.
- A rule must be renderable on a declared surface without changing its meaning.
- Product or harness names are excluded from generalization rules unless the
  item is explicitly product-specific.
- Raw source text, extraction provenance, review state, and licensing metadata
  must be retained where permitted.
- LLM extraction or rewriting is advisory; it cannot silently promote a rule to
  the released set.

## Task constraints

- A task should have a neutral coding objective so that the rule is the intended
  behavioral intervention.
- Initial state, dependencies, resource limits, and success evidence must be
  reproducible.
- The task must expose a meaningful opportunity to observe the target rule.
- Task fixtures may be synthetic and small in the first phase. Larger codebases
  are referenced externally rather than duplicated in every Item.
- Hidden oracle material must be inaccessible to the model-visible workspace.

## Item and pairing constraints

- An Item binds reusable rule/task assets and a surface/policy plan; it should
  not duplicate their full contents unnecessarily.
- Every intervention that claims a behavioral effect should have a matched
  baseline or a documented reason why pairing is impossible.
- The baseline and intervention must keep unrelated variables fixed as far as
  possible.
- An Item is not valid merely because its YAML or JSON parses. It also needs a
  verifier, an observable opportunity, and a supported rendering target.
- Exploratory combinations may be ephemeral. Released Items need stable IDs,
  version metadata, and content hashes.

## Surface and harness constraints

- The research model must distinguish system, managed/global instruction,
  project instruction, user message, tool description, skill, and future
  surfaces where they are experimentally relevant.
- Intended surface and effective surface are separate records.
- A backend limitation must be reported as unsupported or as a delivery failure;
  it must not be hidden by concatenating all inputs into one prompt.
- StepCLI is the first adapter. Pi and Codex must not force premature changes to
  the canonical data model.
- Harness version, commit, runtime configuration, loaded instruction files,
  truncation/import behavior, and effective tool/prompt surface must be captured.

## Execution and isolation constraints

- Each trial runs in an isolated, freshly materialized workspace.
- Packs are inputs and are immutable after a run references their hash.
- Model credentials and private evaluator data must not be written into public
  manifests or model-visible files.
- Raw native harness events are retained when possible; normalized trajectories
  are derived views.
- Retries and replications have distinct identities and must never overwrite
  one another.

## Verification and analysis constraints

- Prefer code-, test-, diff-, and event-based verification.
- Use an LLM judge only where deterministic evidence is insufficient, and record
  judge model, prompt, input evidence, and uncertainty.
- Separate `rule_satisfied`, `rule_violated`, `delivery_failure`,
  `task_failure`, `infrastructure_failure`, and `inconclusive` outcomes.
- Verification is local to a trial; analysis consumes verdicts across trials.
- Analysis must report baseline/intervention pairing and denominator choices,
  including behavior-diff and opportunity-conditioned subsets.
- A failed or incomplete artifact must be visible as missing/incomplete data, not
  silently counted as a model error.

## Reproducibility constraints

Every released run should be reconstructable from a lock manifest containing,
as applicable:

- repository and benchmark revision;
- rule, task, Item, and Pack hashes;
- model/provider and generation parameters;
- harness and adapter version/commit;
- runtime image and dependency digests;
- seed, replicate, retry, and timeout information;
- verifier and analysis versions;
- external artifact locations.

## Change discipline

- Formal schemas are introduced only after the conceptual contracts are
  reviewed.
- New surfaces, verdict classes, or output locations require a design-document
  update.
- Do not copy or reset unrelated changes in neighboring repositories.
- Keep the first implementation small enough to audit end to end with a
  synthetic micro-repository.
