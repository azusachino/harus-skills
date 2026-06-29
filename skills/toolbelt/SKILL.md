---
name: toolbelt
description: Reference for haru's preferred modern CLI tools — when and how to use eza/bat/fd/ripgrep/sd, xh, dasel, procs, doggo, hexyl, duckdb/psql/sqlx-cli, hyperfine/oha. Invoke when a task involves searching files, editing text, HTTP/API calls, data/SQL work, DNS or process debugging, hex inspection, or benchmarking, and you want the idiomatic tool + flags instead of the classic Unix default.
metadata:
  author: haru
  version: 2.0.1
user-invokable: true
---

# Toolbelt Skill

haru's machines (managed by `harus-nix` Home Manager) ship a curated set of modern CLIs. **Prefer these over the classic Unix tools by default** — fall back to the classic only when the modern tool is genuinely unavailable.

## Table of Contents
- [Substitution table (always-on)](#substitution-table-always-on)
- [Tooling discipline (carried from global defaults)](#tooling-discipline-carried-from-global-defaults)
- [Runtimes & package managers](#runtimes--package-managers)
- [Search & navigate](#search--navigate)
- [Edit text](#edit-text)
- [HTTP / API debugging](#http--api-debugging)
- [Data & SQL](#data--sql)
- [Debug & inspect](#debug--inspect)
- [Benchmark](#benchmark)
- [When NOT to substitute](#when-not-to-substitute)

This skill is **self-contained** — it carries both the substitution rules and the usage recipes so it works on any device, even one whose global `~/.claude/CLAUDE.md` isn't synced or differs. Treat it as the portable source of truth; if the local global config disagrees, the local config wins for that machine, but these defaults travel with you.

Rule of thumb: classic tools for piping inside scripts that must be portable; modern tools for interactive/agent work where clarity and ergonomics win.

## Substitution table (always-on)

Reach for the right-hand tool by default; fall back to the classic only when the modern one is absent.

| Instead of           | Use                                     | For                             |
| -------------------- | --------------------------------------- | ------------------------------- |
| `ls` / `cat` / `du`  | `eza` / `bat` / `dust`                  | listing, viewing, disk usage    |
| `grep` / `find`      | `ripgrep` (`rg`) / `fd`                 | search                          |
| `sed` (substitute)   | `sd`                                    | find & replace                  |
| `ps` / `dig` / `xxd` | `procs` / `doggo` / `hexyl`             | processes, DNS, hex             |
| `curl` (API testing) | `xh`                                    | HTTP requests                   |
| `jq` for non-JSON    | `dasel`                                 | YAML/TOML/XML/CSV query+convert |
| `jq` for YAML        | `yq`                                    | YAML query + convert            |
| `wc -l` (code count) | `tokei`                                 | code statistics (LOC)           |
| ad-hoc regex design  | `grex`                                  | generate regular expressions    |
| `tmux`               | `zellij`                                | terminal workspace multiplexer  |
| ad-hoc SQL           | `duckdb`, `psql` (postgres), `sqlx-cli` | data + migrations               |
| benchmarking         | `hyperfine` (CLI), `oha` (HTTP)         | perf checks                     |
| `python` / `pip` / `pipx` | `uv` / `uvx`                       | Python runtime, deps, tools     |
| `node` / `npm` / `npx`    | `bun` / `bunx`                     | JS/TS runtime, deps, tools      |

## Tooling discipline (carried from global defaults)

These hold across all of haru's projects and are restated here so the skill stands alone:

- **Nix-first** — tools come from the project devShell (`nix develop`); use `mise` only for language runtimes, not general tooling.
- **`make` is the task runner** — reference `make <target>` everywhere; `make check` before commits, `make validate` before PRs (hook-enforced).
- **JSON → `jq`** — always `jq` for JSON processing; never `python3 -c` or inline Python. Reach for `dasel` the moment the format isn't JSON.
- **Conventional commits, 2-space config indent, no emojis** — per global CodingStyle.

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

## Edit text

- **`sd`** — find & replace, literal-friendly, real regex (no `sed` escaping pain):
  - `sd 'foo' 'bar' file.txt` (in-place, no `-i` needed)
  - `sd -p 'foo' 'bar' file.txt` (preview diff, don't write)
  - `sd '(\w+)@(\w+)' '$2.$1' file` (capture groups with `$1`)
  - Reach for `sed` only for stream edits in portable scripts.

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
  - Use `jq` for pure-JSON pipelines (it's still the default for JSON); reach for `dasel` the moment the format isn't JSON.
- **`yq`** — query/update YAML documents:
  - `yq '.services.web.ports[0]' docker-compose.yml`
  - `yq -P '.foo = "bar"' file.yaml` (pretty print YAML)
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
- **`zellij`** — modern terminal workspace and multiplexer (replaces tmux):
  - `zellij` (starts a new session)
  - `zellij options --theme dracula`

## Benchmark

- **`hyperfine`** — CLI command benchmarking with stats:
  - `hyperfine 'rg foo' 'grep -r foo .'` (compare), `--warmup 3`.
- **`oha`** — HTTP load (see above).

## When NOT to substitute

- Portable shell scripts that may run on minimal/other machines → stick to POSIX (`grep`, `sed`, `find`, `curl`) so they don't depend on this toolbelt.
- Pure-JSON pipelines → `jq` remains the default (per global CLAUDE.md).
- If a tool isn't installed (`command -v <tool>` fails), fall back gracefully.
