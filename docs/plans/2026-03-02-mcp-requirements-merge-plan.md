# MCP Requirements Merge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refine `init-project` and `session` skills to handle global MCP memory requirements (`Standard` facts, markdown lint rules).

**Architecture:** Update the skill definitions (`SKILL.md`) in `skills/init-project` and `skills/session` to parse and merge the `Standard` category from the `@modelcontextprotocol/server-memory` graph.

**Tech Stack:** Markdown, Makefile (linting)

---

### Task 1: Update init-project Skill

**Files:**
- Modify: `skills/init-project/SKILL.md`

**Step 1: Run lint to verify baseline**
Run: `make lint`
Expected: No errors for markdown files.

**Step 2: Modify `init-project/SKILL.md` to add hardcoded `.markdownlint-cli2.yaml`**
In Phase 3 or Phase 5, add instructions to generate a `.markdownlint-cli2.yaml` file with the following content:
```yaml
ignores:
  - ".agents/**"
  - "docs/plans/**"
```

**Step 3: Modify `init-project/SKILL.md` for MCP Full Merge**
Update Phase 3 (where files are generated) to instruct the agent:
"If MCP `@modelcontextprotocol/server-memory` is available, call `read_graph()` first. Dynamically merge the retrieved global facts into the generated templates naturally:
- `CodingStyle` facts → merge into `AGENTS.md` (Coding Conventions) and `.agents/config.yaml`.
- `ToolPreferences` facts → merge into `AGENTS.md` (Build, Run & Test) and `.agents/config.yaml`.
- `UserPreferences` & `Standard` facts → merge into `.agents/CONTEXT.md` (Agent Rules) and `AGENTS.md` (Quality Standards)."

**Step 4: Run lint to verify changes**
Run: `make lint`
Expected: Passes with no errors.

**Step 5: Commit**
```bash
git add skills/init-project/SKILL.md
git commit -m "feat(init-project): add mcp requirements merge and markdownlint defaults"
```

### Task 2: Update session Skill

**Files:**
- Modify: `skills/session/SKILL.md`

**Step 1: Modify `session/SKILL.md` `Commands` section**
Update `/session start` step 1 to include `Standard` in the list of category entities loaded from MCP.
Update `/session end` step 2 to mention categorizing cross-project rules as `Standard`.

**Step 2: Modify `session/SKILL.md` `Category entities` table**
Add `Standard` to the markdown table under "Category entities (cross-project user facts)":
| `Standard` | Cross-project system requirements, global configurations, tool exclusions |

**Step 3: Run lint to verify changes**
Run: `make lint`
Expected: Passes with no errors.

**Step 4: Commit**
```bash
git add skills/session/SKILL.md
git commit -m "feat(session): add Standard category to mcp global memory"
```