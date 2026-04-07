# Claude Infrastructure Templates

Templates for `.claude/` directory generation. Used by `init-project` Phase 3.

---

## CLAUDE.md

Root-level project instructions for Claude Code. Keep concise — detailed conventions go in `.claude/rules/`.

Template:

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

## `.claude/rules/core.md`

Hard DO/DON'T rules for all agents working in this project. Always generated.

Template:

```markdown
## Agent Rules — Core

### DO
- Use \`make <target>\` for all task execution — never run tools directly
- At session start: load MCP entities if available (\`search_nodes\` in tools); skip \`CURRENT_TASK.md\` when MCP active
- At session end: write state to \`[project]:session\` MCP entity
- Dispatch sub-agents for independent tasks — parallelize where possible
- Update \`.agents/CONTEXT.md\` when architecture or conventions change
- Bump \`metadata.version\` in skill + manifests after any skill edit
- Stage files explicitly: \`git add <specific files>\` only

### DON'T
- Commit without user confirmation
- Use \`git add -A\` or \`git add .\`
- Install tools globally — use nix devShell or \`make <target>\` instead
- Lint or format \`.md\` files (markdown linting is disabled)
- Use plan mode for small, well-scoped tasks — only for complex multi-step features
\`\`\`
```

## `.claude/rules/config.md`

Generated only when config management is detected or confirmed by user.

Template:

```markdown
## Agent Rules — Config Management

### DO
- Validate config schema before applying changes
- Create a rollback snapshot before any migration: \`cp config.yaml config.yaml.bak\`
- Test config changes in a dry-run or staging environment first
- Document every config key change in the commit message

### DON'T
- Apply config changes directly to production without a staged rollback plan
- Remove config keys without checking all consumers
- Commit secrets or credentials in config files
\`\`\`
```

## `.claude/rules/release.md`

Generated only when a release process is detected or confirmed by user.

Template:

```markdown
## Agent Rules — Release

### DO
- Run \`make check\` (or equivalent) before any release commit
- Tag releases using semantic versioning: \`vMAJOR.MINOR.PATCH\`
- Update changelog or release notes before tagging
- Verify smoke tests pass against the release artifact

### DON'T
- Push directly to \`main\`/\`master\` — use a PR
- Skip CI checks with \`--no-verify\` or equivalent
- Release from a dirty working tree
\`\`\`
```

## `.claude/commands/help.md`

Help slash command stub. Offered optionally.

Template:

```markdown
---
description: Show available commands and agent capabilities for this project.
---

List all available slash commands in \`.claude/commands/\` and agents in \`.claude/agents/\`, with a one-line description of each. Then show the key \`make\` targets from the Makefile.
\`\`\`
```
