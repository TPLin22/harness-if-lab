# Harness Adapters

Adapters connect a backend Pack to a real agent harness. StepCLI is the first
target; Pi and Codex are future targets.

The `harnesses/stepcli` directory is the current ownership boundary. The first
adapter implementation is [`stepcli/adapter.py`](stepcli/adapter.py); it may
later be expanded or replaced by a companion implementation, but the semantic
contracts in this repository remain unchanged either way.

An adapter owns the mapping from an Item's backend-neutral surface declaration
to actual harness inputs. For StepCLI this includes the first-stage project
instruction file and user-message delivery; system-prompt configuration, tool
descriptions, and skills remain future surfaces. The mapping is adapter code,
not an Item field and not the Harbor Pack compiler's responsibility.

Each rule binding must remain independently traceable. The current adapter
records the intended target, the concrete transport/path, content hash, and a
planned or unsupported status. A future runtime phase will add the effective
surface after discovery and precedence, including truncation or an unintended
surface merge. Unsupported surfaces are rejected by default; they are not
silently concatenated into one prompt.

For the current two-surface path, `user_message` is delivered through Harbor's
existing user instruction channel and `project_file` is materialized as a
`.claude/rules/*.md` file before StepCLI startup. See the
[first-stage delivery contract](../docs/first-stage-delivery.md) for the exact
mapping and preflight expectations.

The adapter also exposes a capability boundary for the optional Item-level
`tool_set_ref`. A future implementation may replace a complete tool registry,
schema/presentation, implementation, and permission policy; the current
scaffold only reserves the reference and requires unsupported capabilities to be
reported.
