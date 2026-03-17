# init-project v0.8.0 — `.claude/` Infrastructure Generation

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `init-project` to scaffold a full `.claude/` directory with `rules/`, `agents/`, and `commands/` stubs, based on real-world patterns from popular Claude Code projects.

**Architecture:** Add a new `configs/claude-infra.md` template file containing all `.claude/` file templates. Update `SKILL.md` to (1) ask one new Phase 2 question about config/release processes, (2) generate `.claude/` structure in Phase 3, and (3) reflect the new outputs in the Phase 6 summary. Bump versions in all three manifest locations.

**Tech Stack:** Markdown only. Verification via `make check` (fmt + lint + verify).

---

## File Map

| Action | File | Purpose |
|---|---|---|
| Create | `skills/init-project/configs/claude-infra.md` | Templates for all `.claude/` files |
| Modify | `skills/init-project/CONFIGS.md` | Add reference to `claude-infra.md` |
| Modify | `skills/init-project/SKILL.md` | Phase 2 question + Phase 3 generation + Phase 6 summary + version bump 0.7.0 → 0.8.0 |
| Modify | `gemini-extension.json` | Version bump 1.4.0 → 1.5.0 |
| Modify | `.claude-plugin/marketplace.json` | Version bump 1.4.0 → 1.5.0 |

---

## Task 1: Create `configs/claude-infra.md`

**Files:**
- Create: `skills/init-project/configs/claude-infra.md`

- [ ] **Step 1: Write the template file**

Create `skills/init-project/configs/claude-infra.md` with this exact content:

```markdown
# Claude Infrastructure Templates

Templates for `.claude/` directory generation. Used by `init-project` Phase 3.

---

## CLAUDE.md

Root-level project instructions for Claude Code. Keep concise — detailed conventions go in `.claude/rules/`.

```markdown
# CLAUDE.md

## Project

[One-sentence description of the project.]

## Commands

\`\`\`bash
make fmt          # Format all files
make lint         # Lint checks
make check        # fmt + lint + verify
make test         # Run tests (if applicable)
\`\`\`

## Rules

- See `.claude/rules/core.md` for agent DO/DON'T rules
[- See `.claude/rules/config.md` for config management rules  # include if config/release detected]
[- See `.claude/rules/release.md` for release process rules   # include if release process detected]

## Key Files

[List 3–5 important entry points from the scan]
\`\`\`
```

---

## `.claude/rules/core.md`

Hard DO/DON'T rules for all agents working in this project. Always generated.

```markdown
## Agent Rules — Core

### DO
- Use `make <target>` for all task execution — never run tools directly
- At session start: load MCP entities if available (`search_nodes` in tools); skip `CURRENT_TASK.md` when MCP active
- At session end: write state to `[project]:session` MCP entity
- Dispatch sub-agents for independent tasks — parallelize where possible
- Update `.agents/CONTEXT.md` when architecture or conventions change
- Bump `metadata.version` in skill + manifests after any skill edit
- Stage files explicitly: `git add <specific files>` only

### DON'T
- Commit without user confirmation
- Use `git add -A` or `git add .`
- Install tools globally — use nix devShell or `make <target>` instead
- Lint or format `.md` files (markdown linting is disabled)
- Use plan mode for small, well-scoped tasks — only for complex multi-step features
```

---

## `.claude/rules/config.md`

Generated only when config management is detected or confirmed by user.

```markdown
## Agent Rules — Config Management

### DO
- Validate config schema before applying changes
- Create a rollback snapshot before any migration: `cp config.yaml config.yaml.bak`
- Test config changes in a dry-run or staging environment first
- Document every config key change in the commit message

### DON'T
- Apply config changes directly to production without a staged rollback plan
- Remove config keys without checking all consumers
- Commit secrets or credentials in config files
```

---

## `.claude/rules/release.md`

Generated only when a release process is detected or confirmed by user.

```markdown
## Agent Rules — Release

### DO
- Run `make check` (or equivalent) before any release commit
- Tag releases using semantic versioning: `vMAJOR.MINOR.PATCH`
- Update changelog or release notes before tagging
- Verify smoke tests pass against the release artifact

### DON'T
- Push directly to `main`/`master` — use a PR
- Skip CI checks with `--no-verify` or equivalent
- Release from a dirty working tree
```

---

## `.claude/agents/reviewer.md`

Code review agent. Always generated.

```markdown
---
description: Reviews code changes for correctness, style, and potential issues. Invoke after completing a feature or before opening a PR.
---

You are a thorough code reviewer for this project. When reviewing:

1. Check correctness — does the logic do what it claims?
2. Check style — does it follow `.claude/rules/core.md` conventions?
3. Check tests — are edge cases covered?
4. Check for security issues — injection, credential exposure, unsafe operations
5. Check for over-engineering — flag unnecessary complexity

Output: a concise list of issues grouped as MUST FIX / NICE TO HAVE / PRAISE. Be direct.
```

---

## `.claude/agents/explorer.md`

Codebase exploration agent. Always generated.

```markdown
---
description: Maps unfamiliar areas of the codebase. Use when you need to understand how a module works, trace a data flow, or find where a behavior is implemented.
---

You are a codebase explorer. When given a question about this project:

1. Use Glob and Grep to locate relevant files — don't guess paths
2. Read only what's needed — don't dump entire files
3. Trace call chains from entry points downward
4. Summarize findings as: entry point → key files → notable patterns → answer

Output: a concise map with file paths and line numbers. No speculation — only what the code shows.
```

---

## `.claude/commands/help.md`

Help slash command stub. Offered optionally.

```markdown
---
description: Show available commands and agent capabilities for this project.
---

List all available slash commands in `.claude/commands/` and agents in `.claude/agents/`, with a one-line description of each. Then show the key `make` targets from the Makefile.
```
```

- [ ] **Step 2: Verify the file exists and is well-formed**

```bash
ls skills/init-project/configs/
```

Expected: `claude-infra.md` appears alongside other config files.

---

## Task 2: Update `CONFIGS.md`

**Files:**
- Modify: `skills/init-project/CONFIGS.md`

- [ ] **Step 1: Add reference to `claude-infra.md`**

Append this line to the "Always read first" section:

```markdown
- `configs/claude-infra.md` - `.claude/` directory templates (rules, agents, commands, CLAUDE.md)
```

- [ ] **Step 2: Verify**

Read the file and confirm the new line appears under "Always read first".

---

## Task 3: Update `SKILL.md` — Phase 2 question

**Files:**
- Modify: `skills/init-project/SKILL.md` (Phase 2 section)

- [ ] **Step 1: Add question 6 to Phase 2**

After question 5 ("Prefer Nix + Makefile for tooling?"), add:

```markdown
6. "Does this project have config management (env files, secrets, migrations) or a release process (tagging, changelogs, CI gates)?" — if yes, generate `rules/config.md` and/or `rules/release.md` in Phase 3.
```

- [ ] **Step 2: Verify**

Read Phase 2 and confirm the question is present and numbered correctly.

---

## Task 4: Update `SKILL.md` — Phase 3 `.claude/` generation

**Files:**
- Modify: `skills/init-project/SKILL.md` (Phase 3 section)

- [ ] **Step 1: Add `.claude/` generation block**

After the `### .agents/MEMORY.md (fallback only)` section and before `### .gitignore additions`, add a new section:

```markdown
### `.claude/` directory

Load `configs/claude-infra.md` for all templates below. Ask permission once for the whole group before writing.

#### CLAUDE.md (root)

Generate if not already present. Populate from scan:
- Project description from README or detected purpose
- Key `make` targets from Makefile
- Rule file references (always `core.md`; add `config.md`/`release.md` if those were confirmed in Phase 2)
- Key files / entry points from scan

Never overwrite an existing CLAUDE.md — offer to merge instead.

#### `.claude/rules/core.md`

Always generate. Contains hard DO/DON'T rules for all agents. Use the template from `configs/claude-infra.md`, adapting the tool provisioning section to the detected stack (nix/mise/other).

#### `.claude/rules/config.md`

Generate only if user confirmed config management in Phase 2.

#### `.claude/rules/release.md`

Generate only if user confirmed a release process in Phase 2.

#### `.claude/agents/reviewer.md` and `.claude/agents/explorer.md`

Always generate both. Use templates from `configs/claude-infra.md` verbatim — they are generic enough to apply to any project.

#### `.claude/commands/help.md`

Offer optionally: "Want a `/help` slash command stub?" Generate if accepted.

#### `.claude/settings.json`

Already handled above (MCP config). No change needed here.
```

- [ ] **Step 2: Verify Phase 3 reads coherently**

Read Phase 3 end-to-end and confirm:
- No duplicate sections
- `.claude/` block appears between `.agents/MEMORY.md` and `.gitignore additions`
- All conditionals (config.md, release.md, help.md) are clearly marked

---

## Task 5: Update `SKILL.md` — Phase 6 summary + version bump

**Files:**
- Modify: `skills/init-project/SKILL.md` (Phase 6 + frontmatter)

- [ ] **Step 1: Update the Phase 6 output listing**

Replace the existing `Init complete:` block with:

```markdown
Init complete:
  AGENTS.md, .agents/CONTEXT.md, .agents/CURRENT_TASK.md, .agents/MEMORY.md
  CLAUDE.md
  .claude/rules/core.md [+ config.md, release.md if applicable]
  .claude/agents/reviewer.md, .claude/agents/explorer.md
  .claude/commands/help.md [if accepted]
  .claude/settings.json (MCP memory)
  .gitignore (updated)
  docs/architecture.md, docs/setup.md, docs/plan.md, docs/todo.md
  Makefile, [other tooling configs]
```

- [ ] **Step 2: Bump skill version in frontmatter**

Change `version: 0.7.0` → `version: 0.8.0` in the YAML frontmatter.

- [ ] **Step 3: Verify**

Read frontmatter and Phase 6 — confirm version is `0.8.0` and the summary is accurate.

---

## Task 6: Bump manifest versions

**Files:**
- Modify: `gemini-extension.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Bump `gemini-extension.json`**

Change `"version": "1.4.0"` → `"version": "1.5.0"`.

- [ ] **Step 2: Bump `.claude-plugin/marketplace.json`**

Change `"version": "1.4.0"` → `"version": "1.5.0"`.

- [ ] **Step 3: Verify both**

```bash
grep "version" gemini-extension.json .claude-plugin/marketplace.json
```

Expected: both show `1.5.0`.

---

## Task 7: Run checks and commit

- [ ] **Step 1: Format**

```bash
make fmt
```

Expected: exits 0, formats JSON/YAML files.

- [ ] **Step 2: Run all checks**

```bash
make check
```

Expected: exits 0 — fmt-check + lint + verify all pass.

- [ ] **Step 3: Stage files explicitly**

```bash
git add skills/init-project/SKILL.md \
        skills/init-project/CONFIGS.md \
        skills/init-project/configs/claude-infra.md \
        gemini-extension.json \
        .claude-plugin/marketplace.json \
        docs/plans/2026-03-17-init-project-claude-infra.md
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(init-project): scaffold .claude/ rules, agents, commands (v0.8.0)"
```
