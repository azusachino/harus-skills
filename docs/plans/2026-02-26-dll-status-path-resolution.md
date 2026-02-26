# Daily Language Lesson Path Resolution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Default the `dll-status.sh` output path to `$(pwd)/lessons/$YYYY` when `VAULT_PATH` is not set.

**Architecture:** Modify the path resolution logic in `dll-status.sh` to use `$(pwd)/lessons/$YYYY` as the default output directory.

**Tech Stack:** Bash

---

### Task 1: Verify current behavior

**Files:**
- Read: `skills/daily-language-lesson/scripts/dll-status.sh`

**Step 1: Run the script and observe output**

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh
```

**Step 2: Note the current `OUTPUT_PATH`**

Expected: `OUTPUT_PATH` should be in the git repo root or current directory, but likely NOT include the year subfolder if `VAULT_PATH` is unset.

---

### Task 2: Modify path resolution in `dll-status.sh`

**Files:**
- Modify: `skills/daily-language-lesson/scripts/dll-status.sh`

**Step 1: Apply the changes**

```bash
# Resolve output path
if [ -n "${VAULT_PATH:-}" ]; then
  OUTPUT_DIR="$VAULT_PATH/$YYYY"
else
  OUTPUT_DIR="$(pwd)/lessons/$YYYY"
fi
OUTPUT_PATH="$OUTPUT_DIR/$TARGET_DATE.md"
```

**Step 2: Verify the change locally**

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh
```
Expected: `OUTPUT_PATH` should be `$(pwd)/lessons/2026/2026-02-26.md` (assuming today is 2026-02-26).

**Step 3: Verify with `VAULT_PATH` set**

```bash
VAULT_PATH=/tmp/vault bash skills/daily-language-lesson/scripts/dll-status.sh
```
Expected: `OUTPUT_PATH` should be `/tmp/vault/2026/2026-02-26.md`.

**Step 4: Commit**

```bash
git add skills/daily-language-lesson/scripts/dll-status.sh
git commit -m "fix(dll): default output path to cwd/lessons/YYYY"
```

---

### Task 3: Verify overall skill behavior

**Files:**
- Read: `skills/daily-language-lesson/SKILL.md`

**Step 1: Check if other parts of the skill need update**

The skill uses `bash "<BASE_DIR>/scripts/dll-status.sh" [ARGUMENT]` and parses the output. Since we modified the script to output the correct `OUTPUT_PATH`, it should just work.

**Step 2: Final manual verification**

Run the skill (if possible in this environment) or verify that the script indeed creates the directory and file in the expected location.

```bash
bash skills/daily-language-lesson/scripts/dll-status.sh 2026-01-01
ls -d lessons/2026
```
Expected: `lessons/2026` directory exists.
