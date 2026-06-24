#!/usr/bin/env python3
"""Sync the universal harus-skills plugin version across its manifests.

The canonical version is ``metadata.version`` in ``.claude-plugin/marketplace.json``.
It must stay identical in three counterparts (the second marketplace spot plus the
gemini and codex manifests). This script reads the source and propagates it, or sets
an explicit version everywhere, or checks alignment for CI.

Usage:
    uv run python tools/sync_version.py            # propagate source version to counterparts
    uv run python tools/sync_version.py 3.1.0      # set every spot to 3.1.0
    uv run python tools/sync_version.py --check    # verify alignment, exit 1 on mismatch

Per-skill SKILL.md versions are intentionally out of scope: they are independent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Every target spot is a JSON ``"version": "..."`` value; replacing in raw text
# (rather than re-dumping the parsed object) preserves the repo's prettier layout.
VERSION_RE = re.compile(r'("version"\s*:\s*")[^"]*(")')

ROOT = Path(__file__).resolve().parents[1]

# (relative path, [key-paths]) — a key-path is a tuple of dict keys / list indices.
TARGETS: list[tuple[str, list[tuple]]] = [
    (".claude-plugin/marketplace.json", [("metadata", "version"), ("plugins", 0, "version")]),
    ("gemini-extension.json", [("version",)]),
    (".codex-plugin/plugin.json", [("version",)]),
]

# Canonical source of truth.
SOURCE_FILE, SOURCE_PATH = ".claude-plugin/marketplace.json", ("metadata", "version")


def _get(data, path: tuple):
    for key in path:
        data = data[key]
    return data


def _load(rel: str):
    return json.loads((ROOT / rel).read_text())


def read_source_version() -> str:
    return _get(_load(SOURCE_FILE), SOURCE_PATH)


def iter_spots():
    """Yield (rel, path, current_value) for every version spot."""
    for rel, paths in TARGETS:
        data = _load(rel)
        for path in paths:
            yield rel, path, _get(data, path)


def check() -> int:
    source = read_source_version()
    mismatches = [(rel, path, val) for rel, path, val in iter_spots() if val != source]
    if mismatches:
        print(f"Version mismatch (source {SOURCE_FILE}={source}):", file=sys.stderr)
        for rel, path, val in mismatches:
            print(f"  {rel} {'.'.join(map(str, path))} = {val}", file=sys.stderr)
        return 1
    print(f"All version spots aligned at {source}.")
    return 0


def apply(version: str) -> int:
    changed = False
    for rel, paths in TARGETS:
        data = _load(rel)
        for path in paths:
            if _get(data, path) != version:
                print(f"  {rel} {'.'.join(map(str, path))} -> {version}")
        # Replace in raw text to keep formatting; every "version" key is a target.
        original = (ROOT / rel).read_text()
        updated = VERSION_RE.sub(rf"\g<1>{version}\g<2>", original)
        if updated != original:
            (ROOT / rel).write_text(updated)
            changed = True
    if not changed:
        print(f"Already at {version}; nothing to do.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("version", nargs="?", help="explicit version to set everywhere (e.g. 3.1.0)")
    group.add_argument("--check", action="store_true", help="verify alignment without writing")
    args = parser.parse_args(argv)

    if args.check:
        return check()
    return apply(args.version or read_source_version())


if __name__ == "__main__":
    raise SystemExit(main())
