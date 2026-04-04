---
name: session
description: Use when starting or ending a work session, when a project has a .agents/ directory at the start of a conversation, or when user says "start session", "let's continue", "wrap up", or "end session" — restores prior context and saves session state
metadata:
  author: haru
  version: 1.9.0
---

# Session Skill

Manage memory and session state across agents and conversations.

**Core principle**: MCP `@modelcontextprotocol/server-memory` is the canonical store for session state and global facts when available. Local `.agents/` files are fallback only — except `CONTEXT.md`, which is always read and updated.

## Auto-Trigger

Run `/session start` automatically when `.agents/` exists in the project root, or when the user says "start session", "let's continue", "resume".

Run `/session end` when the user says "wrap up", "end session", "save context", "I'm done".

## `/session start`

**Step 1 — Detect MCP**: check if `search_nodes`, `create_entities`, `add_observations` are all in the available tool list. Record this — do not re-check.

**Step 2 — Load global memory**:

- If MCP: use `search_nodes` or `open_nodes` for targeted retrieval of category entities (`UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard`), the project entity (cwd basename, lowercased, hyphens), and the session entity `[project-name]:session`. Avoid `read_graph()` for large projects.
- If no MCP: try `save_memory` tool for preferences; fall back silently.

**Step 3 — Load project context** (always, regardless of MCP):

- Read `AGENTS.md` and `.agents/CONTEXT.md`. Skip silently if missing.
- If context-mode is active (hooks present), use `ctx_search` to query indexed docs rather than reading full files.

**Step 4 — Session state** (MCP fallback only):

- If MCP unavailable: read `.agents/CURRENT_TASK.md`.
- If MCP available: skip `CURRENT_TASK.md` entirely — session state comes from `[project]:session` entity.

**Step 5 — Doc freshness check**:

- Run `git log --oneline -5` to see recent commits.
- If commits touch feature files but `AGENTS.md` or `CONTEXT.md` were not updated, flag it: "Docs may be stale — consider syncing after this session."

**Step 6 — Report**: "Session resumed. Last task: [X]. Next: [Y]." Note any stale docs.

## `/session end`

**Step 1 — Sync session state**:

- If MCP: delete `[project-name]:session`, recreate with:
  - `objective`, `status` (IN_PROGRESS | BLOCKED | REVIEW | DONE), `completed`, `remaining`, `next`, `last-updated`
- If no MCP: overwrite `.agents/CURRENT_TASK.md` with the same fields.

**Step 2 — Sync global facts**:

- If MCP: for each new cross-project fact — `search_nodes` to deduplicate, then `add_observations` on the appropriate category entity. For project decisions, add to the project entity.
- If no MCP: append to `.agents/MEMORY.md` (format: `## YYYY-MM-DD — [topic]` / `**Fact:** ...` / `**Why it matters:** ...`). Update in place if a similar entry exists.

**Step 3 — Sync docs**:

- Update `.agents/CONTEXT.md` if any core behavior, architecture pattern, or non-obvious convention changed this session. Keep it concise — remove stale entries.
- Update `AGENTS.md` if project structure, commands, or tech stack changed.
- If docs grew significantly this session, trim redundant or outdated sections.

**Step 4 — Confirm**: "Session saved. Next: [one-sentence handoff]."

## Context-Mode Integration

If context-mode is installed (check for `ctx_search`, `ctx_batch_execute` in tools or hooks present):

- At session start, prefer `ctx_batch_execute` to load memory + run `git log` in one call rather than sequential reads.
- Use `ctx_search` for targeted retrieval from large `CONTEXT.md` or `MEMORY.md` instead of reading full files.
- Raw file reads still apply for files you intend to edit (e.g., before updating `CONTEXT.md`).

## MCP Entity Conventions

**Session entity** — `[project-name]:session`: volatile, deleted and recreated each session end.

**Category entities**: `UserPreferences`, `CodingStyle`, `ToolPreferences`, `Standard` — cross-project user facts.

**Project entity** — repo basename: stable project conventions (e.g. "Uses nix devShell", "Task runner is make").

Deduplication: always `search_nodes` before adding observations.

## Fallback: Local Files

Used only when MCP is unavailable:

- `.agents/CURRENT_TASK.md` — task state (overwrite each session end)
- `.agents/MEMORY.md` — decision log (append only; update in place for duplicates)

Both files should be in `.gitignore` — they are session-volatile and should not pollute git history.

## Core Principles

- **MCP as Truth**: session state lives in MCP only. No local writes for task state when MCP is active.
- **CONTEXT.md is living**: always read; update and trim at session end when things change.
- **Doc sync**: flag and fix stale docs at session boundaries — don't let documentation drift.
- **Graceful degradation**: fall back to local files silently if MCP is not configured.
