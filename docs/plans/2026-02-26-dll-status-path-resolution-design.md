# Design: Daily Language Lesson Path Resolution

## Overview

The `dll-status.sh` script currently defaults to a path that might not exist or might be based on the git repository root. The user wants it to default to `$(pwd)/lessons` with a year subfolder.

## Goals

- Default the output path to `$(pwd)/lessons/$YYYY` when `VAULT_PATH` is not set.
- Maintain existing behavior for when `VAULT_PATH` IS set.
- Ensure the output directory is created.

## Component Changes

### `skills/daily-language-lesson/scripts/dll-status.sh`

- **Resolve output path**:
  - `TARGET_DATE` is arg 1 or today's date (`YYYY-MM-DD`).
  - `YYYY` is extracted from `TARGET_DATE`.
  - `OUTPUT_DIR` is set to `$VAULT_PATH/$YYYY` if `VAULT_PATH` is defined.
  - Otherwise, `OUTPUT_DIR` is set to `$(pwd)/lessons/$YYYY`.
  - `OUTPUT_PATH` is set to `$OUTPUT_DIR/$TARGET_DATE.md`.
  - `mkdir -p "$OUTPUT_DIR"` is called.

## Architecture

```bash
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
```

## Testing

- **Reproduction**: Run `dll-status.sh` and observe its current output.
- **Verification**: Run `dll-status.sh` after the change and verify it outputs `OUTPUT_PATH` correctly to `$(pwd)/lessons/$YYYY/$TARGET_DATE.md`.
- **Vault Check**: Set `VAULT_PATH` environment variable and verify it respects it.
