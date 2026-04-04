import sys
import os
from unittest.mock import MagicMock

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../skills/lang-skills/notion-language-lesson/scripts"))

# Mock environment before importing
os.environ["NOTION_API_KEY"] = "fake"
os.environ["NOTION_DATABASE_ID"] = "fake"

import nll_push

def test_markdown_to_blocks_basic():
    md = "## Section\n- Item 1\n- Item 2\n\nSome text with **bold** and `code`."
    blocks = nll_push.markdown_to_blocks(md)
    
    assert len(blocks) == 4
    assert blocks[0]["type"] == "heading_2"
    assert blocks[1]["type"] == "bulleted_list_item"
    assert blocks[2]["type"] == "bulleted_list_item"
    assert blocks[3]["type"] == "paragraph"
    # Check for bold and code annotations in rich_text
    rich_text = blocks[3]["paragraph"]["rich_text"]
    assert any(rt.get("annotations", {}).get("bold") for rt in rich_text)
    assert any(rt.get("annotations", {}).get("code") for rt in rich_text)

def test_markdown_to_blocks_answer_key():
    md = "## ✅ Answer Key\n1. Answer 1\n2. Answer 2"
    blocks = nll_push.markdown_to_blocks(md)
    
    assert len(blocks) == 1
    assert blocks[0]["type"] == "toggle"
    # Toggle block has children directly in this parser
    assert len(blocks[0]["toggle"]["children"]) == 2
