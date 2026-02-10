# Project Design

## Design Goals

- Reusable, shareable Claude Code skills
- Minimal setup friction for consumers
- Agent-agnostic infrastructure patterns (via init-project)

## Key Decisions

| Decision     | Choice                | Rationale                          |
| ------------ | --------------------- | ---------------------------------- |
| Skill format | Agent Skills Standard | Interoperability across agents     |
| Task runner  | mise                  | Language-agnostic, declarative     |
| Formatter    | prettier              | Wide format support (md/json/yaml) |
| Linter       | markdownlint-cli2     | CLI-friendly, configurable         |
| Distribution | Plugin marketplace    | Native Claude Code integration     |

## Trade-offs

- **No runtime code**: limits what skills can do, but maximizes portability
- **Single plugin**: simpler config vs. granular install control
- **mise dependency**: requires mise installed, but provides reproducible tooling
