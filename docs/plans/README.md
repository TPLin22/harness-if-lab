# Plans

This directory holds execution plans: construction schedules, adopted
methodologies, migration steps, and historical stage records that describe what
someone intended to do or what an implementation checkpoint established.

It is separate from the documents in `docs/`, which describe what is true about
the project and are maintained. An `active` plan is maintained only as an
execution plan; completed or superseded plans are historical records and are
not silently rewritten.

## Convention

- One plan per file, named `YYYY-MM-DD-<slug>.md`, dated when the plan was
  written.
- YAML frontmatter with `title`, `description`, and `status`
  (`active`, `completed`, or `superseded`).
- A completed or abandoned plan, or a historical stage record, moves to
  `completed/` with its `status` updated. It is not deleted; a superseded plan
  is the record of why the current approach was chosen.

The active methodology remains at
[`2026-08-26-methodology-and-construction-plan.md`](2026-08-26-methodology-and-construction-plan.md).
The completed directory contains the historical
[first-stage delivery record](completed/2026-08-29-first-stage-delivery.md).

## Authority

A plan is subordinate to `AGENTS.md` and to the documents in `docs/`. It cannot
create or relax a boundary.

Where a plan's approach does not fit an existing boundary or document, it states
the conflict and leaves the edit to a review decision. It must not resolve the
conflict silently by writing a narrower or wider rule of its own — a plan that
quietly contradicts a durable document will be followed by someone who never
reads the document it contradicts.
