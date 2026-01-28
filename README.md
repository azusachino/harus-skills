# harus-skills

leap higher

A collection of custom Claude Code skills for productivity and learning.

## Skills

### 📚 Daily Language Lesson (`/daily-language-lesson`, `/dll`, `/lesson`)

Generate comprehensive daily language learning lessons for multiple languages.

- **English**: Native level (advanced literature, idioms, sophisticated grammar)
- **Japanese**: Native level (advanced kanji, keigo, literary expressions)
- **Spanish**: Entry level (basic vocabulary, simple grammar)

Each lesson includes reading passages, vocabulary, comprehension questions, and grammar practice. Lessons are saved as markdown files in dated folders.

[Learn more →](skills/daily-language-lesson/README.md)

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd harus-skills

# Install skills (adds to Claude Code config)
make install

# Restart Claude Code, then use:
/lesson
```

## Installation

### Automated Installation (Recommended)

```bash
make install
```

This will:
- Create `~/.config/claude/config.json` if it doesn't exist
- Add this repository's skills directory to the configuration
- Verify the setup

**Important**: Restart Claude Code after installation for changes to take effect.

### Manual Installation

1. Clone this repository
2. Edit `~/.config/claude/config.json` and add:
   ```json
   {
     "skillDirectories": [
       "/path/to/harus-skills/skills"
     ]
   }
   ```
3. Restart Claude Code

### Verify Installation

```bash
make verify-config
```

## Usage

### Daily Language Lesson

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

## Makefile Commands

```bash
make help           # Show all available commands
make install        # Install skills to Claude Code
make uninstall      # Remove skills from Claude Code
make verify-config  # Check configuration status
make list-skills    # List all available skills
make test           # Verify lesson generation
make clean          # Remove generated lessons
```

## Contributing

Feel free to add your own skills to this collection. Each skill should have its own directory under `skills/` with:
- `skill.json` - Skill metadata and configuration
- `prompt.md` - Instructions for Claude on how to execute the skill
- `README.md` - Documentation for users

