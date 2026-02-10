# harus-skills

leap higher

A collection of custom Claude Code skills for productivity and learning.

## Plugins

This marketplace contains two plugin collections:

### 🛠️ code-skills

Development and git workflow helpers.

**Skills:**

- `/mkmr` - Create merge requests from current branch to mainline with automated diff analysis and description generation

### 📚 language-skills

Language learning and lesson generation tools.

**Skills:**

- `/daily-language-lesson` (aliases: `/dll`, `/lesson`) - Generate comprehensive daily language learning lessons
  - **English**: Native level (advanced literature, idioms, sophisticated grammar)
  - **Japanese**: Native level (advanced kanji, keigo, literary expressions)
  - **Spanish**: Entry level (basic vocabulary, simple grammar)

Each lesson includes reading passages, vocabulary, comprehension questions, and grammar practice. Lessons are saved as markdown files in dated folders.

## Installation

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI tool installed

### Method 1: Install as Marketplace (Recommended)

This method allows you to install individual plugins as needed.

1. **Add this repository as a marketplace:**

   ```bash
   /plugin marketplace add azusachino/harus-skills
   ```

2. **Install plugins:**

   Option A - Via CLI:

   ```bash
   # Install both plugins
   /plugin install code-skills@harus-skills
   /plugin install language-skills@harus-skills

   # Or install individually
   /plugin install code-skills@harus-skills
   /plugin install language-skills@harus-skills
   ```

   Option B - Via Browse Interface:
   1. Run `/plugin marketplace browse`
   2. Select `harus-skills`
   3. Choose which plugin(s) to install (`code-skills` and/or `language-skills`)
   4. Select `Install now`

3. **Restart Claude Code** for changes to take effect

### Method 2: Install via Skill Directory (Legacy)

If you prefer to make all skills available without the plugin system:

1. Clone this repository:

   ```bash
   git clone <your-repo-url>
   cd harus-skills
   ```

2. Add to Claude Code configuration:

   Edit `~/.config/claude/config.json` (create if it doesn't exist):

   ```json
   {
     "skillDirectories": ["/path/to/harus-skills/skills"]
   }
   ```

3. Restart Claude Code

### Verify Installation

In Claude Code, check available skills:

```bash
/help
```

Your installed skills should appear in the skills section.

## Usage

### mkmr - Create Merge Request

```bash
/mkmr
```

The skill will guide you through:

1. Asking for permission to proceed
2. Identifying mainline branch (main/develop)
3. Checking for unstaged changes
4. Analyzing diff and generating description
5. Creating the merge request via gh/glab

### daily-language-lesson - Generate Language Lessons

```bash
# Generate today's language lessons
/lesson
# or
/daily-language-lesson
# or
/dll
```

Lessons are saved to `lessons/YYYY-MM-DD/` with three files:

- `english.md` - Native level
- `japanese.md` - Native level
- `spanish.md` - Entry level

## Development

### Setup

This repository uses [mise](https://mise.jdx.dev/) for tool management:

```bash
# Install mise (if not already installed)
curl https://mise.run | sh

# Install all tools and setup dev environment
mise install
mise run dev
```

### Daily Commands

```bash
mise fmt              # Format all files (markdown, JSON, YAML, TOML)
mise lint             # Lint markdown files
mise check            # Run all checks before committing
mise list-skills      # List all available skills
mise clean            # Remove generated lessons
```

**Important:** Always run `mise fmt` after editing files. Git hooks will auto-format on commit if installed via `mise run dev`.

### Available Tasks

Run `mise tasks` to see all available commands, or check `mise.toml` for details.

## Skill Structure

Each skill follows the [Agent Skills Standard](http://agentskills.io) format:

```s
skills/
  skill-name/
    SKILL.md          # Skill definition with YAML frontmatter and instructions
    README.md         # Optional: User documentation
```

### SKILL.md Format

```yaml
---
name: skill-name
description: Clear description of what the skill does and when to use it
metadata:
  author: Your Name
  version: "1.0.0"
  aliases: ["alias1", "alias2"] # Optional
allowed-tools: git gh glab # Optional: Restrict tool usage
---
# Skill Name

[Instructions for Claude on how to execute the skill]
```

## Contributing

Feel free to add your own skills to this collection:

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file following the format above
3. Optionally add a `README.md` for user documentation
4. Update `.claude-plugin/marketplace.json` to register the skill in the appropriate plugin
5. Test the skill in Claude Code
6. Submit a pull request

## Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official skills and examples
- [Agent Skills Standard](http://agentskills.io) - Specification and documentation
- [Claude Code Documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - Using skills in Claude
