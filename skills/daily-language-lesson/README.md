# Daily Language Lesson Skill

Generate daily language learning lessons for English (advanced), Japanese (N1), and Spanish (B1–B2), saved directly to your Obsidian vault or a local `lessons/` folder.

## Features

- **English** at IELTS Band 7+ / advanced level: academic writing, nuanced idioms, rhetorical devices
- **Japanese** at N1 / near-native: advanced kanji, keigo, literary and journalistic expressions
- **Spanish** at B1–B2: past/future tenses, subjunctive intro, opinion expression

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

Lessons will be written to `$VAULT_PATH/YYYY/YYYY-MM-DD.md` — the year subfolder is created automatically. If the file already exists (Obsidian pre-creates daily notes), the lesson sections are appended.

If `VAULT_PATH` is not set, lessons fall back to `lessons/YYYY-MM-DD.md` in this repo.

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

Each lesson is written as a single markdown file with three sections using Obsidian `ad-note` callout blocks:

````markdown
## writing

```ad-note
# English Lesson — YYYY-MM-DD
...
```

## japanese

```ad-note
# 日本語レッスン — YYYY-MM-DD
...
```

## spanish

```ad-note
# Lección de Español — YYYY-MM-DD
...
```
````

## Daily workflow

1. Run `mise run lesson` each morning
2. Open your vault — today's daily note will have the three lesson sections
3. Complete the exercises and check your answers
4. Vary: use `/lesson 2026-03-05` to prepare future lessons in advance

## Tips

- Topics rotate across 8 domains (tech, crypto, music, psychology, books, history, science, daily life) and link all three languages to a shared theme
- The skill checks the last 7 lessons to avoid repeating recent topics
- If today's lesson already exists in the file, the skill will ask before overwriting
- Spanish content is designed to be encouraging for B1–B2 learners
- Japanese includes furigana references where helpful
