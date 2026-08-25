# Harness Adapters

Adapters connect a backend Pack to a real agent harness. StepCLI is the first
target; Pi and Codex are future targets.

An adapter must preserve surface identity, capture the effective surface, and
retain native harness evidence. It must not hide unsupported surfaces by
silently concatenating them.
