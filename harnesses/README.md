# Harness Adapters

Adapters connect a backend Pack to a real agent harness. StepCLI is the first
target; Pi and Codex are future targets.

The `harnesses/stepcli` directory is the current ownership boundary. It may
later be developed or vendored as a companion repository, but the semantic
contracts in this repository remain unchanged either way.

An adapter owns the mapping from an Item's backend-neutral surface declaration
to actual harness inputs. For StepCLI this may eventually include system-prompt
configuration, project instruction files, user-message delivery, tool
descriptions, and skills. The mapping is adapter code, not an Item field and not
the Harbor Pack compiler's responsibility.

Each rule binding must remain independently traceable. The adapter records the
intended target, actual delivery target/content hash, effective surface after
discovery and precedence, and a delivery status (including an unintended
surface merge). It must not hide unsupported surfaces by silently concatenating
them into one prompt.

The adapter also exposes a capability boundary for the optional Item-level
`tool_set_ref`. A future implementation may replace a complete tool registry,
schema/presentation, implementation, and permission policy; the current
scaffold only reserves the reference and requires unsupported capabilities to be
reported.
