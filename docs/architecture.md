# Architecture

## System Overview

harus-skills is a Claude Code plugin marketplace containing reusable skills. Skills are markdown-based instruction files that Claude Code executes as user-invocable commands. No runtime code; the "architecture" is file organization and metadata conventions.

## Project Structure

```text
harus-skills/
  skills/                        # Each subdirectory is one skill
    daily-language-lesson/       # Generates language learning lessons
      SKILL.md                   # Skill definition
      README.md                  # User documentation
    mkmr/                        # Creates merge requests
      SKILL.md
    init-project/                # Project initialization
      SKILL.md
      CONFIGS.md                 # Reference configs for tooling setup
  docs/                          # Project documentation
    plans/                       # Design documents and proposals
  lessons/                       # Generated output (gitignored)
  .claude-plugin/
    marketplace.json             # Plugin registry
  .agents/                       # Agent infrastructure
    MEMORY.md                    # Shared agent memory
    config.yaml                  # Agent configuration
```

## Module Map

| Skill                 | Purpose                   | Invocation               |
| --------------------- | ------------------------- | ------------------------ |
| daily-language-lesson | Generate en/ja/es lessons | `/lesson`, `/dll`        |
| mkmr                  | Create MRs from branch    | `/mkmr`                  |
| init-project          | Initialize project infra  | `/init-project`, `/init` |

## Data Flow

1. User invokes a skill via `/command`
2. Claude Code reads the skill's `SKILL.md`
3. YAML frontmatter configures metadata and tool restrictions
4. Markdown body provides execution instructions
5. Claude follows instructions, interacting with user and filesystem

## Dependencies

- **mise**: Task runner and tool version manager
- **prettier**: Markdown/JSON/YAML formatter
- **markdownlint-cli2**: Markdown linter
- **taplo**: TOML formatter
- **shfmt**: Shell script formatter
- **commitizen**: Standardized commit messages (optional)
