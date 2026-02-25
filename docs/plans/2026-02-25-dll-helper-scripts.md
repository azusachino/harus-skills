# dll-status.sh Helper Script Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bundle a single shell script with the daily-language-lesson skill so Claude calls it once to get all Step 0 context (date, vault path, file mode, recent themes) as structured `KEY=value` output — no improvisation needed.

**Architecture:** One script at `skills/daily-language-lesson/scripts/dll-status.sh`. It handles date resolution, VAULT_PATH fallback, file existence/content detection (outputting a MODE), and theme scanning. SKILL.md Step 0 is replaced with a single `bash <BASE_DIR>/scripts/dll-status.sh [ARGUMENT]` call. No new dependencies.

**Tech Stack:** bash, standard POSIX tools (grep, sed, wc, ls, mkdir), git (for repo root fallback only)

---

## Task 1: Create the scripts directory and dll-status.sh

**Files:**

- Create: `skills/daily-language-lesson/scripts/dll-status.sh`

### Step 1: Create the directory

```bash
mkdir -p skills/daily-language-lesson/scripts
```

### Step 2: Write the script

Create `skills/daily-language-lesson/scripts/dll-status.sh` with this exact content:

```bash
#!/usr/bin/env bash
# dll-status.sh — Pre-flight check for the daily-language-lesson skill
#
# Usage: dll-status.sh [TARGET_DATE]
#   TARGET_DATE: optional YYYY-MM-DD; defaults to today
#
# Outputs KEY=value lines:
#   TARGET_DATE, YYYY, OUTPUT_PATH, MODE, RECENT_THEMES
#
# MODE values:
#   create — file does not exist
#   append — file exists but has no ## writing section
#   fill   — file exists with ## writing but all ad-note blocks are empty
#   warn   — file exists with real lesson content in ad-note blocks

set -euo pipefail

TARGET_DATE="${1:-$(date +%Y-%m-%d)}"
YYYY="${TARGET_DATE:0:4}"

# Resolve output path
if [ -n "${VAULT_PATH:-}" ]; then
  OUTPUT_DIR="$VAULT_PATH/$YYYY"
  OUTPUT_PATH="$OUTPUT_DIR/$TARGET_DATE.md"
else
  REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo ".")"
  OUTPUT_DIR="$REPO_ROOT/lessons"
  OUTPUT_PATH="$OUTPUT_DIR/$TARGET_DATE.md"
fi

mkdir -p "$OUTPUT_DIR"

# Detect MODE
if [ ! -f "$OUTPUT_PATH" ]; then
  MODE="create"
elif ! grep -q "^## writing" "$OUTPUT_PATH" 2>/dev/null; then
  MODE="append"
else
  # Check if any ad-note block contains real content (non-whitespace)
  HAS_CONTENT=$(awk '
    /^```ad-note/{in_block=1; content=""; next}
    in_block && /^```/{
      if (content ~ /[^ \t\n]/) { print "yes"; exit }
      in_block=0; next
    }
    in_block { content = content $0 "\n" }
  ' "$OUTPUT_PATH")

  if [ "$HAS_CONTENT" = "yes" ]; then
    MODE="warn"
  else
    MODE="fill"
  fi
fi

# Scan recent themes from last 7 lesson files with real content
SCAN_DIR="$OUTPUT_DIR"
RECENT_THEMES=""

if [ -d "$SCAN_DIR" ]; then
  THEMES=""
  while IFS= read -r f; do
    theme=$(grep '\*\*Theme\*\*:' "$f" 2>/dev/null | head -1 | sed 's/.*\*\*Theme\*\*: //')
    if [ -n "$theme" ]; then
      date_str=$(basename "$f" .md)
      if [ -n "$THEMES" ]; then
        THEMES="$THEMES | $date_str: $theme"
      else
        THEMES="$date_str: $theme"
      fi
    fi
  done < <(
    ls "$SCAN_DIR"/*.md 2>/dev/null \
      | grep -v "$TARGET_DATE.md" \
      | sort -r \
      | while IFS= read -r f; do
          size=$(wc -c < "$f" 2>/dev/null || echo 0)
          [ "$size" -gt 500 ] && echo "$f"
        done \
      | head -7
  )
  RECENT_THEMES="$THEMES"
fi

echo "TARGET_DATE=$TARGET_DATE"
echo "YYYY=$YYYY"
echo "OUTPUT_PATH=$OUTPUT_PATH"
echo "MODE=$MODE"
echo "RECENT_THEMES=$RECENT_THEMES"
```

### Step 3: Make it executable

```bash
chmod +x skills/daily-language-lesson/scripts/dll-status.sh
```

### Step 4: Verify it runs without error

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh 2026-03-01
```

Expected output (values will vary by machine):

```text
TARGET_DATE=2026-03-01
YYYY=2026
OUTPUT_PATH=/Users/.../journal/daily/2026/2026-03-01.md
MODE=warn
RECENT_THEMES=2026-02-28: Distributed Systems & The Philosophy of Consensus | ...
```

Check all five keys are present and MODE is one of `create/append/fill/warn`.

### Step 5: Verify fallback (no VAULT_PATH)

```bash
VAULT_PATH="" bash skills/daily-language-lesson/scripts/dll-status.sh 2099-01-01
```

Expected: `OUTPUT_PATH` ends in `lessons/2099-01-01.md`, `MODE=create` (file won't exist).

### Step 6: Commit

```bash
git add skills/daily-language-lesson/scripts/dll-status.sh
git commit -m "feat(dll): add dll-status.sh pre-flight helper script"
```

---

## Task 2: Update SKILL.md — frontmatter and Step 0

**Files:**

- Modify: `skills/daily-language-lesson/SKILL.md`

### Step 1: Add `allowed-tools: bash` to frontmatter

The current frontmatter (lines 1–9):

```yaml
---
name: daily-language-lesson
description: Generate daily language lessons ...
metadata:
  author: haru
  version: 2.0.0
  aliases: ["dll", "lesson"]
disable-model-invocation: true
---
```

Add one line before the closing `---`:

```yaml
allowed-tools: bash
```

### Step 2: Replace the entire Step 0 section

Find this block in SKILL.md (starts at `### Step 0: Vault status check`):

```markdown
### Step 0: Vault status check

1. **Resolve the target date**:
   ...

2. **Resolve the output path**:
   ...

3. **Check for existing lesson**:
   ...

4. **Scan recent topics for rotation**:
   ...
```

Replace it entirely with:

````markdown
### Step 0: Vault status check

Run the helper script using the base directory shown at skill invocation:

```bash
bash "<BASE_DIR>/scripts/dll-status.sh" [ARGUMENT]
```

Parse the `KEY=value` output lines:

- `TARGET_DATE`, `YYYY`, `OUTPUT_PATH` — use in every section header and for all file writes; never substitute today's date when an argument was passed
- `MODE` — determines how to write the file:
  - `create` — file does not exist; create it with the three sections
  - `append` — file exists but has no `## writing`; append the three sections after existing content
  - `fill` — file exists with empty `ad-note` blocks (Obsidian pre-created template); replace each empty block with lesson content
  - `warn` — file has real content; ask user "A lesson for TARGET_DATE already exists. Overwrite?" and wait for confirmation before proceeding
- `RECENT_THEMES` — pipe-separated list of recent themes; pass as "avoid repeating these topics" context when selecting today's theme
````

### Step 3: Bump version in frontmatter

Change `version: 2.0.0` → `version: 2.1.0`

### Step 4: Verify the SKILL.md looks correct

Read the file and confirm:

- `allowed-tools: bash` is in the frontmatter
- `version: 2.1.0`
- Step 0 now references `dll-status.sh` instead of prose instructions
- Steps 1, 2, 3 are unchanged

### Step 5: Commit

```bash
git add skills/daily-language-lesson/SKILL.md
git commit -m "feat(dll): update SKILL.md to use dll-status.sh in Step 0"
```

---

## Task 3: Smoke test end-to-end

### Step 1: Run the script for a date that has a real lesson

Pick a date you know has content (e.g. `2026-03-01`):

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh 2026-03-01
```

Expected: `MODE=warn` (file has content).

### Step 2: Run for a future date that won't exist

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh 2099-12-31
```

Expected: `MODE=create`, `OUTPUT_PATH` points to vault or `lessons/`.

### Step 3: Run for today's Obsidian pre-created file

If today's file exists in the vault but is empty/pre-created:

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh
```

Expected: `MODE=fill` (empty ad-note blocks) or `MODE=create` if not pre-created.

### Step 4: Run mise fmt on the script

```bash
mise fmt
```

Expected: no errors (shfmt will format `dll-status.sh` in place).

### Step 5: Final commit if fmt changed anything

```bash
git diff --stat
# If changes:
git add skills/daily-language-lesson/scripts/dll-status.sh
git commit -m "style(dll): apply shfmt formatting to dll-status.sh"
```
