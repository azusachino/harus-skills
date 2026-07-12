# 1. Pure-markdown skills, no runtime code

- Status: Accepted
- Date: 2026-07-12

## Context

Skills must run in any Claude Code environment — and, increasingly, in other agent runtimes (Codex, Antigravity). We want minimal setup friction for consumers and maximal portability, and the repository should stay reviewable without a toolchain.

## Decision

Every skill is pure markdown: a `SKILL.md` with YAML frontmatter plus a markdown body of execution instructions the agent follows. There is no build step and no runtime code beyond what the agent and shell execute while following those instructions. Bundled assets (config templates, reference docs) are also plain files, never executables.

## Consequences

- Maximal portability and cross-agent interoperability; a skill is just text, so any compliant agent can load it.
- No build, no CI compilation, trivial diff review — the whole repo is content.
- The trade-off: a skill can only do what the agent + shell can already do. Logic-heavy behavior is expressed as instructions, not as code, which is less precise than a real program. When a capability genuinely needs code, it belongs in a separate tool (e.g. the `asobi` CLI), not inside a skill.
