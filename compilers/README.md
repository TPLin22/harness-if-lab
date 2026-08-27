# Compilers

Compilers will translate semantic benchmark definitions into backend-specific
execution inputs. The first planned backend is Harbor.

There are two distinct compilation boundaries:

1. An Item compiler resolves the task and rule references, validates each rule's
   role/surface assignment, and emits a canonical condition manifest.
2. The Harbor compiler/materializer turns that manifest and its `TaskSpec` into
   a complete Harbor task package under the external output root.

The Harbor compiler may resolve evaluator-only SWE-bench data from the external
task cache. It must not make Harbor's `instruction.md` or `extra_instruction_paths`
the canonical representation of independent instruction surfaces, and it must
not encode StepCLI-specific config keys into Item data.

Keep compilation deterministic and record the source and renderer hashes in the
generated Pack metadata. A generated Pack is an input package, not a live
workspace. No compiler implementation is present yet.
