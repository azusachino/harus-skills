# harus-skills

Three Markdown skills shared across agent runtimes: `asobi` for durable work state, `revise` for evidence-backed lessons, and `toolbelt` for terminal tool choices. Skill behavior lives in `skills/<name>/SKILL.md`; this file governs contributions to the repository.

## Working principles

- Read the affected skill, its callers and the current repository state before editing. Current user and workspace instructions take precedence over recalled preferences and portable skill defaults.
- Keep each skill focused on its distinct job. Include guidance that changes a decision; remove repeated policy, cached inventories, and generic advice. Preserve useful recipes and concrete safety boundaries.
- Resolve routine uncertainty through repository evidence, installed CLI help, and safe checks. Continue authorized work; ask when the unresolved choice changes scope, authority, or the risk to user data.
- Reuse existing tools and targets. Define proportionate verification; distinguish structural validation from evidence that an agent follows the guidance correctly.
- Use independent subagents when useful and permitted by the current workspace. Worktrees and parallel sessions remain explicit opt-in.
- Preserve unrelated edits and partial staging. Use conventional commits without emojis, stage named files, and run `make check` before committing. Pushes, PRs, and other remote mutations require explicit authorization.

## Skill ownership

| Skill | Source | Boundary |
| --- | --- | --- |
| `asobi` | `skills/asobi/SKILL.md` | Graph scope, session/task state, recall, skill selection and requested maintenance |
| `revise` | `skills/revise/SKILL.md` | Durable lessons with evidence; session status stays with Asobi |
| `toolbelt` | `skills/toolbelt/SKILL.md` | Tool selection and recipes; project configuration owns the actual toolchain |

Use the Asobi skill for session start and closeout. Confirm graph scope before writes: ancestor configuration can apply inside a nested repository. Capture lessons when they would change future behavior; deduplicate and retain their evidence limits.

## Packaging and versions

The flat `skills/` tree is the authored source. `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and `gemini-extension.json` package the same content. Keep historical decisions in `docs/adr/`; supersede an accepted ADR with a new one rather than rewriting history.

After changing a `skills/*/SKILL.md`, bump that skill's independent `metadata.version` and the universal plugin version in the same commit. Run `make sync-version V=x.y.z` to align all manifest versions, then `make validate`. Read the actual files for current versions; prose documentation must not cache them.

Installed copies belong to their installer. In a workspace with declarative Asobi selection, update `asobi.toml` and reconcile through `asobi skills sync`; edit this repository's source skills here, not a consumer's installed snapshot.

## Development

`Makefile` owns the available tasks. This repository currently supplies a Nix devShell and Nix-based CI; keep using that verified path until the planned Mise migration updates both. Mise is the preferred project pinning approach for new tooling; Nix/Home Manager remains the global machine toolchain.

```bash
nix develop
make check
make validate
```

JSON/YAML uses Prettier with 2-space indentation. Markdown is reviewed as prose: do not run Prettier on it or manually wrap prose lines.

The current `make install-hooks` assumes `.git/` is a directory and restages files; it is unsuitable for submodules and partial staging. Run `make check` explicitly until that target is repaired. `make validate` checks manifest JSON and version alignment, not installation in every agent host.

The current audit and remediation plan live in harus-kb under `docs/runbooks/audits/2026-09/2026-09-07-harus-skills-guidance-audit.md` and `docs/runbooks/plans/2026-09/2026-09-07-refresh-harus-skills.md` in the workstation repository. Operational commands remain owned here.
