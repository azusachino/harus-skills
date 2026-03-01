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
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [rich_text(text)]},
    }


def numbered_block(text):
    return {
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [rich_text(text)]},
    }


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
            blocks.append(numbered_block(stripped[idx + 2 :]))
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
    parser.add_argument(
        "--en", required=True, help="Path to English lesson markdown file"
    )
    parser.add_argument(
        "--ja", required=True, help="Path to Japanese lesson markdown file"
    )
    parser.add_argument(
        "--es", required=True, help="Path to Spanish lesson markdown file"
    )
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
        page = notion_request(
            api_key,
            "POST",
            "/pages",
            {
                "parent": {"database_id": database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {"text": {"content": f"{args.target_date} — {args.theme}"}}
                        ]
                    },
                    "Date": {"date": {"start": args.target_date}},
                    "Theme": {"rich_text": [{"text": {"content": args.theme}}]},
                    "Languages": {
                        "multi_select": [
                            {"name": "English"},
                            {"name": "Japanese"},
                            {"name": "Spanish"},
                        ]
                    },
                    "English Reviewed": {"checkbox": False},
                    "Japanese Reviewed": {"checkbox": False},
                    "Spanish Reviewed": {"checkbox": False},
                },
            },
        )
    except urllib.error.HTTPError as e:
        print(
            f"ERROR: Failed to create Notion page: {e.code}: {e.read().decode()}",
            file=sys.stderr,
        )
        sys.exit(1)

    page_id = page["id"]
    page_url = page["url"]

    # 2. Build lesson blocks and append to page
    en_block = build_lesson_section(
        "English Lesson", "🇺🇸", "Advanced / IELTS Band 7+", args.theme, en_md
    )
    ja_block = build_lesson_section(
        "Japanese Lesson", "🇯🇵", "N1 / ネイティブ近接レベル", args.theme, ja_md
    )
    es_block = build_lesson_section(
        "Spanish Lesson", "🇪🇸", "Intermediate B1–B2", args.theme, es_md
    )

    try:
        notion_request(
            api_key,
            "PATCH",
            f"/blocks/{page_id}/children",
            {
                "children": [en_block, ja_block, es_block],
            },
        )
    except urllib.error.HTTPError as e:
        print(
            f"ERROR: Failed to append blocks: {e.code}: {e.read().decode()}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"NOTION_URL={page_url}")


if __name__ == "__main__":
    main()
