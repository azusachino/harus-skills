# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains custom Claude Code skills for productivity and learning. Skills are user-invocable commands that extend Claude Code's capabilities. The repository uses Claude's plugin marketplace system via `.claude-plugin/marketplace.json` configuration.

## Repository Structure

```sh
skills/                         # Custom skill definitions
  daily-language-lesson/        # Language learning lesson generator
    SKILL.md                   # Skill definition with YAML frontmatter
    README.md                  # User documentation
  mkmr/                        # Merge request creation skill
    SKILL.md                   # Skill definition with YAML frontmatter
lessons/YYYY-MM-DD/            # Generated lesson files (gitignored)
.claude-plugin/                # Claude plugin configuration
  marketplace.json             # Marketplace and plugin registration
```

## Architecture

### Skill System

All skills follow the [Agent Skills Standard](http://agentskills.io) format with `SKILL.md` files:

- YAML frontmatter contains metadata (name, description, metadata block, allowed-tools)
- Markdown body contains execution instructions for Claude
- Optional `README.md` for user-facing documentation

### Plugin Configuration

The `.claude-plugin/marketplace.json` file defines the marketplace structure:

- **Marketplace name**: `harus-skills`
- **Two separate plugins**:
  1. `code-skills` - Development and git workflow helpers (contains `mkmr`)
  2. `language-skills` - Language learning tools (contains `daily-language-lesson`)
- Skills can be invoked as `/skill-name` or `/plugin-name:skill-name`
- Users can install individual plugins or all skills via skill directory method

### Skill Invocation

Skills are invoked via the Skill tool:

- `/daily-language-lesson` (aliases: `/dll`, `/lesson`) or `/language-skills:daily-language-lesson`
- `/mkmr` or `/code-skills:mkmr`

## Skill Development

### daily-language-lesson Skill (language-skills plugin)

Generates markdown-based language lessons at different proficiency levels:

- English: Native level (advanced literature, idioms, sophisticated grammar)
- Japanese: Native level (advanced kanji, keigo, literary expressions)
- Spanish: Entry level (basic vocabulary, simple grammar)

Output structure: `lessons/YYYY-MM-DD/{english,japanese,spanish}.md`

Each lesson includes:

1. Reading passage (300-400 words/characters, 150-200 for Spanish)
2. Vocabulary section (8-10 words with pronunciation, definitions, examples)
3. Comprehension questions (5 questions with answer key)
4. Grammar point with explanations, examples, and practice exercises

The skill creates structured markdown files with emojis in section headers (📖, 📚, ❓, 📝, ✅) for visual organization.

### mkmr Skill (code-skills plugin)

Creates merge requests from current branch to mainline branch. Workflow:

1. Ask user permission before executing tasks
2. Identify mainline branch (main or develop)
3. Check gh/glab tool availability
4. Verify not on mainline branch
5. Check for unstaged changes and commit if necessary
6. Review diff between current and mainline branch
7. Push to remote if needed
8. Create merge request with detailed description

Uses `allowed-tools: git gh glab` to restrict tool usage.

## Installation Methods

### Method 1: Marketplace Plugin Installation (Recommended)

```bash
/plugin marketplace add <github-username>/harus-skills
/plugin install code-skills@harus-skills
/plugin install language-skills@harus-skills
```

### Method 2: Skill Directory (Legacy)

Adds skills directory to `~/.config/claude/config.json`:

```json
{
  "skillDirectories": [
    "/path/to/harus-skills/skills"
  ]
}
```

This makes all skills available without the plugin system.

## Development Workflow

### Formatting and Linting

This repository uses [mise](https://mise.jdx.dev/) for tool management and task automation.

**Setup:**

```bash
mise install          # Install all required tools
mise run dev          # Setup development environment (includes git hooks)
```

**Common commands:**

```bash
mise fmt              # Format all files (markdown, JSON, YAML, TOML, shell)
mise fmt-check        # Check formatting without modifying
mise lint             # Lint markdown files
mise lint-fix         # Lint and fix markdown files
mise check            # Run all checks (format, lint, verify)
mise list-skills      # List all available skills
mise clean            # Remove generated lessons
mise verify           # Verify repository structure
```

**IMPORTANT:** Always run `mise fmt` after editing files. Git hooks are available to auto-format on commit.

### File Formatting

- **Markdown**: Prettier with prose wrap at 80 characters
- **JSON/YAML**: Prettier with 2-space indentation
- **TOML**: Taplo formatter
- **Shell scripts**: shfmt with 2-space indentation

## Key Conventions

- All skills use SKILL.md format with YAML frontmatter
- Skills should ask for user permission before executing commands (see mkmr workflow)
- Generated content goes to `lessons/` directory which is gitignored
- The mkmr skill explicitly avoids emojis in git commit messages and MR descriptions
- The daily-language-lesson skill uses emojis for formatting lesson sections
- Always format files with `mise fmt` before committing
