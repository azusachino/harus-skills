# Codex Infrastructure Templates

Codex CLI reads `AGENTS.md` natively — no separate config file needed for most projects.

---

## AGENTS.md Requirements for Codex

Codex executes commands from `AGENTS.md` directly. Ensure it includes:

- **Commands** section with exact runnable shell commands (not pseudocode)
- **Tech Stack** with explicit versions where relevant
- **Coding Conventions** with concrete examples
- No relative path assumptions — Codex may run from any working directory

---

## CODEX.md (monorepo only)

If the root `AGENTS.md` is too broad for a subdirectory, create a `CODEX.md` (or `AGENTS.md`) at the relevant package root. Codex prefers the nearest context file to the files it is editing.

---

## `.codex-plugin/plugin.json` (skill repos only)

Only relevant when this project is itself a Claude Code skill/plugin repository. Skip for all other project types.

Template:

```json
{
  "name": "[plugin-name]",
  "description": "[what this plugin provides]",
  "version": "1.0.0",
  "skills": "./skills"
}
```
