# Revise Skill + Plugin Version Alignment Tool — Design

Status: **Draft for review** · Date: 2026-06-24 · Author: haru (with Claude)

This document is a proposal for discussion. Nothing here is built yet. It covers two related asks: (1) a new `/revise` skill that lets agents persist work-experiences, findings, and wrong-approaches; (2) a Python tool (uv-managed) that keeps the single plugin version aligned across manifests.

## 1. Raw ideas (captured verbatim from the request)

> I might need add a revise skill, to let agents persist recent work-experiences, findings, wrong-approaches to places (memory, asobi, project-local).

> the issue will become, how the new session would ack this lesson. (the fallback shall be docs/xx/xx.md)

> recently even I directly called asobi with xxxx, I didn't know if agent tried to fetch project:session; how to debug it?

> also manage a py-tool to align xxx-plugin version plz, uv already inited.

Three distinct concerns surface from these notes: **persistence** (write the lesson somewhere durable), **recall** (a new session must actually surface the lesson — persistence alone is write-only), and **observability** (how do you know whether the agent even ran the asobi load step). Plus the orthogonal versioning chore.

## 2. Problem statement

We already have three overlapping persistence stores: harness file-memory (`~/.claude/.../memory/`), the asobi knowledge graph, and project-local files (`CLAUDE.md`, `docs/`). A learning captured today has no consistent home, and — more importantly — **no guaranteed path back into a future session's context**. The novel, genuinely-missing primitive is the **wrong-approach / dead-end**: neither memory nor asobi has a first-class "this was tried and failed, don't re-walk it" concept. An ADR records a *chosen* path; a pitfall records a *rejected* one. They are not the same.

## 3. Prior art — popular solutions

The dominant pattern in the literature is a **closed loop**: act → evaluate → write a natural-language lesson → store it in a (often bounded) buffer → inject relevant lessons back into future prompts.

- **Reflexion** is the canonical implementation: after a failed task the agent writes a verbal post-mortem and prepends it on the next attempt — no fine-tuning, just a text buffer of self-critiques. The "lesson" is typically a short, actionable, prefixed line kept in a bounded deque (e.g. last N lessons). This directly validates the `pitfall` idea: capture the failure as terse text, recall it before the next attempt. ([Reflexion overview / agent-memory survey](https://arxiv.org/pdf/2603.07670), [externalization review](https://arxiv.org/html/2604.08224v1))
- **Generative Agents** add a reflection *synthesis* step: raw observations accumulate, then get clustered and summarized into higher-order reflections; retrieval scores by recency × relevance × importance, not pure similarity. Lesson for us: don't just append — periodically consolidate (asobi's 50-obs cap + consolidation rule already encodes this). ([survey](https://arxiv.org/pdf/2603.07670))
- **Reflect on successes too, not only failures** — a known Reflexion extension reinforces effective strategies alongside dead ends. This maps to our three inputs: work-experiences and findings are the "what worked" half; pitfalls are the "what failed" half.
- **Production memory systems** (mem0, A-Mem, Zep, MemGPT) provide the storage/retrieval substrate. A noted tradeoff: graph memory (mem0, Zep) gives structure but predefined schemas can limit adaptability — relevant because asobi *is* a graph. We mitigate by keeping the pitfall schema minimal (a handful of obs keys) and leaning on semantic `query` for recall. ([A-Mem](https://arxiv.org/pdf/2502.12110), [agent-memory survey](https://arxiv.org/pdf/2603.07670))

**Takeaway:** our design is a deliberate, small instance of the Reflexion loop, with asobi as the persistent episodic store and `asobi query` as the recency/relevance retriever. The risk every paper flags — variable self-evaluation quality — we accept; lessons are advisory context, not gospel.

For the **version tool**, the established family is `bumpversion → bump2version → bump-my-version`. Only **bump-my-version** is actively maintained, configures from `pyproject.toml`, validates config via Pydantic, and supports multiple replacements across heterogeneous files (JSON, TOML, Markdown frontmatter) from a single `current_version`. `release-please`/`changesets` solve a *different* problem (commit-driven automated releases in CI) and are heavier than needed here. ([bump-my-version](https://github.com/callowayproject/bump-my-version), [bump2version, deprecated](https://github.com/c4urself/bump2version))

## 4. Decisions already taken (in discussion)

| Question | Decision |
| --- | --- |
| Where does revise live? | **Standalone `/revise` skill** (not an asobi subcommand) |
| How to model wrong-approaches? | **New `pitfall` entity** (`[project]:pitfall:<slug>`) |
| Which stores does revise write? | **asobi primary**; file-memory stays harness-managed; **project-local markdown fallback** when asobi is absent |
| Fallback path | **`docs/lessons/`** (`pitfalls.md` + `learnings.md`) |
| Scope of first pass | **Skill + recall wiring into asobi** (`start` + `dispatch`); SessionStart hook handled separately |
| Version tool | **bump-my-version**, configured in `pyproject.toml` |

## 5. Proposed design — `/revise` skill

### 5.1 Purpose and boundary vs `/asobi end`

`/asobi end` captures *where am I* — session continuity (objective/status/next). `/revise` captures *what did I learn* — durable lessons, especially negative results. They are complementary: `/revise` can fire mid-session after a meaningful chunk; `/asobi end` fires at wrap-up. Keeping them separate is what justifies a standalone skill rather than overloading `end`.

### 5.2 Flow

1. **Detect asobi** — `command -v asobi`. Present → graph path; absent → `docs/lessons/` fallback path.
2. **Classify** the learning: work-experience / finding / wrong-approach.
3. **Dedup first** — `asobi search "<topic>"`. A repeat hit gets an appended `seen-again: YYYY-MM-DD` obs, never a duplicate entity.
4. **Route** (table below).
5. **Confirm** — one line: what was persisted and where.

### 5.3 Routing

| Input | Destination | Mechanism |
| --- | --- | --- |
| work-experience (how a thing was actually done) | `[repo-basename]` project entity | `asobi obs` — convention/pattern learned |
| finding (non-obvious fact / gotcha) | project entity, or a `decision` entity if it's a choice | `asobi obs` / ADR |
| wrong-approach | **new `[project]:pitfall:<slug>`** | see 5.4 |

### 5.4 The `pitfall` entity (new primitive)

```bash
asobi new "[project]:pitfall:<slug>" "concept"
asobi truth "[project]:pitfall:<slug>" status active          # active | resolved
asobi obs  "[project]:pitfall:<slug>" "tried: <approach attempted>"
asobi obs  "[project]:pitfall:<slug>" "why-it-failed: <root cause / symptom>"
asobi obs  "[project]:pitfall:<slug>" "do-instead: <approach that worked, or 'open'>"
asobi obs  "[project]:pitfall:<slug>" "date: YYYY-MM-DD"
asobi link "[project]:[epic]:task-N" "[project]:pitfall:<slug>" "depends_on"
```

- `status` is a **truth** so it's readable from a cheap `search` (Reflexion-style bounded recall — scan active pitfalls without loading every obs).
- A pitfall is **not** a `decision`: a decision is a chosen path; a pitfall is a rejected one. Separate type keeps `query "why X"` (decisions) distinct from `query "how to X"` (pitfalls surface as warnings).
- When the dead end is later solved, flip `status` to `resolved` and fill `do-instead` — the success half of the Reflexion loop.

### 5.5 Fallback — `docs/lessons/` (asobi absent)

- `docs/lessons/pitfalls.md` — append a dated `### <slug>` block with **Tried / Why it failed / Do instead**.
- `docs/lessons/learnings.md` — append work-experiences + findings.
- Both repo-tracked (PR-reviewable) and stable-pathed. Header note: "Migrate into asobi once installed" — but **no auto-sync** (kept simple, per decision).

### 5.6 Closing the loop — recall wiring (the crux)

Persistence without recall is write-only — this is the part that makes `/revise` worth building. It ships with edits to the asobi skill, not just a new file:

- **`/asobi start`** gains a step: `asobi search "[project]:pitfall" --where status=active` → report `"N active pitfalls: <titles>"`. Cheap (truths + counts), and the printed line is *also* the proof that recall ran.
- **`/asobi tasks dispatch`** brief adds `asobi query "<task title>"` so any linked pitfall reaches the *working* agent inline — at the exact moment before it would re-walk the dead end.
- **Relations** (`pitfall ←depends_on task`) mean following the active epic naturally pulls its pitfalls.

## 6. Observability — "did the agent actually fetch `project:session`?"

The honest constraint: **asobi reads leave no trace**, and a probabilistic agent can't be *forced* to run a command. Three levels, weakest → strongest:

1. **Output contract (cheap, today).** The start ritual *must* emit `"Session resumed. Last task: X. Next: Y."`. No banner ⇒ it didn't load. Human-visible, but relies on the agent obeying.
2. **Wrapper log (the actual debug tool).** A shim named `asobi` earlier in `$PATH` that tees every invocation to `~/.asobi/access.log` then `exec`s the real binary. `tail ~/.asobi/access.log` gives ground truth on exactly which commands ran — answers "did it fetch the session" with certainty. Use when you need to debug a specific suspicion.
3. **SessionStart hook (the real fix).** A `SessionStart` hook in `settings.json` runs `asobi show … [project]:session` itself and injects the output into context. Load becomes **harness-deterministic**, not agent-discretionary — the question disappears. The whole problem exists only because `start` is currently a *skill instruction* (agent runs it) rather than a *hook* (harness runs it).

**Recommendation:** ship (3) for guaranteed loading + (2) as the on-demand debug shim; (1) stays as the human confirmation line. (3) is out of scope for the first pass (touches `settings.json`, handled via the `update-config` skill) but should be a fast follow.

## 7. Proposed design — plugin version alignment tool

### 7.1 Today

One universal `harus-skills` version (currently `3.0.0`) must stay identical across four spots: `.claude-plugin/marketplace.json` (`metadata.version` **and** `plugins[0].version`), `gemini-extension.json` (`version`), `.codex-plugin/plugin.json` (`version`). Per-skill `SKILL.md` `metadata.version` are independent (currently `2.0.0`). `make verify` already *checks* alignment but does not *set* it — drift is still possible by hand.

### 7.2 Proposal — bump-my-version via uv

Add `bump-my-version` as a dev dependency (uv is already initialized; `pyproject.toml` present at `version = "0.1.0"`). Configure `[tool.bumpversion]` with `current_version` as the single source and one `[[tool.bumpversion.files]]` per manifest spot, using a JSON-path-anchored `search`/`replace` so only the version line changes. Drive it through Make:

```makefile
bump-version:   ## Bump universal plugin version (use V=major|minor|patch)
	uv run bump-my-version bump $(V)
```

- `uv run bump-my-version show-bump` previews major/minor/patch targets before committing.
- `make verify`'s existing alignment check becomes the post-condition guard — if bump-my-version touched all four, `verify` passes.
- **Open scope:** whether the tool also bumps per-skill `SKILL.md` versions. Since those are independent and per-skill, recommend **keeping them manual** (or a separate `bump-skill SKILL=asobi` target) rather than forcing them onto the universal cadence.

### 7.3 Alternative considered

A bespoke ~30-line Python script using `json`/`tomllib` + write-back. Rejected as the default: reinvents a maintained tool, and the personal-defaults "simple over clever / jq for JSON" guidance points to a declarative config over hand-rolled file surgery. Keep as a fallback only if bump-my-version's heterogeneous-file handling proves awkward for the Markdown frontmatter case.

## 8. Repo plumbing (when built)

- New `skills/revise/SKILL.md`; skills auto-discover (no manifest listing).
- Version-bump rule applies: bump revise's own `metadata.version` + the universal version in all four manifest spots (ideally *via the new tool* — nice dogfooding).
- Update `CLAUDE.md`: skill table, invocation table, agent-behavior note (when to `/revise`).
- asobi `SKILL.md`: add the `pitfall` entity to the Entity Reference, and the recall steps in `start` + `dispatch`.
- `pyproject.toml`: add `bump-my-version` dev dep + `[tool.bumpversion]`; `Makefile`: `bump-version` target.

## 9. Open questions for reviewers

1. **Pitfall granularity** — one entity per dead end, or a single rolling `[project]:pitfalls` entity with one obs per dead end (Reflexion's bounded buffer)? Per-entity gives relations + per-item status; rolling is lighter but loses linkage. Current lean: per-entity.
2. **Should `/revise` also reflect on successes** explicitly (a `win:`/`do-this` note on the project entity), or is that already covered by work-experiences? Literature says successes are worth reinforcing.
3. **SessionStart hook now or later** — accept the deterministic-load hook in the first pass, or ship skill+recall first and add the hook once the recall path is proven?
4. **Per-skill version automation** — leave `SKILL.md` versions manual, or fold them into the tool?
5. **Cross-machine pitfalls** — pitfalls are project-scoped today. Any case for a global `pitfall` (e.g. a tooling gotcha that recurs across repos), which would push it toward file-memory instead?

## Sources

- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers](https://arxiv.org/pdf/2603.07670)
- [Externalization in LLM Agents: Memory, Skills, Protocols and Harness Engineering](https://arxiv.org/html/2604.08224v1)
- [A-Mem: Agentic Memory for LLM Agents](https://arxiv.org/pdf/2502.12110)
- [bump-my-version](https://github.com/callowayproject/bump-my-version)
- [bump2version (deprecated, points to bump-my-version)](https://github.com/c4urself/bump2version)
