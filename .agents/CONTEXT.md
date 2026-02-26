## Agent Rules (Hard DO / DON'T)

- DO: Check Global Memory (`~/.agents/preferences/`, `~/.agents/facts/`) at session start for user preferences.
- DO: Update `.agents/CURRENT_TASK.md` before session end.
- DO: Sync any learned personal facts to Global Memory using `save_memory` and `~/.agents/facts/`.
- DON'T: Commit without user confirmation.

## Project Context (Internal)

- This is a repository of custom agent skills (Claude/Gemini).
- Memory Tier: Project (`.agents/`) is the source of truth for technical context. Global Tier (`~/.agents/`) is for user preferences.
