# Plans

This directory holds execution plans: construction schedules, adopted
methodologies, migration steps, and other documents that describe what someone
intends to do.

It is separate from the documents in `docs/`, which describe what is true about
the project and are maintained. A plan is superseded rather than maintained.

## Convention

- One plan per file, named `YYYY-MM-DD-<slug>.md`, dated when the plan was
  written.
- YAML frontmatter with `title`, `description`, and `status`
  (`active`, `completed`, or `superseded`).
- A completed or abandoned plan moves to `completed/` with its `status` updated.
  It is not deleted; a superseded plan is the record of why the current approach
  was chosen.

## Authority

A plan is subordinate to `AGENTS.md` and to the documents in `docs/`. It cannot
create or relax a boundary.

Where a plan's approach does not fit an existing boundary or document, it states
the conflict and leaves the edit to a review decision. It must not resolve the
conflict silently by writing a narrower or wider rule of its own — a plan that
quietly contradicts a durable document will be followed by someone who never
reads the document it contradicts.
