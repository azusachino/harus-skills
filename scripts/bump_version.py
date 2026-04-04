#!/usr/bin/env python3
import json
import sys
import re
from pathlib import Path


def bump_version(new_version):
    # Update gemini-extension.json
    gemini_path = Path("gemini-extension.json")
    if gemini_path.exists():
        data = json.loads(gemini_path.read_text())
        data["version"] = new_version
        gemini_path.write_text(json.dumps(data, indent=2) + "\n")

    # Update marketplace.json
    market_path = Path(".claude-plugin/marketplace.json")
    if market_path.exists():
        data = json.loads(market_path.read_text())
        data["metadata"]["version"] = new_version
        market_path.write_text(json.dumps(data, indent=2) + "\n")

    # Update all SKILL.md files
    for skill_file in Path("skills").rglob("SKILL.md"):
        content = skill_file.read_text()
        # Update version in YAML frontmatter
        content = re.sub(r"(version:)\s*.*", f"\\1 {new_version}", content)
        skill_file.write_text(content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bump_version.py <version>")
        sys.exit(1)
    bump_version(sys.argv[1])
