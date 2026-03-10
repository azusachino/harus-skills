# Setup

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI
- nix (for devShell) or mise as fallback
- git

## Installation

```bash
git clone git@github.com:azusachino/harus-skills.git
cd harus-skills
```

Enter the nix devShell if using nix:

```bash
nix develop
```

## Build

No build step. This is a content repository.

## Run

Skills are invoked inside Claude Code:

```bash
/lesson          # Generate language lessons (Obsidian vault)
/nll             # Generate language lessons (Notion)
/init-project    # Initialize a project with agent infrastructure
/session         # Manage session state and memory
```

## Test

```bash
make check       # Run format check + lint + structure verify
make fmt-check   # Check formatting only
make lint        # Lint markdown only
make verify      # Verify repo structure only
```

## Development

```bash
make fmt         # Format all files
make lint-fix    # Lint and auto-fix markdown
make list-skills # List available skills
make clean       # Remove generated lessons
```
