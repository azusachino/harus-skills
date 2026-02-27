# Memory Conventions Design

Date: 2026-02-28

## Problem

The session skill's global memory tier only vaguely mentioned `save_memory` and `~/.agents/`. Agents had two recurring failures:

1. Claiming they lacked permission to read/write `~/.agents/` and stopping rather than continuing without it.
2. Not knowing which backend to use when multiple options were available, leading to inconsistent behavior across Claude Code and other agents.

## Goal

Add unified memory management conventions to `session/SKILL.md` that:

- Teach agents to detect what memory tools are available and use them in a consistent write order.
- Explain Claude Code's native memory system (`save_memory` + auto-loaded MEMORY.md) as the preferred global tier.
- Remain fully functional for agents without native memory tools (filesystem-only fallback).
- Provide concrete guidance on what to write, what not to write, and how to format entries.

## Design

### Section 1: Memory Backend Support

A capability table showing which backends are available in which agents, and what each is used for. Includes an explicit note about Claude Code's auto-load behavior (zero read-token cost).

### Section 2: Memory Writing Protocol

A single ordered write protocol at session end:

1. `save_memory` (if available) — global facts, zero read cost next session
2. `.agents/MEMORY.md` (always) — project-scoped decisions, universal
3. `~/.agents/` (if accessible) — mirror of global facts for filesystem-only agents

Plus conventions for:

- **What to write**: decisions with rationale, user preferences, non-obvious patterns, things that went wrong.
- **What NOT to write**: active task state, content already in AGENTS.md/CONTEXT.md, large code blocks, ephemeral observations.
- **Entry format**: short, factual, future-agent-readable. Update in place rather than duplicating.

## Trade-offs Considered

- **Separate per-agent sections** — more explicit but longer and harder to maintain. Rejected in favor of a unified write-order that agents follow regardless of environment.
- **Detect agent type explicitly** — fragile, agents can't reliably self-identify. The capability table plus graceful skip-on-fail is more robust.
