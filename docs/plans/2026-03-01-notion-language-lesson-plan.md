# Notion Language Lesson Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a `notion-language-lesson` (alias `nll`) skill that generates daily language lessons and pushes them to a pre-created Notion database as structured toggle-block pages, with fallback to the existing Obsidian vault pipeline.

**Architecture:** Two Python helper scripts (`nll-status.py` and `nll-push.py`) under `skills/notion-language-lesson/scripts/`. The SKILL.md orchestrates env checks, lesson generation, temp-file writing, and script invocation — mirroring the dll skill flow. Lesson content is written to temp markdown files then converted to Notion block JSON by `nll-push.py`.

**Tech Stack:** Python 3 stdlib only (`urllib`, `json`, `argparse`, `datetime`) — no pip dependencies. Notion REST API v1 (`2022-06-28`). Same temp-file + helper-script pattern as the existing dll skill.

---

### Task 1: Create skill directory structure

**Files:**
- Create: `skills/notion-language-lesson/scripts/.gitkeep`

**Step 1: Create directories**

```bash
mkdir -p skills/notion-language-lesson/scripts
```

**Step 2: Verify structure**

```bash
ls skills/notion-language-lesson/
# Expected: scripts/
```

**Step 3: Commit**

```bash
git add skills/notion-language-lesson/
git commit -m "chore: scaffold notion-language-lesson skill directory"
```

---

### Task 2: Write `nll-status.py`

**Files:**
- Create: `skills/notion-language-lesson/scripts/nll-status.py`

**What it does:** Queries the Notion database for an existing row on the target date. Outputs `KEY=value` lines for the SKILL.md to parse: `TARGET_DATE`, `MODE` (`create` or `warn`), `RECENT_THEMES` (pipe-separated themes from last 7 rows).

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
nll-status.py — Pre-flight check for the notion-language-lesson skill.

Usage: python3 nll-status.py [TARGET_DATE]
  TARGET_DATE: optional YYYY-MM-DD; defaults to today

Outputs KEY=value lines:
  TARGET_DATE=YYYY-MM-DD
  MODE=create|warn
  RECENT_THEMES=theme1|theme2|...

Reads from environment:
  NOTION_API_KEY      — Notion integration secret
  NOTION_DATABASE_ID  — ID of the pre-created lessons database
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.error


def get_env(key):
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: {key} environment variable is not set", file=sys.stderr)
        sys.exit(1)
    return val


def notion_query(api_key, database_id, payload):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        try:
            datetime.date.fromisoformat(target_date)
        except ValueError:
            print(f"ERROR: Invalid date format: {target_date}. Use YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
    else:
        target_date = datetime.date.today().isoformat()

    api_key = get_env("NOTION_API_KEY")
    database_id = get_env("NOTION_DATABASE_ID")

    # Check if a row already exists for target date
    try:
        result = notion_query(api_key, database_id, {
            "filter": {
                "property": "Date",
                "date": {"equals": target_date}
            }
        })
    except urllib.error.HTTPError as e:
        print(f"ERROR: Notion API error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    mode = "warn" if result.get("results") else "create"

    # Fetch last 7 rows to extract recent themes (avoid repetition)
    try:
        recent = notion_query(api_key, database_id, {
            "sorts": [{"property": "Date", "direction": "descending"}],
            "page_size": 7,
        })
    except urllib.error.HTTPError:
        recent = {"results": []}

    themes = []
    for page in recent.get("results", []):
        props = page.get("properties", {})
        rich_text = props.get("Theme", {}).get("rich_text", [])
        if rich_text:
            themes.append(rich_text[0].get("plain_text", ""))

    print(f"TARGET_DATE={target_date}")
    print(f"MODE={mode}")
    print(f"RECENT_THEMES={'|'.join(themes)}")


if __name__ == "__main__":
    main()
```

**Step 2: Make executable**

```bash
chmod +x skills/notion-language-lesson/scripts/nll-status.py
```

**Step 3: Smoke-test with missing env vars**

```bash
python3 skills/notion-language-lesson/scripts/nll-status.py
# Expected: ERROR: NOTION_API_KEY environment variable is not set (exit 1)
```

**Step 4: Smoke-test with invalid date**

```bash
NOTION_API_KEY=fake NOTION_DATABASE_ID=fake python3 skills/notion-language-lesson/scripts/nll-status.py not-a-date
# Expected: ERROR: Invalid date format: not-a-date. Use YYYY-MM-DD (exit 1)
```

**Step 5: Commit**

```bash
git add skills/notion-language-lesson/scripts/nll-status.py
git commit -m "feat: add nll-status.py for Notion DB pre-flight check"
```

---

### Task 3: Write `nll-push.py`

**Files:**
- Create: `skills/notion-language-lesson/scripts/nll-push.py`

**What it does:** Reads three temp markdown files (one per language lesson), creates a new Notion database row with all properties set, then appends the lesson content as nested toggle-heading blocks to the row's page body. Outputs `NOTION_URL=<url>` on success.

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
nll-push.py — Push generated lessons to a Notion database row.

Usage:
  python3 nll-push.py TARGET_DATE THEME --en EN_FILE --ja JA_FILE --es ES_FILE

Outputs:
  NOTION_URL=https://www.notion.so/...

Reads from environment:
  NOTION_API_KEY      — Notion integration secret
  NOTION_DATABASE_ID  — ID of the pre-created lessons database
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error


def get_env(key):
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: {key} environment variable is not set", file=sys.stderr)
        sys.exit(1)
    return val


def notion_request(api_key, method, path, payload=None):
    url = f"https://api.notion.com/v1{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        },
        method=method,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# --- Block builders ---

def rich_text(content, bold=False):
    t = {"type": "text", "text": {"content": content}}
    if bold:
        t["annotations"] = {"bold": True}
    return t


def paragraph_block(text):
    return {"type": "paragraph", "paragraph": {"rich_text": [rich_text(text)]}}


def heading_block(text, level=3):
    bt = f"heading_{level}"
    return {bt: {"rich_text": [rich_text(text)]}, "type": bt}


def bullet_block(text):
    return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [rich_text(text)]}}


def numbered_block(text):
    return {"type": "numbered_list_item", "numbered_list_item": {"rich_text": [rich_text(text)]}}


def divider_block():
    return {"type": "divider", "divider": {}}


def callout_block(text, emoji="📅"):
    return {
        "type": "callout",
        "callout": {
            "rich_text": [rich_text(text)],
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }


def toggle_heading_block(text, level=2, children=None):
    """Toggleable heading (is_toggleable supported in Notion API 2022-06-28+)."""
    bt = f"heading_{level}"
    return {
        "type": bt,
        bt: {
            "rich_text": [rich_text(text)],
            "is_toggleable": True,
            "children": children or [],
        },
    }


def toggle_block(text, children=None):
    """Plain toggle for answer keys — hidden by default."""
    return {
        "type": "toggle",
        "toggle": {
            "rich_text": [rich_text(text, bold=True)],
            "children": children or [],
        },
    }


# --- Markdown parser ---

def markdown_to_blocks(md_text):
    """
    Minimal markdown-to-Notion-blocks converter.

    Handles:
      ## Heading 2  → heading_2
      ### Heading 3 → heading_3
      - item        → bulleted_list_item
      1. item       → numbered_list_item
      ---           → divider
      blank lines   → skipped
      everything else → paragraph
    """
    blocks = []
    for line in md_text.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("## "):
            blocks.append(heading_block(stripped[3:], 2))
        elif stripped.startswith("### "):
            blocks.append(heading_block(stripped[4:], 3))
        elif stripped.startswith("#### "):
            blocks.append(heading_block(stripped[5:], 3))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append(bullet_block(stripped[2:]))
        elif stripped and stripped[0].isdigit() and ". " in stripped:
            idx = stripped.index(". ")
            blocks.append(numbered_block(stripped[idx + 2:]))
        elif stripped == "---":
            blocks.append(divider_block())
        elif stripped == "":
            pass
        else:
            blocks.append(paragraph_block(stripped))
    return blocks


def build_lesson_section(label, emoji, level_label, theme, content_md):
    """Wrap one lesson's markdown in a toggleable heading_2 block."""
    inner = [
        callout_block(f"Theme: {theme}  |  Level: {level_label}"),
        divider_block(),
    ] + markdown_to_blocks(content_md)
    return toggle_heading_block(f"{emoji} {label}", level=2, children=inner)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target_date", help="YYYY-MM-DD")
    parser.add_argument("theme", help="Unifying theme for this lesson")
    parser.add_argument("--en", required=True, help="Path to English lesson markdown file")
    parser.add_argument("--ja", required=True, help="Path to Japanese lesson markdown file")
    parser.add_argument("--es", required=True, help="Path to Spanish lesson markdown file")
    args = parser.parse_args()

    api_key = get_env("NOTION_API_KEY")
    database_id = get_env("NOTION_DATABASE_ID")

    def read_file(path):
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            return f.read().strip()

    en_md = read_file(args.en)
    ja_md = read_file(args.ja)
    es_md = read_file(args.es)

    # 1. Create database row with all properties
    try:
        page = notion_request(api_key, "POST", "/pages", {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": f"{args.target_date} — {args.theme}"}}]},
                "Date": {"date": {"start": args.target_date}},
                "Theme": {"rich_text": [{"text": {"content": args.theme}}]},
                "Languages": {"multi_select": [
                    {"name": "English"},
                    {"name": "Japanese"},
                    {"name": "Spanish"},
                ]},
                "English Reviewed": {"checkbox": False},
                "Japanese Reviewed": {"checkbox": False},
                "Spanish Reviewed": {"checkbox": False},
            },
        })
    except urllib.error.HTTPError as e:
        print(f"ERROR: Failed to create Notion page: {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    page_id = page["id"]
    page_url = page["url"]

    # 2. Build lesson blocks and append to page
    en_block = build_lesson_section("English Lesson", "🇺🇸", "Advanced / IELTS Band 7+", args.theme, en_md)
    ja_block = build_lesson_section("Japanese Lesson", "🇯🇵", "N1 / ネイティブ近接レベル", args.theme, ja_md)
    es_block = build_lesson_section("Spanish Lesson", "🇪🇸", "Intermediate B1–B2", args.theme, es_md)

    try:
        notion_request(api_key, "PATCH", f"/blocks/{page_id}/children", {
            "children": [en_block, ja_block, es_block],
        })
    except urllib.error.HTTPError as e:
        print(f"ERROR: Failed to append blocks: {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    print(f"NOTION_URL={page_url}")


if __name__ == "__main__":
    main()
```

**Step 2: Make executable**

```bash
chmod +x skills/notion-language-lesson/scripts/nll-push.py
```

**Step 3: Smoke-test missing args**

```bash
python3 skills/notion-language-lesson/scripts/nll-push.py
# Expected: error: the following arguments are required: target_date, theme, --en, --ja, --es
```

**Step 4: Smoke-test missing env**

```bash
python3 skills/notion-language-lesson/scripts/nll-push.py 2026-03-01 "Test" \
  --en /dev/null --ja /dev/null --es /dev/null
# Expected: ERROR: NOTION_API_KEY environment variable is not set (exit 1)
```

**Step 5: Commit**

```bash
git add skills/notion-language-lesson/scripts/nll-push.py
git commit -m "feat: add nll-push.py to push lessons to Notion"
```

---

### Task 4: Write `SKILL.md`

**Files:**
- Create: `skills/notion-language-lesson/SKILL.md`

**What it does:** Defines the skill. Mirrors the dll execution flow: env check → status → generate → write temp files → push to Notion → fallback to Obsidian → confirm.

**Step 1: Write the skill**

```markdown
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

```bash
# Write plain markdown — no ad-note blocks, no frontmatter
# Just the section content starting from the reading passage
```

- `/tmp/nll-en.md` — English lesson in markdown
- `/tmp/nll-ja.md` — Japanese lesson in markdown
- `/tmp/nll-es.md` — Spanish lesson in markdown

Each file should contain the lesson sections as plain markdown:

```
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
```

**Step 2: Verify frontmatter is valid YAML**

```bash
python3 -c "
import sys
content = open('skills/notion-language-lesson/SKILL.md').read()
fm = content.split('---')[1]
print('Frontmatter lines:', len(fm.strip().splitlines()))
print('OK')
"
```

Expected: prints `OK` with no errors.

**Step 3: Commit**

```bash
git add skills/notion-language-lesson/SKILL.md
git commit -m "feat: add notion-language-lesson SKILL.md"
```

---

### Task 5: Register skill in marketplace and bump versions

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `gemini-extension.json`
- Modify: `skills/notion-language-lesson/SKILL.md` (version already set to 1.0.0 in Task 4)

Per the Skill Edit Checklist in project memory, after adding a new skill:
1. Bump `metadata.version` in the new SKILL.md (already 1.0.0 — new skill, so this is correct)
2. Bump `version` in `gemini-extension.json` (currently `1.0.1` → `1.0.2`)
3. Bump `metadata.version` in `.claude-plugin/marketplace.json` (currently `1.0.1` → `1.0.2`)

**Step 1: Add skill to marketplace.json**

In `.claude-plugin/marketplace.json`, add `"./skills/notion-language-lesson"` to the `skills` array and bump the version:

```json
{
  "name": "harus-skills",
  "owner": {
    "name": "haru",
    "email": "azusachino@duck.com"
  },
  "metadata": {
    "description": "Custom Claude Code skills for productivity and learning",
    "version": "1.0.2"
  },
  "plugins": [
    {
      "name": "harus-skills",
      "description": "harus useful skills",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/mkmr",
        "./skills/next-session",
        "./skills/daily-language-lesson",
        "./skills/init-project",
        "./skills/session",
        "./skills/notion-language-lesson"
      ]
    }
  ]
}
```

**Step 2: Bump gemini-extension.json**

Find the `version` field and change `1.0.1` → `1.0.2`.

**Step 3: Verify JSON is valid**

```bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo "marketplace OK"
python3 -m json.tool gemini-extension.json > /dev/null && echo "gemini OK"
```

Expected: both print `OK`.

**Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json gemini-extension.json
git commit -m "chore: register notion-language-lesson skill, bump versions to 1.0.2"
```

---

### Task 6: Update `.env.example`

**Files:**
- Modify: `.env.example`

**Step 1: Add Notion variables**

Append to `.env.example`:

```bash
# Notion integration for notion-language-lesson (nll) skill
# Create an integration at https://www.notion.so/my-integrations
# and share your lessons database with it
# NOTION_API_KEY=secret_...
NOTION_API_KEY=your_notion_integration_secret

# The ID of your pre-created Notion lessons database
# Find it in the database URL: notion.so/<workspace>/<DATABASE_ID>?v=...
# NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=your_notion_database_id
```

**Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: add NOTION_API_KEY and NOTION_DATABASE_ID to .env.example"
```

---

### Task 7: Format and final verification

**Step 1: Run formatter (JSON/YAML only — never markdown)**

```bash
mise fmt
```

**Step 2: Run full check**

```bash
mise check
```

Expected: all checks pass.

**Step 3: Verify skill appears in list**

```bash
mise list-skills
```

Expected: `notion-language-lesson` (or `nll`) appears in output.

**Step 4: Final commit if fmt made changes**

```bash
git add -A
git status
# Only commit if there are changes from fmt
git commit -m "chore: format files after notion-language-lesson skill addition"
```

---

### Task 8: Integration test (live Notion API)

> Only run this if `NOTION_API_KEY` and `NOTION_DATABASE_ID` are available in your shell.

**Step 1: Run status check**

```bash
python3 skills/notion-language-lesson/scripts/nll-status.py
# Expected output (no existing row for today):
# TARGET_DATE=2026-03-01
# MODE=create
# RECENT_THEMES=...
```

**Step 2: Create test temp files**

```bash
echo "## 📖 Reading Passage\n\nTest passage.\n\n---\n\n## ✅ Answer Key\n\n1. Test answer." > /tmp/nll-en.md
cp /tmp/nll-en.md /tmp/nll-ja.md
cp /tmp/nll-en.md /tmp/nll-es.md
```

**Step 3: Push to Notion**

```bash
python3 skills/notion-language-lesson/scripts/nll-push.py \
  "$(date +%Y-%m-%d)-test" "Integration Test" \
  --en /tmp/nll-en.md --ja /tmp/nll-ja.md --es /tmp/nll-es.md
# Expected: NOTION_URL=https://www.notion.so/...
```

**Step 4: Verify in Notion**

Open the URL in browser. Confirm:
- Row appears in database with correct `Name`, `Date`, `Theme`, `Languages`, all checkboxes unchecked
- Page body has three toggleable headings (🇺🇸 English, 🇯🇵 Japanese, 🇪🇸 Spanish)
- Each toggle contains the callout + lesson sections

**Step 5: Clean up test row**

Delete the test row manually in Notion.
