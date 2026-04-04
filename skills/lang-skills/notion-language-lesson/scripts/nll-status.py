#!/usr/bin/env python3
"""
nll-status.py — Pre-flight check for the notion-language-lesson skill.

Usage: python3 nll-status.py [TARGET_DATE]
  TARGET_DATE: optional YYYY-MM-DD; defaults to today

Outputs KEY=value lines:
  TARGET_DATE=YYYY-MM-DD
  MODE=create|warn
  EXISTING_PAGE_ID=<id>  (non-empty only when MODE=warn)
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
from typing import Dict, Any


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: {key} environment variable is not set", file=sys.stderr)
        sys.exit(1)
    return val


def notion_query(
    api_key: str, database_id: str, payload: Dict[str, Any], max_retries: int = 5
) -> Dict[str, Any]:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    data = json.dumps(payload).encode()

    for i in range(max_retries):
        try:
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
        except urllib.error.HTTPError as e:
            if e.code in [429, 502, 503, 504] and i < max_retries - 1:
                import time
                import random

                wait = (2**i) + random.random()
                print(f"Retrying in {wait:.2f}s... ({e.code})", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
    raise Exception(f"Max retries exceeded for {url}")


def main() -> None:
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        try:
            datetime.date.fromisoformat(target_date)
        except ValueError:
            print(
                f"ERROR: Invalid date format: {target_date}. Use YYYY-MM-DD",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        target_date = datetime.date.today().isoformat()

    api_key = get_env("NOTION_API_KEY")
    database_id = get_env("NOTION_DATABASE_ID")

    # Check if a row already exists for target date
    try:
        result = notion_query(
            api_key,
            database_id,
            {"filter": {"property": "Date", "date": {"equals": target_date}}},
        )
    except urllib.error.HTTPError as e:
        print(f"ERROR: Notion API error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    existing_page_id = ""
    results = result.get("results", [])
    if results:
        mode = "warn"
        existing_page_id = results[0].get("id", "")
    else:
        mode = "create"

    # Fetch last 7 rows to extract recent themes (avoid repetition)
    try:
        recent = notion_query(
            api_key,
            database_id,
            {
                "sorts": [{"property": "Date", "direction": "descending"}],
                "page_size": 7,
            },
        )
    except (urllib.error.HTTPError, urllib.error.URLError):
        recent = {"results": []}

    themes = []
    for page in recent.get("results", []):
        props = page.get("properties", {})
        rich_text = props.get("Theme", {}).get("rich_text", [])
        if rich_text:
            themes.append(rich_text[0].get("plain_text", ""))

    print(f"TARGET_DATE={target_date}")
    print(f"MODE={mode}")
    print(f"EXISTING_PAGE_ID={existing_page_id}")
    print(f"RECENT_THEMES={'|'.join(themes)}")


if __name__ == "__main__":
    main()
