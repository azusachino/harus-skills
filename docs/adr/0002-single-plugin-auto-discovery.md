# 2. Single plugin, skills auto-discovered

- Status: Accepted
- Date: 2026-07-12

## Context

The marketplace could expose each skill as its own installable plugin (granular, per-skill install control) or bundle every skill into one plugin. `marketplace.json` also supports listing skills explicitly or letting them be discovered from a directory.

## Decision

Ship a single `harus-skills` plugin. Skills are auto-discovered from the flat `skills/` directory — each skill is one subdirectory with a `SKILL.md`, and no skill is listed explicitly in `marketplace.json`. Adding a skill is just adding a directory.

## Consequences

- Simplest possible config: one plugin entry, one place to look, and adding or removing a skill needs no manifest edit.
- One universal version to bump per release (see ADR 0003) rather than per-skill plugin versions.
- The trade-off: consumers install the whole set, all-or-nothing — there is no per-skill install control. Acceptable because the set is small and curated for one user's workflow.
