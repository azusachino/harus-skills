# daily-language-lesson Improvement Design

**Date**: 2026-02-25
**Branch**: dev

## Overview

Improve the `daily-language-lesson` skill with three categories of changes:
vault integration, skill quality fixes, and new mise tooling.

## Goals

1. Generate lessons directly into the user's Obsidian vault
2. Fix the date bug in lesson section headers
3. Add a writing exercise section to Spanish (already present in vault, missing
   from SKILL.md)
4. Keep `writing` section label consistent with existing vault files
5. Add vault status checks before generating (existence, recent topics)
6. Add `mise run lesson` and `mise run lesson-date` tasks
7. Rewrite README.md to reflect current state

## Vault Structure

The user's vault layout:

```text
/Users/azusachino/Documents/harusObsidian/journal/daily/
  YYYY/
    YYYY-MM-DD.md    ← Obsidian pre-creates these with YAML frontmatter
```

Files already contain frontmatter like:

```yaml
---
created: YYYY-MM-DD HH:MM
modified: YYYY-MM-DD HH:MM
tags:
  - daily-relief
---
```

Obsidian pre-creates the entire year's files. The skill must **append** lesson
sections rather than overwrite.

## Configuration

Introduce `VAULT_PATH` environment variable (set in `.env` at repo root,
gitignored):

```env
VAULT_PATH=/Users/azusachino/Documents/harusObsidian/journal/daily
```

Output path resolution:

```text
$VAULT_PATH/YYYY/YYYY-MM-DD.md    (if VAULT_PATH is set)
lessons/YYYY-MM-DD.md             (fallback if not set)
```

## SKILL.md Changes

### 1. Date argument support

Accept an optional date argument:

- `/lesson` → use today's date
- `/lesson 2026-03-01` → use the specified date

The resolved date must be used **consistently** in all output: the file path,
and every section header inside `ad-note` blocks.

### 2. Vault status check (new Step 0)

Before generating, the skill will:

1. Read `VAULT_PATH` to determine output path
2. Check if `## writing` already exists in the target file → warn user, ask
   whether to overwrite or skip
3. Scan the last 7 date-named files in the vault (or `lessons/`) → extract the
   `**Theme**:` line from each → pass as "avoid these recent topics" context to
   the generator

### 3. Append logic

- If target file exists (Obsidian pre-created with frontmatter only) → append
  the three sections after existing content
- If `## writing` already present → prompt before overwriting
- If file does not exist → create with minimal frontmatter + sections

### 4. Section labels (no change needed)

Keep existing labels: `## writing`, `## japanese`, `## spanish`. These already
match the vault files.

### 5. Spanish writing exercise

Add `✍️ Writing Exercise` section to the Spanish lesson template (already
appearing in vault output, but missing from SKILL.md spec). Each Spanish lesson
should include:

- A short writing prompt (5–8 sentences)
- Suggested vocabulary list
- A sample response

### 6. Date bug fix

Lesson headers inside `ad-note` blocks must use the **resolved target date**,
not the current date. The execution steps will explicitly bind the resolved date
string before generating content.

## mise.toml Changes

Add two tasks to `mise.toml`:

```toml
[tasks.lesson]
description = "Generate today's language lesson to vault (or lessons/ fallback)"
run = "claude '/lesson'"

[tasks."lesson-date"]
description = "Generate lesson for a specific date. Usage: DATE=2026-03-01 mise run lesson-date"
run = "claude '/lesson ${DATE}'"
```

## README.md Rewrite

Full rewrite covering:

- Correct single-file `ad-note` output format with `writing` / `japanese` /
  `spanish` sections
- `VAULT_PATH` setup instructions (`.env` file)
- Updated mise task list (`mise run lesson`, `DATE=... mise run lesson-date`)
- Year subfolder path resolution explained
- Remove stale `prompt.md` reference
- Update output structure example to show `daily/YYYY/YYYY-MM-DD.md`

## Files Changed

| File                                      | Change         |
| ----------------------------------------- | -------------- |
| `skills/daily-language-lesson/SKILL.md`   | Major update   |
| `skills/daily-language-lesson/README.md`  | Full rewrite   |
| `mise.toml`                               | Add 2 tasks    |
| `.env.example`                            | New file       |
| `.gitignore`                              | Add `.env`     |

## Out of Scope

- Lesson stats / streak tracking (deferred)
- Lesson index file
- Multiple vault path configurations
