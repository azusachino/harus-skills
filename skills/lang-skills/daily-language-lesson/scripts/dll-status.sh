#!/usr/bin/env bash
# dll-status.sh — Pre-flight check for the daily-language-lesson skill
#
# Usage: dll-status.sh [TARGET_DATE]
#   TARGET_DATE: optional YYYY-MM-DD; defaults to today
#
# Outputs KEY=value lines:
#   TARGET_DATE, YYYY, OUTPUT_PATH, MODE, RECENT_THEMES
#
# MODE values:
#   create — file does not exist
#   append — file exists but has no ## writing section
#   fill   — file exists with ## writing but all ad-note blocks are empty
#   warn   — file exists with real lesson content in ad-note blocks

set -euo pipefail

TARGET_DATE="${1:-$(date +%Y-%m-%d)}"
YYYY="${TARGET_DATE:0:4}"

# Resolve output path
if [ -n "${VAULT_PATH:-}" ]; then
  OUTPUT_DIR="$VAULT_PATH/$YYYY"
else
  OUTPUT_DIR="$(pwd)/lessons/$YYYY"
fi
OUTPUT_PATH="$OUTPUT_DIR/$TARGET_DATE.md"

mkdir -p "$OUTPUT_DIR"

# Detect MODE
if [ ! -f "$OUTPUT_PATH" ]; then
  MODE="create"
elif ! grep -q "^## writing" "$OUTPUT_PATH" 2>/dev/null; then
  MODE="append"
else
  # Check if any ad-note block contains real content (non-whitespace)
  HAS_CONTENT=$(awk '
    /^```ad-note/{in_block=1; content=""; next}
    in_block && /^```/{
      if (content ~ /[^[:space:]]/) { print "yes"; exit }
      in_block=0; next
    }
    in_block { content = content $0 "\n" }
  ' "$OUTPUT_PATH")

  if [ "$HAS_CONTENT" = "yes" ]; then
    MODE="warn"
  else
    MODE="fill"
  fi
fi

# Scan recent themes from last 7 lesson files with real content
SCAN_DIR="$OUTPUT_DIR"
RECENT_THEMES=""

if [ -d "$SCAN_DIR" ]; then
  THEMES=""
  while IFS= read -r f; do
    theme=$(grep -m 1 '\*\*Theme\*\*:' "$f" 2>/dev/null | sed 's/.*\*\*Theme\*\*: //')
    if [ -n "$theme" ]; then
      date_str=$(basename "$f" .md)
      if [ -n "$THEMES" ]; then
        THEMES="$THEMES | $date_str: $theme"
      else
        THEMES="$date_str: $theme"
      fi
    fi
  done < <(
    find "$SCAN_DIR" -maxdepth 1 -name '*.md' -type f ! -name "$TARGET_DATE.md" -print \
      | sort -r \
      | while IFS= read -r f; do
        size=$(wc -c <"$f" 2>/dev/null || echo 0)
        [ "$size" -gt 500 ] && echo "$f"
      done \
      | head -7
  )
  RECENT_THEMES="$THEMES"
fi

echo "TARGET_DATE=$TARGET_DATE"
echo "YYYY=$YYYY"
echo "OUTPUT_PATH=$OUTPUT_PATH"
echo "MODE=$MODE"
echo "RECENT_THEMES=$RECENT_THEMES"
