# Notion Language Lesson Skill

Generate daily language learning lessons for English (advanced), Japanese (N1), and Spanish (B1–B2), pushed directly to a Notion database as structured toggle-block pages. Falls back to your Obsidian vault if Notion is unavailable.

## Features

- Same lesson content as `daily-language-lesson` — reading passage, vocabulary, comprehension questions, grammar point, writing exercise (Spanish)
- Each lesson day becomes a **Notion database row** with date, theme, language tags, and per-language reviewed checkboxes
- Lesson content lives inside the row's page body as **collapsible toggle sections** — one per language
- Answer keys are hidden inside a toggle by default — click to reveal
- Deduplication — warns before overwriting an existing row for the same date
- Fallback to Obsidian vault if Notion push fails

## Setup

### 1. Create a Notion integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it (e.g. `language-lessons`), select your workspace, click **Save**
4. Copy the **"Internal Integration Secret"** — this is your `NOTION_API_KEY` (starts with `ntn_...`)

### 2. Create the database

Create a new **full-page database** in Notion with these properties:

| Property | Type | Notes |
|---|---|---|
| `Name` | Title | Auto-filled as `YYYY-MM-DD — Theme` |
| `Date` | Date | The lesson date |
| `Theme` | Text | Unifying theme across all three lessons |
| `Languages` | Multi-select | Add options: `English`, `Japanese`, `Spanish` |
| `English Reviewed` | Checkbox | Track review progress |
| `Japanese Reviewed` | Checkbox | Track review progress |
| `Spanish Reviewed` | Checkbox | Track review progress |
| `Notes` | Text | Free-form study notes |

### 3. Grant your integration access to the database

**Important:** Notion integrations require explicit page-level access — they do not have access to your whole workspace automatically.

Grant access from the integration settings page:

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click on your integration
3. Under **"Access"** → **"Add page"** → search for and select your lessons database
4. Save

> **Note:** You cannot grant access from the database's "Connections" panel if the integration was created in a different workspace. Always grant access from the integration settings page.

### 4. Get the database ID

Open the database in Notion. The ID is in the URL:

```
https://www.notion.so/yourworkspace/3167242dc82180cba33fe7d620649eed?v=...
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                    NOTION_DATABASE_ID (32-char hex before ?v=)
```

### 5. Set environment variables

Add to your `~/.config/fish/config.fish` (or equivalent shell config):

```fish
set -gx NOTION_API_KEY "ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
set -gx NOTION_DATABASE_ID "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Reload your shell or run `source ~/.config/fish/config.fish`.

Optionally also set `VAULT_PATH` for the Obsidian fallback:

```fish
set -gx VAULT_PATH "/path/to/your/vault/journal/daily"
```

## Usage

```bash
/notion-language-lesson        # today's lesson
/nll                           # alias
/nll 2026-03-05                # specific date
```

## Notion page structure

Each database row's page body contains three toggleable sections:

```
🇺🇸 English Lesson          ← click to expand
  📅 Theme | Level callout
  📖 Reading Passage
  📚 Vocabulary
  ❓ Comprehension Questions
  📝 Grammar Point
  ✅ Answer Key              ← hidden toggle, click to reveal

🇯🇵 Japanese Lesson          ← click to expand
  [same structure in Japanese]

🇪🇸 Spanish Lesson           ← click to expand
  [same structure + ✍️ Writing Exercise]
```

## Fallback behavior

If the Notion push fails for any reason (network error, API error), the skill automatically runs the `daily-language-lesson` fallback pipeline and writes the lesson to your Obsidian vault (or local `lessons/` folder). The error reason is reported so you can fix and retry.

## Daily workflow

1. Run `/nll` each morning
2. Open Notion — today's row appears in your database
3. Click into the row and expand a language section to start studying
4. Check the **Reviewed** checkbox when done with each language
5. Add study notes in the **Notes** field
