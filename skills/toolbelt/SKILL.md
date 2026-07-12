---
name: toolbelt
description: Reference for haru's preferred modern CLI tools — when and how to use eza/bat/fd/ripgrep/sd/ast-grep, xh, dasel, procs, doggo, hexyl, duckdb/psql/sqlx-cli, hyperfine/oha, difftastic, typos. Invoke when a task involves searching files, editing/refactoring code, HTTP/API calls, data/SQL work, DNS or process debugging, hex inspection, diffing, or benchmarking, and you want the idiomatic tool + flags instead of the classic Unix default.
metadata:
  author: haru
  version: 2.1.0
user-invokable: true
---

# Toolbelt Skill

haru's machines (managed by `harus-nix` Home Manager) ship a curated set of modern CLIs. **Prefer these over the classic Unix tools by default** — fall back to the classic only when the modern tool is genuinely unavailable.

## Table of Contents
- [Stop-and-ask rule (hard stop)](#stop-and-ask-rule-hard-stop)
- [Substitution table (always-on)](#substitution-table-always-on)
- [Tooling discipline (carried from global defaults)](#tooling-discipline-carried-from-global-defaults)
- [Runtimes & package managers](#runtimes--package-managers)
- [Search & navigate](#search--navigate)
- [Edit text](#edit-text)
- [HTTP / API debugging](#http--api-debugging)
- [Data & SQL](#data--sql)
- [Debug & inspect](#debug--inspect)
- [Benchmark](#benchmark)
- [Domain & infra tools (know these exist)](#domain--infra-tools-know-these-exist)
- [When NOT to substitute](#when-not-to-substitute)

This skill is **self-contained** — it carries both the substitution rules and the usage recipes so it works on any device, even one whose global `~/.claude/CLAUDE.md` isn't synced or differs. Treat it as the portable source of truth; if the local global config disagrees, the local config wins for that machine, but these defaults travel with you.

Rule of thumb: classic tools for piping inside scripts that must be portable; modern tools for interactive/agent work where clarity and ergonomics win.

## Stop-and-ask rule (hard stop)

**On any ambiguity — an error you don't understand, a missing tool, a flag behaving oddly, state that contradicts your assumptions — STOP and ask.** Never improvise a fallback, retry with guessed flags, or work around the block; one clear question beats three speculative attempts. This is the global **stop-and-ask / fail-fast** default (canonical in `UserPreferences`). The sole exception: a tool that's literally not installed (`command -v` fails) may fall back gracefully — anything else ambiguous is a stop.

## Substitution table (always-on)

Reach for the right-hand tool by default; fall back to the classic only when the modern one is absent.

| Instead of           | Use                                     | For                             |
| -------------------- | --------------------------------------- | ------------------------------- |
| `ls` / `cat` / `du`  | `eza` / `bat` / `dust`                  | listing, viewing, disk usage    |
| `grep` / `find`      | `ripgrep` (`rg`) / `fd`                 | text/file search                |
| `grep` for code structure | `ast-grep` (`sg`)                  | AST-aware search & rewrite      |
| `sed` (substitute)   | `sd`                                    | find & replace                  |
| `git diff`           | `difftastic` (`difft`)                  | syntax-aware diffs              |
| `ps` / `dig` / `xxd` | `procs` / `doggo` / `hexyl`             | processes, DNS, hex             |
| `curl` (API testing) | `xh`                                    | HTTP requests                   |
| `jq` for non-JSON    | `dasel`                                 | YAML/TOML/XML/CSV query+convert |
| `wc -l` (code count) | `tokei`                                 | code statistics (LOC)           |
| ad-hoc regex design  | `grex`                                  | generate regular expressions    |
| spell-check source   | `typos`                                 | typo linting in code + docs     |
| ad-hoc SQL           | `duckdb`, `psql` (postgres), `sqlx-cli` | data + migrations               |
| benchmarking         | `hyperfine` (CLI), `oha` (HTTP)         | perf checks                     |
| `python` / `pip` / `pipx` | `uv` / `uvx`                       | Python runtime, deps, tools     |
| `node` / `npm` / `npx`    | `bun` / `bunx`                     | JS/TS runtime, deps, tools      |

## Tooling discipline (carried from global defaults)

These hold across all of haru's projects and are restated here so the skill stands alone:

- **Nix-first** — tools come from the project devShell (`nix develop`); use `mise` only for language runtimes, not general tooling. To run a project-pinned runtime/tool through mise, use `mise x -- <tool>` (alias `mise exec`) — it resolves the version from the repo's `.mise.toml`.
- **`make` is the task runner** — reference `make <target>` everywhere; `make check` before commits, `make validate` before PRs (hook-enforced).
- **JSON → `jq`** — always `jq` for JSON processing; never `python3 -c` or inline Python. Reach for `dasel` the moment the format isn't JSON.
- **Conventional commits, 2-space config indent** — per global CodingStyle. Emojis are welcome (commits, prose, docs).

## Runtimes & package managers

Prefer the fast modern runner over the legacy one by default — they're drop-in for the common paths and far faster.

- **`uv`** — Python runtime + dependency + project manager (replaces `python`/`pip`/`venv`/`pipx`/`poetry`):
  - `uv run script.py` (auto-resolves deps), `uv run pytest` (run a tool in the project env)
  - `uv add httpx` / `uv remove httpx` (manage `pyproject.toml`), `uv sync` (install lockfile)
  - `uv venv` (create env), `uv pip install -r req.txt` (pip-compatible shim)
  - **`uvx`** — run a Python CLI tool one-off without installing: `uvx ruff check`, `uvx ruff@0.6 format`.
- **`bun`** — JS/TS runtime + package manager + bundler (replaces `node`/`npm`/`npx`/`yarn`/`pnpm`):
  - `bun run script.ts` (runs TS directly, no compile step), `bun test`
  - `bun install` (fast install), `bun add zod` / `bun remove zod`
  - **`bunx`** — run a package one-off without installing: `bunx prettier --write .`, `bunx tsx file.ts`.

Caveats: stick to `python3`/`node` + `pip`/`npm` when a project's toolchain or CI pins them, when a native addon/wheel isn't yet `bun`/`uv`-compatible, or inside a Nix devShell that already provides the interpreter (per Nix-first, `mise` handles runtimes there). For everything ad-hoc and interactive, reach for `uv`/`bun` first.

## Search & navigate

| Task       | Tool             | Idiom                                                         |
| ---------- | ---------------- | ------------------------------------------------------------- |
| Find text  | `ripgrep` (`rg`) | `rg -n "pattern"`, `rg -t rust foo`, `rg -l pat` (files only) |
| Find files | `fd`             | `fd -e nix`, `fd -t f name`, `fd -H` (include hidden)         |
| List dir   | `eza`            | `eza -la --git`, `eza --tree --level=2`                       |
| View file  | `bat`            | `bat file`, `bat -p` (plain, no decorations for piping)       |
| Disk usage | `dust`           | `dust -d 2` (depth 2)                                         |
| Jump dirs  | `zoxide`         | `z proj` after visiting once                                  |

Prefer `rg`/`fd` over `grep -r`/`find` — faster, respects `.gitignore`, sane defaults. When piping `bat` output, add `-p` to strip line numbers/borders.

- **`ast-grep` (`sg`)** — structural, syntax-aware code search & rewrite (matches by AST, not regex — immune to formatting/whitespace):
  - `sg run -p 'console.log($A)' -l ts` (find every `console.log(...)` call, any argument)
  - `sg run -p 'foo($$$ARGS)' --rewrite 'bar($$$ARGS)' -l py -U` (rename a call, preserving all args; `-U` applies in place)
  - Reach for `sg` over `rg` the moment the pattern is about code *shape* (a call, an import, a JSX element) rather than literal text — no brittle regex, no false hits inside strings/comments.

## Edit text

- **`sd`** — find & replace, literal-friendly, real regex (no `sed` escaping pain):
  - `sd 'foo' 'bar' file.txt` (in-place, no `-i` needed)
  - `sd -p 'foo' 'bar' file.txt` (preview diff, don't write)
  - `sd '(\w+)@(\w+)' '$2.$1' file` (capture groups with `$1`)
  - Reach for `sed` only for stream edits in portable scripts.
  - For *code-structure* rewrites (rename a call, swap an API) use `ast-grep --rewrite` instead — it edits by AST, not text, so formatting and string/comment matches can't trip it up.

## HTTP / API debugging

- **`xh`** — httpie-style client, faster than `curl` for hand-driven requests:
  - `xh get https://api.example.com/users` (auto-pretty JSON)
  - `xh post api.local/login name=haru pass=secret` (JSON body from `k=v`)
  - `xh -f post url field=val` (form), `xh --headers get url` (headers only)
  - `xh get url Authorization:"Bearer $TOK"` (header with `:`)
  - Use `curl` in scripts / when exact wire control or `--resolve` is needed.
- **`oha`** — load testing: `oha -n 1000 -c 50 https://api.local/health`.

## Data & SQL

- **`dasel`** — one tool to query/convert JSON/YAML/TOML/XML/CSV:
  - `dasel -f config.yaml '.services.web.port'`
  - `dasel -f data.json -r json -w yaml` (convert JSON→YAML)
  - `dasel put -f config.yaml -v 8080 '.services.web.port'` (edit YAML/TOML/etc. in place)
  - Use `jq` for pure-JSON pipelines (it's still the default for JSON); reach for `dasel` the moment the format isn't JSON. `dasel` handles YAML query *and* edit — it's the one tool for non-JSON structured data here.
- **`tokei`** — count lines of code quickly:
  - `tokei .` (recursive code statistics by language)
- **`duckdb`** — fast analytical SQL over files, no server:
  - `duckdb -c "select * from 'data.csv' limit 5"`
  - `duckdb -c "select count(*) from read_parquet('*.parquet')"`
- **`miller`** (`mlr`) — CSV/TSV/JSON record processing:
  - `mlr --csv cut -f a,b then sort -nr b data.csv`
- **`psql`** (from `postgresql`) — Postgres client:
  - `psql "$DATABASE_URL" -c '\dt'`, `psql -h host -U user db`
- **`sqlx-cli`** — Rust SQL toolkit / migrations:
  - `sqlx database create`, `sqlx migrate add <name>`, `sqlx migrate run`
  - `sqlx migrate revert`, `cargo sqlx prepare` (offline query cache)

## Debug & inspect

- **`procs`** — modern `ps`:
  - `procs` (all), `procs nginx` (filter by name), `procs --tree`
  - `procs --sortd cpu` (sort by CPU desc), shows ports/TTY/user.
- **`doggo`** — modern `dig` for DNS debugging:
  - `doggo example.com`, `doggo MX example.com`
  - `doggo example.com @1.1.1.1` (specific resolver), `--json` for parsing.
- **`hexyl`** — colored hex viewer:
  - `hexyl file.bin`, `hexyl -n 64 file` (first 64 bytes), inspect encodings/headers.
- **`tailspin`** (`tspin`) — auto-highlight logs: `tspin app.log` or `cmd | tspin`.
- **`btop`** — interactive system monitor.
- **`grex`** — generate regular expressions from user-provided test cases:
  - `grex a b c` (returns `^[a-c]$`)
  - `grex -d -w -p email@example.com` (generate with digits, words, non-space)
- **`typos`** — fast source-code spell checker (skips code identifiers sensibly):
  - `typos` (check the tree), `typos -w` (auto-fix), `typos path/to/file`
  - Good as a pre-commit gate and before shipping docs; low false-positive rate.
- **`difftastic` (`difft`)** — structural, syntax-aware diff (compares ASTs, ignores pure reflow):
  - `difft old.rs new.rs` (standalone), or wire it into git: `GIT_EXTERNAL_DIFF=difft git diff`
  - Reach for it when a plain-text diff is noisy because indentation/wrapping changed but the code didn't.

Terminal multiplexing: `tmux`.

## Benchmark

- **`hyperfine`** — CLI command benchmarking with stats:
  - `hyperfine 'rg foo' 'grep -r foo .'` (compare), `--warmup 3`.
- **`oha`** — HTTP load (see above).

## Domain & infra tools (know these exist)

Not substitutions — these are the specialised tools harus-nix already provisions. Reach for them by name instead of hand-rolling or asking the user to install something; they're on the machine.

| Domain | Tools | Reach for it when |
| --- | --- | --- |
| **Nix workflow** | `nh` (ergonomic nix/home-manager wrapper), `nom` (`nix-output-monitor`) | rebuilding a config, watching a nix build's progress |
| **Kubernetes** | `k9s` (TUI), `kubectl`, `stern` (multi-pod log tail) | inspecting/driving a cluster, tailing pod logs |
| **Cloud & sync** | `rclone` | syncing to/from cloud/object storage |
| **Containers (Linux)** | `podman`, `buildah`, `skopeo` | building/running/inspecting OCI images (rootless, daemonless) |
| **Secrets** | `sops`, `age` | encrypting/decrypting secrets in the repo |
| **Watch & run** | `watchexec` | re-run a command on file changes (tests, builds) |
| **Lint & format** | `shellcheck`, `shfmt`, `yamlfmt`, `prettier`, `markdownlint-cli2`, `typos`, `pre-commit` | linting/formatting shell, YAML, JS/TS, Markdown; spell-check; hook setup |
| **Lang tooling** | `golangci-lint`, `ruff`/`ty` (Python), `cargo-update`/`-sweep`/`-cache` | project-local linting, Rust cargo maintenance |
| **Archives & docs** | `ouch` (compress/extract), `typst` (doc compiler) | packing/unpacking archives, typesetting |
| **Shell & nav** | `navi` (interactive cheat sheet), `fzf`, `zoxide`, `yazi` (file manager) | fuzzy-finding, cheat lookups, browsing files |
| **Runtime pinning** | `mise` (per-project versions via `.mise.toml`, run with `mise x -- <tool>`), `rustup` (Rust toolchains) | a project pins a language version; switching Rust toolchains |

If a task needs a tool not on this list or in the tables above, apply the stop-and-ask rule — confirm with the user before installing anything.

## When NOT to substitute

- Portable shell scripts that may run on minimal/other machines → stick to POSIX (`grep`, `sed`, `find`, `curl`) so they don't depend on this toolbelt.
- Pure-JSON pipelines → `jq` remains the default (per global CLAUDE.md).
- If a tool isn't installed (`command -v <tool>` fails), fall back gracefully.
