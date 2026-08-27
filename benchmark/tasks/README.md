# Task Assets

This directory contains thin, source-pinned task references for the Harness-IF
benchmark. It is a curation area, not a runtime task store. A task spec keeps the
neutral user-facing problem statement and enough provenance to resolve the
evaluator later; it does not copy a repository, patch, hidden tests, Docker
image, or Harbor task directory.

## Current pilot

The first panel is a 20-task, language-stratified candidate panel from the test
split of `SWE-bench/SWE-bench_Multilingual`:

- index: [`indexes/swebench-multilingual-pilot-20.yaml`](indexes/swebench-multilingual-pilot-20.yaml)
- task specs: [`specs/swebench-multilingual/`](specs/swebench-multilingual/)
- agent review: [`indexes/swebench-multilingual-pilot-20-review.yaml`](indexes/swebench-multilingual-pilot-20-review.yaml)
- collection utility: [`generators/collect_swebench_multilingual.py`](generators/collect_swebench_multilingual.py)

The panel is intentionally still `candidate_panel`. The review ledger records
deterministic checks and semantic spot checks performed by an agent; it does not
constitute final human release approval. In particular, several upstream issue
statements contain proposed fixes, workarounds, environment details, or long
diagnostic logs. Those records remain useful for pipeline bring-up but need a
release decision before entering a scored split.

## Directory roles

`indexes/` freezes panel membership, source revision, sampling, exclusions,
reserve IDs, and the content hash of every selected spec. `specs/` contains one
thin YAML record per selected upstream instance. `fixtures/` is reserved for
small synthetic repositories that are intentionally versioned with this project;
SWE-bench repositories do not belong there. `generators/` contains collection
programs and their provenance, not runtime compilers.

The selected spec's model-visible projection is explicitly
`content.problem_statement`. The `source`, `repository`, and opportunity fields
are compiler metadata. `fixture_ref` and `evaluator_ref` are evaluator-only.
The evaluator reference names the oracle fields (`patch`, `test_patch`,
`FAIL_TO_PASS`, and `PASS_TO_PASS`) without storing their values here.

## Reproducing collection

Collection needs a local parquet snapshot of the pinned dataset and an external
Harbor materialization cache. The following is an example; paths are deployment
settings and must stay outside Git:

```sh
HIF_PARQUET=/path/to/swe-bench-multilingual-test.parquet
HIF_HARBOR_TASKS=/path/to/harbor/datasets/swebench_multilingual

/path/to/harbor/.venv/bin/python \
  benchmark/tasks/generators/collect_swebench_multilingual.py \
  --parquet "$HIF_PARQUET" \
  --harbor-root "$HIF_HARBOR_TASKS" \
  --output-dir benchmark/tasks \
  --overwrite
```

The utility uses a fixed dataset revision, seed, language allocation, and
repository cap. It writes only the index and selected specs. It verifies that
the external materialization has the minimum task files needed for later
qualification, but it does not invoke Harbor or StepCLI and does not copy the
external directories. Re-running with `--overwrite` is an explicit replacement
of generated candidate records; inspect the resulting index and hashes before
committing.

## Review gate

Before a task panel is promoted, rerun the checks listed in the review ledger and
confirm all of the following:

1. Every selected ID has exactly one spec and every spec hash matches the index.
2. The dataset revision, parquet hash, row hash, repository, base commit, and
   language are complete and reproducible.
3. The allowlisted model-visible projection contains no patch, test oracle,
   generated test script, evaluator prompt, or local absolute path.
4. The cleaned statement is a neutral, readable coding objective. Suggested
   solutions and issue-template residue have an explicit keep/remove decision.
5. Opportunity tags are treated as curation hints. A tag is not evidence that a
   behavior occurred in a future run.
6. The external evaluator/materializer revision and cache key are recorded in a
   run lock when execution is eventually implemented.

Task collection ends at `TaskSpec`. Item assembly joins these records to one or
more canonical rules and assigns semantic surfaces. Mapping a surface to a
StepCLI file, prompt option, tool implementation, or Harbor package is a later
execution-phase concern.
