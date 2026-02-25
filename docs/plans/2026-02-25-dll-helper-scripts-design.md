# Design: dll-status.sh Helper Script for daily-language-lesson

**Date**: 2026-02-25
**Status**: Approved

## Problem

Every time the `daily-language-lesson` skill runs, Claude improvises all the Step 0 shell logic from scratch: resolving the target date, checking `VAULT_PATH`, computing the output path, detecting file mode, and scanning recent themes with ad-hoc `awk`/`grep`/`find` commands. This is fragile, inconsistent, and wastes context.

## Solution

Bundle a single deterministic shell script with the skill. Claude calls it once and reads structured output — no improvisation needed.

## Approach: Single Composite Script

**File**: `skills/daily-language-lesson/scripts/dll-status.sh`

Accepts one optional argument (the target date, e.g. `2026-03-02`). If not provided, uses `date +%Y-%m-%d`.

### Output format

Key=value lines printed to stdout, one per line:

```
TARGET_DATE=2026-03-02
YYYY=2026
OUTPUT_PATH=/Users/.../journal/daily/2026/2026-03-02.md
MODE=fill
RECENT_THEMES=2026-03-01: The Piano as a Mirror | 2026-02-28: Distributed Systems | ...
```

### MODE values

| Mode | Condition |
|------|-----------|
| `create` | File does not exist |
| `append` | File exists, no `## writing` section found |
| `fill` | File exists with `## writing` but all ad-note blocks are empty (Obsidian pre-created template) |
| `warn` | File exists with real lesson content in ad-note blocks |

### Theme detection

- List all `.md` files in the vault year directory sorted by date descending
- Filter to files with actual content (size > 500 bytes)
- Exclude the target date file itself
- Take the last 7
- For each, extract the `**Theme**:` line from inside the first `ad-note` block after `## writing`
- Join with ` | `

### VAULT_PATH fallback

If `VAULT_PATH` is not set, output path falls back to `lessons/TARGET_DATE.md` relative to the repo root (same as current skill behaviour).

## SKILL.md Change

Replace the entire Step 0 prose with:

```markdown
### Step 0: Vault status check

Run the helper script using the base directory shown at skill invocation:

  bash "<BASE_DIR>/scripts/dll-status.sh" [ARGUMENT]

Parse the KEY=value output:
- TARGET_DATE, YYYY, OUTPUT_PATH — use throughout generation and all headers
- MODE — determines how to write the file (create / append / fill / warn)
- RECENT_THEMES — pass as "avoid repeating these topics" context to generation

If MODE=warn, show the user: "A lesson for TARGET_DATE already exists with content. Overwrite?"
and wait for confirmation before proceeding.
```

Also add `allowed-tools: bash` to the SKILL.md YAML frontmatter.

## Files Changed

- `skills/daily-language-lesson/scripts/dll-status.sh` — new file
- `skills/daily-language-lesson/SKILL.md` — Step 0 replaced, frontmatter updated
