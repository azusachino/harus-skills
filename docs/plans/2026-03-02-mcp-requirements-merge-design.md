# MCP Requirements Merge Design

## Overview
Refine the `init-project` and `session` skills to better handle global user requirements from the MCP memory server, specifically hardcoding known rules like markdown linting exclusions and dynamically merging MCP facts into project templates.

## 1. init-project Skill
- **Hardcoded Rules:** During initialization, generate a `.markdownlint-cli2.yaml` that explicitly ignores `.agents/` and `docs/plans/`.
- **MCP Full Merge:** If the `@modelcontextprotocol/server-memory` MCP is available, invoke `read_graph()` and dynamically merge the global facts into the generated files:
  - `CodingStyle` facts → merge into `AGENTS.md` (Coding Conventions) and `.agents/config.yaml`.
  - `ToolPreferences` facts → merge into `AGENTS.md` (Build, Run & Test) and `.agents/config.yaml`.
  - `UserPreferences` & `Standard` facts → merge into `.agents/CONTEXT.md` (Agent Rules) and `AGENTS.md` (Quality Standards).
- **Template Instructions:** Instruct the agent generating these files to incorporate the fetched facts naturally into the template structure rather than just blindly appending them.

## 2. session Skill
- **New Category:** Expand the list of global MCP category entities to include `Standard` (for cross-project requirements, system rules, and global configurations).
- **`/session start`:** Update the start protocol to explicitly fetch `Standard` entities alongside the existing categories.
- **`/session end`:** Instruct the agent to categorize newly discovered cross-project rules as `Standard` when persisting them to the MCP global memory.
