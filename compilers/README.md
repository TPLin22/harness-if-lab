# Compilers

Compilers translate semantic benchmark definitions into backend-specific
execution inputs. The first backend is Harbor.

There are two distinct compilation boundaries:

1. An Item compiler resolves the task and rule references, validates each rule's
   role/surface assignment, and emits a canonical condition manifest.
2. The Harbor compiler/materializer turns that manifest and its `TaskSpec` into
   a complete Harbor task package under the external output root.

The current implementation is [`harbor/compiler.py`](harbor/compiler.py). It
copies a small task fixture or externally materialized task into an external
Pack, projects the cleaned TaskSpec statement into `instruction.md`, invokes
the StepCLI delivery adapter, and emits a Harbor `launch.yaml` plus provenance
metadata. It uses Harbor's existing `extra_instruction_paths` and agent-stage
`upload_files` interfaces. When an Item requests a registered StepCLI tool-set
projection, it forwards the adapter-produced `extension_surface` as an agent
kwarg; accepting and materializing that kwarg is a separate Harbor integration
boundary. The compiler does not import, modify, or package Harbor.

The Harbor compiler may resolve evaluator-only SWE-bench data from the external
task cache. It must not make Harbor's `instruction.md` or
`extra_instruction_paths` the semantic source of independent instruction
surfaces, and it must not encode StepCLI-specific config keys into Item data.
The generated files are a Pack projection and are never the canonical
benchmark representation.

Keep compilation deterministic and record the source and renderer hashes in the
generated Pack metadata. A generated Pack is an input package, not a live
workspace. The first-stage scope and verification commands are recorded in
[`docs/first-stage-delivery.md`](../docs/first-stage-delivery.md). Verifiers and
the live runner are intentionally not part of this compiler milestone.
