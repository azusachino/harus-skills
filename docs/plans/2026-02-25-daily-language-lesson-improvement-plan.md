# daily-language-lesson Improvement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Add vault integration, fix the date bug, add Spanish writing exercise,
and add mise tasks so lessons generate directly into the Obsidian vault.

**Architecture:** All changes are in 4 files: SKILL.md (vault-aware execution
logic), README.md (full rewrite), mise.toml (2 new tasks), and a new
.env.example. No code is generated — this is prompt/config/doc engineering.
Verification is done with `mise check` after each step.

**Tech Stack:** mise tasks, SKILL.md (markdown prompt), Obsidian ad-note
callout format, bash (mise task bodies)

---

## Task 1: Add `.env` to `.gitignore` and create `.env.example`

**Files:**

- Modify: `.gitignore`
- Create: `.env.example`

**Step 1: Add `.env` to `.gitignore`**

Open `.gitignore`. After the `lessons/` line at the top, add:

```gitignore
# Local vault configuration
.env
```

**Step 2: Create `.env.example`**

Create `.env.example` with this exact content:

```bash
# Path to your Obsidian vault's daily notes directory
# Lessons will be written to $VAULT_PATH/YYYY/YYYY-MM-DD.md
# If not set, lessons fall back to lessons/YYYY-MM-DD.md in this repo
VAULT_PATH=/path/to/your/vault/journal/daily
```

### Step 3: Verify

Run: `mise run verify`
Expected: `✅ Repository structure is valid!`

### Step 4: Commit

```bash
git add .gitignore .env.example
git commit -m "chore: add VAULT_PATH env config and .env.example"
```

---

## Task 2: Add `lesson` and `lesson-date` tasks to `mise.toml`

**Files:**

- Modify: `mise.toml`

### Step 1: Append the two tasks

At the end of `mise.toml`, append:

```toml
[tasks.lesson]
description = "Generate today's language lesson to vault (or lessons/ fallback)"
run = "claude '/lesson'"

[tasks."lesson-date"]
description = "Generate a lesson for a specific date. Usage: DATE=2026-03-01 mise run lesson-date"
run = "claude '/lesson ${DATE}'"
```

### Step 2: Verify formatting

Run: `mise run fmt-check`
Expected: `All files are properly formatted.`

If it fails, run: `mise run fmt` to auto-fix, then re-check.

### Step 3: Commit

```bash
git add mise.toml
git commit -m "feat: add lesson and lesson-date mise tasks"
```

---

## Task 3: Rewrite `README.md`

**Files:**

- Modify: `skills/daily-language-lesson/README.md`

### Step 1: Replace the entire file with the following content

````markdown
# Daily Language Lesson Skill

Generate daily language learning lessons for English (advanced), Japanese (N1),
and Spanish (B1–B2), saved directly to your Obsidian vault or a local
`lessons/` folder.

## Features

- **English** at IELTS Band 7+ / advanced level: academic writing, nuanced
  idioms, rhetorical devices
- **Japanese** at N1 / near-native: advanced kanji, keigo, literary and
  journalistic expressions
- **Spanish** at B1–B2: past/future tenses, subjunctive intro, opinion
  expression

Each lesson includes:

- Reading passage at the appropriate level
- Vocabulary with definitions, passage examples, and usage
- Comprehension questions with answer key
- Grammar point with explanation and practice exercises
- Writing exercise (Spanish)

## Setup

### Vault integration (recommended)

Create a `.env` file in the repo root (gitignored):

```env
VAULT_PATH=/path/to/your/vault/journal/daily
```

Lessons will be written to `$VAULT_PATH/YYYY/YYYY-MM-DD.md` — the year
subfolder is created automatically. If the file already exists (Obsidian
pre-creates daily notes), the lesson sections are appended.

If `VAULT_PATH` is not set, lessons fall back to `lessons/YYYY-MM-DD.md` in
this repo.

## Usage

### Via Claude Code skill

```bash
/daily-language-lesson       # today's lesson
/lesson                      # alias
/dll                         # alias
/lesson 2026-03-01           # specific date
```

### Via mise

```bash
mise run lesson                       # today's lesson
DATE=2026-03-01 mise run lesson-date  # specific date
```

## Output format

Each lesson is written as a single markdown file with three sections using
Obsidian `ad-note` callout blocks:

```markdown
## writing

\`\`\`ad-note
# English Lesson — YYYY-MM-DD
...
\`\`\`

## japanese

\`\`\`ad-note
# 日本語レッスン — YYYY-MM-DD
...
\`\`\`

## spanish

\`\`\`ad-note
# Lección de Español — YYYY-MM-DD
...
\`\`\`
```

## Daily workflow

1. Run `mise run lesson` each morning
2. Open your vault — today's daily note will have the three lesson sections
3. Complete the exercises and check your answers
4. Vary: use `/lesson 2026-03-05` to prepare future lessons in advance

## Tips

- Topics rotate across 8 domains (tech, crypto, music, psychology, books,
  history, science, daily life) and link all three languages to a shared theme
- The skill checks the last 7 lessons to avoid repeating recent topics
- If today's lesson already exists in the file, the skill will ask before
  overwriting
- Spanish content is designed to be encouraging for B1–B2 learners
- Japanese includes furigana references where helpful

````

### Step 2: Verify lint

Run: `mise run lint`
Expected: no errors.

If lint errors appear, run `mise run lint-fix` and review the diff.

### Step 3: Commit

```bash
git add skills/daily-language-lesson/README.md
git commit -m "docs: rewrite daily-language-lesson README for vault integration"
```

---

## Task 4: Update `SKILL.md` — frontmatter and metadata

**Files:**

- Modify: `skills/daily-language-lesson/SKILL.md`

This task and Task 5 together replace the full SKILL.md. Do them sequentially.

### Step 1: Update the YAML frontmatter block (lines 1–9)

Replace the existing frontmatter:

```yaml
---
name: daily-language-lesson
description: Generate comprehensive daily language learning lessons for English (native), Japanese (native), and Spanish (entry level) with reading passages, vocabulary, comprehension questions, and grammar practice
metadata:
  author: haru
  version: 1.0.1
  aliases: ["dll", "lesson"]
disable-model-invocation: true
---
```

With:

```yaml
---
name: daily-language-lesson
description: >-
  Generate daily language lessons for English (advanced), Japanese (N1), and
  Spanish (B1–B2) with reading passages, vocabulary, comprehension questions,
  grammar practice, and writing exercises — saved directly to your Obsidian
  vault.
metadata:
  author: haru
  version: 2.0.0
  aliases: ["dll", "lesson"]
disable-model-invocation: true
---
```

### Step 2: Verify

Run: `mise run verify`
Expected: `✅ Repository structure is valid!`

---

## Task 5: Update `SKILL.md` — execution logic

**Files:**

- Modify: `skills/daily-language-lesson/SKILL.md`

### Step 1: Replace the full body of SKILL.md (everything after frontmatter)

Replace everything from line 10 onward with:

````markdown
# Daily Language Lesson Generator

You are a language learning assistant that generates comprehensive, engaging
daily lessons across three languages. Lessons are personalized around the
learner's interests: backend engineering, crypto/finance, piano/music,
reading/books, psychology, history, and culture.

## Language Levels

- **Japanese**: N1 / near-native (advanced kanji, keigo, literary and
  journalistic expressions, subtle nuance)
- **English**: Advanced / IELTS Band 7+ (academic writing, professional
  discourse, nuanced idioms, rhetorical devices)
- **Spanish**: Intermediate B1–B2 (past and future tenses, subjunctive
  introduction, complex sentence structures, opinion expression)

## Topic Rotation

Rotate through a diverse set of engaging topics. Draw from:

- **Technology & Engineering**: distributed systems, AI ethics, open source,
  programming paradigms
- **Crypto & Finance**: blockchain concepts, market psychology, DeFi, economic
  history
- **Music & Piano**: music theory, composers, practice methodology, instrument
  history
- **Psychology & Behavior**: cognitive biases, decision-making, motivation,
  mental models
- **Books & Literature**: book reviews, author backgrounds, narrative
  techniques, philosophy of reading
- **History & Culture**: civilizations, historical turning points, cultural
  anthropology
- **Science & Nature**: biology, physics, astronomy, mathematics beauty
- **Daily Life & Society**: urban living, food culture, travel, social dynamics

Each day, pick a **unifying theme** and connect all three language lessons to
that theme (e.g., "Cognitive Bias", "The History of Money", "What Makes a Great
Musician"). This creates cross-language reinforcement.

## Lesson Structure

Each lesson should include:

### 1. Reading Passage

- **English**: 300–400 words — advanced articles, essays, or opinion pieces
  with sophisticated vocabulary
- **Japanese**: 300–400 characters including kanji, from essays, news, or
  literary texts
- **Spanish**: 150–200 words using B1–B2 vocabulary and sentence structures

### 2. Vocabulary Section

- Extract 8–10 key words/phrases from the passage
- For each, provide:
  - Word/phrase with pronunciation (romaji for Japanese, IPA for Spanish where
    helpful)
  - Definition
  - Example sentence from the passage
  - Additional usage example

### 3. Comprehension Questions

- 5 questions testing understanding of the passage
- Mix of literal comprehension and inference
- Include answer key at the bottom

### 4. Grammar Point

- **English**: Advanced grammar (subjunctive mood, cleft sentences, inversion,
  concessive clauses, etc.)
- **Japanese**: Advanced grammar patterns (e.g., ～に際して, ～をもって,
  ～ばかりか, ～に他ならない)
- **Spanish**: B1–B2 grammar (subjunctive in noun/adverbial clauses, ser vs
  estar distinctions, compound tenses)
- Provide: explanation, 3–4 example sentences, 3 practice exercises with
  answers

### 5. Writing Exercise (Spanish only)

- A short writing prompt (5–8 sentences)
- Suggested vocabulary list
- A sample response demonstrating target grammar

## Output Format

Each lesson section uses this template inside an `ad-note` callout block:

```markdown
## writing

```ad-note
# English Lesson — YYYY-MM-DD
**Theme**: [Unifying theme]
**Level**: Advanced / IELTS Band 7+

---

## 📖 Reading Passage

[passage]

---

## 📚 Vocabulary

### 1. [word/phrase]

- **Pronunciation**: [if applicable]
- **Definition**: [definition]
- **From passage**: "[quote]"
- **Usage**: [additional example]

[repeat for all vocabulary items]

---

## ❓ Comprehension Questions

1. [question]
...

---

## 📝 Grammar Point: [Topic]

### Explanation

[explanation]

### Examples

1. [example]
...

### Practice

1. [exercise]
...

---

## ✅ Answer Key

### Comprehension Questions

1. [answer]
...

### Grammar Practice

1. [answer]
...
```

## japanese

```ad-note
[Japanese lesson in same structure, in Japanese]
```

## spanish

```ad-note
# Lección de Español — YYYY-MM-DD

[Spanish lesson with writing exercise section ✍️ after grammar practice]
```
```

## Execution Steps

### Step 0: Vault status check

1. **Resolve the target date**:
   - If an argument was passed (e.g. `/lesson 2026-03-01`), use that date
   - Otherwise, run `date +%Y-%m-%d` to get today's date
   - Bind this as `TARGET_DATE` for all subsequent steps

2. **Resolve the output path**:
   - Read the `VAULT_PATH` environment variable
   - If set: output path = `$VAULT_PATH/YYYY/TARGET_DATE.md`
     (e.g. `daily/2026/2026-03-01.md`)
   - If not set: output path = `lessons/TARGET_DATE.md` in this repo
   - Create the year directory if it doesn't exist: `mkdir -p $VAULT_PATH/YYYY`

3. **Check for existing lesson**:
   - If the output file exists, read it
   - If it contains `## writing`, warn the user: "A lesson for TARGET_DATE
     already exists. Overwrite?" — wait for confirmation before proceeding
   - If the file exists but has no `## writing`, proceed (append mode)
   - If the file doesn't exist, proceed (create mode)

4. **Scan recent topics** (for rotation):
   - List the last 7 lesson files in the output directory (sorted by date,
     descending)
   - For each, extract the `**Theme**:` line from the `## writing` section
   - Pass these as "recently used topics — do not repeat" to the generation
     step

### Step 1: Generate lessons

Using the theme selected from Step 0 (avoiding recent topics), generate:

1. English lesson at IELTS Band 7+ level
2. Japanese lesson at N1 level
3. Spanish lesson at B1–B2 level (include writing exercise)

All three lessons must:

- Use `TARGET_DATE` (not today's date) in every section header
- Share the same unifying theme
- Follow the output format template above

### Step 2: Write to file

- If in **create mode**: write the file with all three sections
- If in **append mode**: append the three sections after any existing content
  in the file

The final file structure:

```markdown
---
[frontmatter if creating new file]
---

[existing content if appending]

## writing

```ad-note
[English lesson]
```

## japanese

```ad-note
[Japanese lesson]
```

## spanish

```ad-note
[Spanish lesson]
```
```

### Step 3: Confirm

Report to the user:

- Where the file was saved (full path)
- The theme used
- Whether it was created or appended
- A one-line summary of the lesson topic for each language

## Quality Guidelines

- **Use TARGET_DATE in all headers** — never the current date if a date
  argument was passed
- Make passages genuinely interesting — avoid bland, textbook-style prose
- Grammar points should build progressively over time
- Spanish content should be encouraging for B1–B2 learners
- Japanese should include furigana for less common kanji
- Vary topic domains across consecutive days to maintain breadth
- All content should be original and educational
````

### Step 2: Verify

Run: `mise run verify`
Expected: `✅ Repository structure is valid!`

### Step 3: Format

Run: `mise run fmt`
Expected: `Done.`

### Step 4: Lint check

Run: `mise run lint`

If there are lint errors in SKILL.md from code blocks inside ad-note examples,
those are false positives from the nested triple-backtick blocks. Add the file
to `.markdownlintignore` if needed, or check `.markdownlint.json` for existing
ignores.

### Step 5: Commit

```bash
git add skills/daily-language-lesson/SKILL.md
git commit -m "feat: vault integration and date argument for daily-language-lesson"
```

---

## Task 6: Final check and verify all together

### Step 1: Run full check suite

```bash
mise run check
```

Expected output:

```text
All files are properly formatted.
...
Done.
...
✅ Repository structure is valid!
✅ All checks passed!
```

### Step 2: Final commit (if any formatting auto-fixed)

```bash
git add -A
git commit -m "chore: post-format cleanup"
```

Only needed if `mise run fmt` changed anything in step 1.

### Step 3: Review the git log

```bash
git log --oneline -5
```

Expected: 4–5 commits visible covering all tasks above.
