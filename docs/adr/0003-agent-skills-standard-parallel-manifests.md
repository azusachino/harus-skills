# 3. Agent Skills Standard with parallel agent manifests

- Status: Accepted
- Date: 2026-07-12

## Context

The same skills are used across more than one agent runtime — Claude Code, Codex, and Antigravity (gemini-compatible). Re-authoring skills per runtime would triple the maintenance and let the copies drift.

## Decision

Author every skill once to the [Agent Skills Standard](http://agentskills.io) (`SKILL.md` + YAML frontmatter), and ship parallel manifests that all point at the same `skills/` directory:

- `.claude-plugin/marketplace.json` — Claude Code marketplace
- `.codex-plugin/plugin.json` — Codex
- `gemini-extension.json` — Antigravity (compatibility)

`CLAUDE.md` is the single context file referenced by the manifests. All manifests carry one identical universal version, bumped together in the same commit as any skill change; `make validate` enforces that the versions stay aligned.

## Consequences

- One authored source of skills serves every agent; no per-runtime forks to keep in sync.
- Every release must bump the universal version in all manifests at once — a small, mechanical, checkable rule rather than a source of drift.
- Individual skills still carry their own `metadata.version` (frontmatter is the per-skill source of truth); the universal version tracks the plugin/marketplace as a whole.
