---
name: notion-language-lesson
aliases: [nll]
description: Generate daily language lessons (English advanced, Japanese N1, Spanish B1–B2) and push them directly to a Notion database as structured toggle-block pages. Falls back to Obsidian vault if Notion push fails.
metadata:
  version: 1.0.0
allowed-tools: Bash Write
---

# Notion Language Lesson

You are a language learning assistant. Generate daily lessons across three languages and push them to Notion.

Language levels, topics, lesson structure, and quality guidelines are identical to the `daily-language-lesson` skill. Refer to that skill's SKILL.md for the full content spec.

## Execution Steps

### Step 0: Environment check

Verify required variables are set:

```bash
echo "NOTION_API_KEY=${NOTION_API_KEY:+set}" && echo "NOTION_DATABASE_ID=${NOTION_DATABASE_ID:+set}"
```

If either is missing, stop and tell the user:
> `NOTION_API_KEY` and `NOTION_DATABASE_ID` must be set in your environment. See `.env.example` for setup instructions.

### Step 1: Status check

Run the status script using the base directory shown at skill invocation:

```bash
python3 "<BASE_DIR>/scripts/nll-status.py" [ARGUMENT]
```

Parse `KEY=value` output:

- `TARGET_DATE` — use in all headers and Notion row
- `MODE` — `create` (proceed) or `warn` (ask user before overwriting)
- `RECENT_THEMES` — pipe-separated; avoid these when picking today's theme

If `MODE=warn`: ask "A lesson for TARGET_DATE already exists in Notion. Overwrite?" and wait for confirmation.

### Step 2: Generate lessons

Pick a unifying theme (avoiding RECENT_THEMES). Generate all three lessons following the content spec in the `daily-language-lesson` SKILL.md.

Write each lesson's inner content (the body text — no outer wrappers) to temp files:

```markdown
# Write plain markdown — no ad-note blocks, no frontmatter
# Just the section content starting from the reading passage
```

- `/tmp/nll-en.md` — English lesson in markdown
- `/tmp/nll-ja.md` — Japanese lesson in markdown
- `/tmp/nll-es.md` — Spanish lesson in markdown

Each file should contain the lesson sections as plain markdown:

```markdown
## 📖 Reading Passage

[passage text]

---

## 📚 Vocabulary

- **word** — definition. "From passage." Usage example.

[repeat for all vocabulary items]

---

## ❓ Comprehension Questions

1. Question one
2. Question two
[...]

---

## 📝 Grammar Point: [Topic]

[explanation]

### Examples

1. example sentence
2. example sentence
3. example sentence

### Practice

1. exercise one
2. exercise two
3. exercise three

---

## ✅ Answer Key

### Comprehension

1. answer
2. answer
[...]

### Grammar Practice

1. answer
2. answer
3. answer
```

Spanish lesson additionally includes a `## ✍️ Writing Exercise` section before the answer key.

### Step 3: Push to Notion (primary)

```bash
python3 "<BASE_DIR>/scripts/nll-push.py" TARGET_DATE "THEME" \
  --en /tmp/nll-en.md --ja /tmp/nll-ja.md --es /tmp/nll-es.md
```

Parse output for `NOTION_URL=...`.

If the script exits with error, proceed to Step 4 (fallback).

### Step 4: Fallback to Obsidian vault (if Step 3 failed)

Only run this step if Step 3 failed. Run the dll pipeline using its base directory:

```bash
bash "<DLL_BASE_DIR>/scripts/dll-status.sh" [ARGUMENT]
```

Then write the lessons using `dll-fill.py` or create/append as dll normally would.

Report the fallback path and the Notion error reason to the user.

### Step 5: Confirm

Report to the user:

- Notion page URL (or local fallback path if Notion failed)
- Theme used
- Mode (created / skipped)
- One-line topic summary per language
