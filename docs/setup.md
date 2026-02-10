# Setup

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- [mise](https://mise.jdx.dev/) (tool version manager)
- git

## Installation

```bash
git clone git@github.com:azusachino/harus-skills.git
cd harus-skills
mise install
mise run dev
```

## Build

No build step. This is a content repository.

## Run

Skills are invoked inside Claude Code:

```bash
/lesson              # Generate language lessons
/mkmr                # Create merge request
/init-project        # Initialize a project
```

## Test

```bash
mise check           # Run format check + lint + structure verify
mise fmt-check       # Check formatting only
mise lint            # Lint markdown only
mise verify          # Verify repo structure only
```

## Development

```bash
mise fmt             # Format all files
mise lint-fix        # Lint and auto-fix markdown
mise list-skills     # List available skills
mise clean           # Remove generated lessons
```
