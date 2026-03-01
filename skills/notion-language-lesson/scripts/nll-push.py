#!/usr/bin/env python3
"""
nll-push.py — Push generated lessons to a Notion database row.

Usage:
  python3 nll-push.py TARGET_DATE THEME --en EN_FILE --ja JA_FILE --es ES_FILE
                      [--replace PAGE_ID]

  --replace PAGE_ID  Archive this existing page before creating a new one
                     (used when overwriting a lesson that already exists)

Outputs:
  NOTION_URL=https://www.notion.so/...

Reads from environment:
  NOTION_API_KEY      — Notion integration secret
  NOTION_DATABASE_ID  — ID of the pre-created lessons database
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, List, Any


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: {key} environment variable is not set", file=sys.stderr)
        sys.exit(1)
    return val


def notion_request(
    api_key: str, method: str, path: str, payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
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


def archive_page(api_key: str, page_id: str) -> None:
    """Archive (soft-delete) a Notion page. Best-effort — never raises."""
    try:
        notion_request(api_key, "PATCH", f"/pages/{page_id}", {"archived": True})
    except Exception:
        pass


# --- Inline markdown parser ---

_INLINE_PATTERN = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")


def parse_inline(text: str) -> List[Dict[str, Any]]:
    """
    Parse **bold** and `code` inline markers into Notion rich_text objects.
    Plain text segments are returned as-is.
    """
    parts = []
    for seg in _INLINE_PATTERN.split(text):
        if not seg:
            continue
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            parts.append(
                {
                    "type": "text",
                    "text": {"content": seg[2:-2]},
                    "annotations": {"bold": True},
                }
            )
        elif seg.startswith("`") and seg.endswith("`") and len(seg) > 2:
            parts.append(
                {
                    "type": "text",
                    "text": {"content": seg[1:-1]},
                    "annotations": {"code": True},
                }
            )
        else:
            parts.append({"type": "text", "text": {"content": seg}})
    return parts or [{"type": "text", "text": {"content": text}}]


def plain_rich_text(content: str) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": {"content": content}}]


# --- Block builders ---


def paragraph_block(text: str) -> Dict[str, Any]:
    return {"type": "paragraph", "paragraph": {"rich_text": parse_inline(text)}}


def heading_block(text: str, level: int = 3) -> Dict[str, Any]:
    bt = f"heading_{level}"
    return {bt: {"rich_text": plain_rich_text(text)}, "type": bt}


def bullet_block(text: str) -> Dict[str, Any]:
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": parse_inline(text)},
    }


def numbered_block(text: str) -> Dict[str, Any]:
    return {
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": parse_inline(text)},
    }


def divider_block() -> Dict[str, Any]:
    return {"type": "divider", "divider": {}}


def callout_block(text: str, emoji: str = "📅") -> Dict[str, Any]:
    return {
        "type": "callout",
        "callout": {
            "rich_text": plain_rich_text(text),
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }


def toggle_heading_block(text: str, level: int = 2) -> Dict[str, Any]:
    """Toggleable section heading. Children must be appended in a separate API call."""
    bt = f"heading_{level}"
    return {
        "type": bt,
        bt: {
            "rich_text": plain_rich_text(text),
            "is_toggleable": True,
        },
    }


def answer_key_toggle(children: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap answer key content in a plain toggle block (hidden by default)."""
    return {
        "type": "toggle",
        "toggle": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "✅ Answer Key"},
                    "annotations": {"bold": True},
                }
            ],
            "children": children,
        },
    }


# --- Markdown parser ---


def markdown_to_blocks(md_text: str) -> List[Dict[str, Any]]:
    """
    Convert lesson markdown to Notion blocks.

    Special handling:
    - Lines after '## ✅ Answer Key' are collected and wrapped in a toggle block
      so answer keys are hidden by default.
    - **bold** and `code` in text lines are converted to annotated rich_text.
    """
    blocks = []
    answer_key_lines = []
    in_answer_key = False

    for line in md_text.splitlines():
        stripped = line.rstrip()

        # Detect answer key section — collect remaining lines into toggle
        if stripped.startswith("## ✅"):
            in_answer_key = True
            continue

        if in_answer_key:
            answer_key_lines.append(stripped)
            continue

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

    # Build answer key toggle if we found that section
    if answer_key_lines:
        ak_blocks = []
        for line in answer_key_lines:
            if not line:
                continue
            if line.startswith("### "):
                ak_blocks.append(heading_block(line[4:], 3))
            elif line and line[0].isdigit() and ". " in line:
                idx = line.index(". ")
                ak_blocks.append(numbered_block(line[idx + 2 :]))
            elif line.startswith("- "):
                ak_blocks.append(bullet_block(line[2:]))
            else:
                ak_blocks.append(paragraph_block(line))
        if ak_blocks:
            blocks.append(answer_key_toggle(ak_blocks))

    return blocks


def build_lesson_inner(
    level_label: str, theme: str, content_md: str
) -> List[Dict[str, Any]]:
    """Build the inner content blocks for one language lesson."""
    return [
        callout_block(f"Theme: {theme}  |  Level: {level_label}"),
        divider_block(),
    ] + markdown_to_blocks(content_md)


def main() -> None:
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
    parser.add_argument(
        "--replace",
        metavar="PAGE_ID",
        help="Archive this existing page before creating new one (overwrite mode)",
    )
    args = parser.parse_args()

    api_key = get_env("NOTION_API_KEY")
    database_id = get_env("NOTION_DATABASE_ID")

    def read_file(path: str) -> str:
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            return f.read().strip()

    en_md = read_file(args.en)
    ja_md = read_file(args.ja)
    es_md = read_file(args.es)

    # Archive existing page if overwriting
    if args.replace:
        try:
            notion_request(
                api_key, "PATCH", f"/pages/{args.replace}", {"archived": True}
            )
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"ERROR: Failed to archive existing page: {body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            print(
                f"ERROR: Failed to archive existing page: {e.reason}", file=sys.stderr
            )
            sys.exit(1)

    # Step 1: Create database row with all properties
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
                    "Notes": {"rich_text": []},
                },
            },
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: Failed to create Notion page: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Failed to create Notion page: {e.reason}", file=sys.stderr)
        sys.exit(1)

    page_id = page["id"]
    page_url = page["url"]

    # Step 2: Append three toggle heading blocks (no children — Notion API constraint)
    lessons = [
        ("🇺🇸 English Lesson", "Advanced / IELTS Band 7+", en_md),
        ("🇯🇵 Japanese Lesson", "N1 / ネイティブ近接レベル", ja_md),
        ("🇪🇸 Spanish Lesson", "Intermediate B1–B2", es_md),
    ]
    headings = [toggle_heading_block(label) for label, _, _ in lessons]

    try:
        result = notion_request(
            api_key,
            "PATCH",
            f"/blocks/{page_id}/children",
            {"children": headings},
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: Failed to create section headings: {body}", file=sys.stderr)
        archive_page(api_key, page_id)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Failed to create section headings: {e.reason}", file=sys.stderr)
        archive_page(api_key, page_id)
        sys.exit(1)

    heading_ids = [block["id"] for block in result.get("results", [])]
    if len(heading_ids) != 3:
        print("ERROR: Unexpected number of heading blocks created", file=sys.stderr)
        archive_page(api_key, page_id)
        sys.exit(1)

    # Step 3: Append lesson content as children of each heading block
    for heading_id, (label, level_label, md) in zip(heading_ids, lessons):
        inner_blocks = build_lesson_inner(level_label, args.theme, md)
        try:
            notion_request(
                api_key,
                "PATCH",
                f"/blocks/{heading_id}/children",
                {"children": inner_blocks},
            )
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"ERROR: Failed to append {label} content: {body}", file=sys.stderr)
            archive_page(api_key, page_id)
            sys.exit(1)
        except urllib.error.URLError as e:
            print(
                f"ERROR: Failed to append {label} content: {e.reason}", file=sys.stderr
            )
            archive_page(api_key, page_id)
            sys.exit(1)

    print(f"NOTION_URL={page_url}")


if __name__ == "__main__":
    main()
