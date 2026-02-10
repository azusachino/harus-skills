---
name: next-session
description: restore context from local files for next session
metadata:
  author: haru
  version: 1.0.0
---

always store context to current project local file.

# Next Session Skill

1. Read TODO.md and find the next unchecked session
2. Read the corresponding plan file if it exists
3. Create/update the session plan markdown (stored locally)
4. Implement all code, tutorials, checkpoints, and notes
5. Run lint/build/test and fix all errors until clean
6. Update TODO.md checkboxes and all tracking files
7. Summarize what was completed (with local tracking file)
8. Try to format files under this project (`make fmt` or `mise run fmt`)
