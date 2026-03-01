# Notion Language Lesson Skill — Design

**Date**: 2026-03-01
**Status**: Approved

## Overview

A new skill `notion-language-lesson` (alias `nll`) that generates daily language lessons identical in content to the existing `daily-language-lesson` (dll) skill, but writes them directly to a pre-created Notion database as structured blocks. Notion is the primary output; the existing Obsidian vault write is the fallback.

## Requirements

- Auth: `NOTION_API_KEY` and `NOTION_DATABASE_ID` environment variables
- Database: pre-created by user in Notion with required properties
- Output: Notion database row per day, lessons as nested toggle blocks in the row page body
- Fallback: if Notion push fails, fall back to existing dll Obsidian vault pipeline
- Dedup: if a row for the target date already exists, warn and ask user before overwriting

## Notion Database Properties

| Property | Notion Type | Notes |
| :--- | :--- | :--- |
| `Name` | Title | Set to `YYYY-MM-DD — Theme` |
| `Date` | Date | The lesson date |
| `Theme` | Rich Text | Unifying theme across all three lessons |
| `Languages` | Multi-select | Values: `English`, `Japanese`, `Spanish` |
| `English Reviewed` | Checkbox | Review tracking |
| `Japanese Reviewed` | Checkbox | Review tracking |
| `Spanish Reviewed` | Checkbox | Review tracking |
| `Notes` | Rich Text | Free-form study notes |

## Page Body Block Structure

Each database row's page body contains three top-level toggle headings, one per language:

```text
Toggle Heading 2: "🇺🇸 English Lesson"
  ├── Callout: Theme + Level
  ├── Heading 3: "📖 Reading Passage"
  │   └── Paragraph blocks
  ├── Heading 3: "📚 Vocabulary"
  │   └── Bulleted list items (word → definition → examples)
  ├── Heading 3: "❓ Comprehension Questions"
  │   └── Numbered list items
  ├── Heading 3: "📝 Grammar Point"
  │   └── Paragraph + bulleted examples + numbered exercises
  └── Heading 3: "✅ Answer Key"
      └── Toggle blocks (hidden by default)

Toggle Heading 2: "🇯🇵 Japanese Lesson"
  └── [same structure in Japanese]

Toggle Heading 2: "🇪🇸 Spanish Lesson"
  └── [same structure + ✍️ Writing Exercise section]
```text

Answer keys are wrapped in toggle blocks so they are hidden by default — the user must click to reveal them, enabling self-testing.

## Implementation Approach

Python scripts (stdlib only, no pip dependencies), consistent with the existing `dll-fill.py` helper.

Two helper scripts under `skills/notion-language-lesson/scripts/`:

### `nll-status.py`

Queries the Notion database for today's (or target) date. Outputs `KEY=value` lines:

- `TARGET_DATE` — the lesson date (today or passed argument)
- `MODE` — `create` (no row exists) or `warn` (row exists)
- `RECENT_THEMES` — pipe-separated themes from the last 7 rows (to avoid repetition)

### `nll-push.py`

Accepts temp files for each lesson (en, ja, es) and:

1. Creates a new Notion database row with all properties set
2. Appends the full block structure to the row's page body via the Notion Blocks API
3. Outputs the resulting Notion page URL on success

## Execution Flow

```text
Step 0: Environment check
  → Verify NOTION_API_KEY and NOTION_DATABASE_ID are set; abort with clear error if missing
  → Run nll-status.py [ARGUMENT] → parse TARGET_DATE, MODE, RECENT_THEMES

Step 1: Generate lessons
  → Pick unifying theme (avoiding RECENT_THEMES)
  → Generate English (IELTS Band 7+), Japanese (N1), Spanish (B1–B2) lessons
  → Write each to temp file: /tmp/nll-en.txt, /tmp/nll-ja.txt, /tmp/nll-es.txt

Step 2: Push to Notion (primary)
  → Run nll-push.py TARGET_DATE THEME --en /tmp/nll-en.txt --ja /tmp/nll-ja.txt --es /tmp/nll-es.txt
  → On success: report Notion page URL to user

Step 3: Fallback to Obsidian vault (if Step 2 fails)
  → Run existing dll-status.sh + dll-fill.py pipeline
  → Report fallback path and error reason to user

Step 4: Confirm to user
  → Notion page URL (or local fallback path)
  → Theme used
  → Mode (created / skipped)
  → One-line topic summary per language
```text

## MODE Handling

- `create` — no row for target date in DB; proceed normally
- `warn` — row already exists; ask "A lesson for TARGET_DATE already exists in Notion. Overwrite?" and wait for confirmation

## Skill Invocation

```text
/notion-language-lesson          # today's lesson
/notion-language-lesson 2026-03-05   # specific date
/nll                             # alias
```text

## Files to Create

```text
skills/notion-language-lesson/
  SKILL.md                       # skill definition
  scripts/
    nll-status.py                # DB query + status check
    nll-push.py                  # Notion API push
```text

## Environment Variables

| Variable | Required | Description |
| :--- | :--- | :--- |
| `NOTION_API_KEY` | Yes | Notion integration secret |
| `NOTION_DATABASE_ID` | Yes | ID of the pre-created lessons database |
| `VAULT_PATH` | No | Obsidian vault path (for fallback only) |
