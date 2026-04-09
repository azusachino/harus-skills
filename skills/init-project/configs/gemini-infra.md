# Gemini Infrastructure Templates

Templates for `.gemini/` directory and `GEMINI.md`. Used by `init-project` Phase 3.

---

## GEMINI.md

Short project context derived from `AGENTS.md`. Keep under 80 lines — Gemini loads this on every invocation.

Add at top: `<!-- Generated from AGENTS.md — edit AGENTS.md, not this file -->`

Sections to extract from `AGENTS.md`:

- Language, runtime, version
- Task runner and key `make` targets
- Code conventions (naming, formatting, commit style)
- Key entry points / files
- Any API gotchas or upstream references

---

## `.gemini/system.md`

Executor behavior for Gemini CLI. Copy from `~/.gemini/system.md` if it exists — do not generate from scratch in that case.

If `~/.gemini/system.md` is absent, scaffold from this template:

```markdown
# System

You are a software engineering assistant working in this project.

## Workflow

- Use `make <target>` for all task execution
- At session start: run `/session start` if `.agents/` exists
- At session end: run `/session end` to save state
- Dispatch sub-agents for independent parallel tasks by default

## Rules

- Ask before committing or pushing
- Stage files explicitly: `git add <specific files>` only
- No emojis in commit messages or responses
- Simple solutions over clever ones — no speculative abstractions
- Skip `CURRENT_TASK.md` and `.agents/CONTEXT.md` when MCP memory is active
```

---

## `.gemini/settings.json`

MCP server config for Gemini CLI. Same `mcpServers` structure as `.mcp.json`. Only include project-specific servers the user selected in Phase 2 — omit any already configured globally.

```json
{
  "mcpServers": {}
}
```

Note: inform the user whether this file is gitignored by default in Gemini CLI — if so, teammates will not receive it automatically.
