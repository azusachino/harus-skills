# Requirements

## Functional Requirements

- [x] Skills follow Agent Skills Standard (SKILL.md with YAML frontmatter)
- [x] Plugin marketplace registration via `.claude-plugin/marketplace.json`
- [x] Daily language lesson generation (English, Japanese, Spanish)
- [x] Merge request creation from feature branches
- [x] Project initialization with agent infrastructure
- [ ] Skill discovery and browsing

## Non-Functional Requirements

- Portability: skills work in any Claude Code environment
- Simplicity: no build step, no dependencies beyond mise-managed tools
- Quality: all files formatted and linted before commit

## Constraints

- Skills must be pure markdown (SKILL.md format)
- No runtime code execution outside of skill instructions
- Generated content (lessons/) must not be committed
