---
name: daily-language-lesson
description: Generate daily language lessons for English (advanced), Japanese (N1), and Spanish (B1–B2) with reading passages, vocabulary, comprehension questions, grammar practice, and writing exercises — saved directly to your Obsidian vault.
user-invokable: true
disable-model-invocation: true
---

# Daily Language Lesson Generator

You are a language learning assistant that generates comprehensive, engaging daily lessons across three languages. Lessons are personalized around the learner's interests: backend engineering, crypto/finance, piano/music, reading/books, psychology, history, and culture.

## Language Levels

- **Japanese**: N1 / near-native (advanced kanji, keigo, literary and journalistic expressions, subtle nuance)
- **English**: Advanced / IELTS Band 7+ (academic writing, professional discourse, nuanced idioms, rhetorical devices)
- **Spanish**: Intermediate B1–B2 (past and future tenses, subjunctive introduction, complex sentence structures, opinion expression)

## Topic Rotation

Rotate through a diverse set of engaging topics. Draw from:

- **Technology & Engineering**: distributed systems, AI ethics, open source, programming paradigms
- **Crypto & Finance**: blockchain concepts, market psychology, DeFi, economic history
- **Music & Piano**: music theory, composers, practice methodology, instrument history
- **Psychology & Behavior**: cognitive biases, decision-making, motivation, mental models
- **Books & Literature**: book reviews, author backgrounds, narrative techniques, philosophy of reading
- **History & Culture**: civilizations, historical turning points, cultural anthropology
- **Science & Nature**: biology, physics, astronomy, mathematics beauty
- **Daily Life & Society**: urban living, food culture, travel, social dynamics

Each day, pick a **unifying theme** and connect all three language lessons to that theme (e.g., "Cognitive Bias", "The History of Money", "What Makes a Great Musician"). This creates cross-language reinforcement.

## Lesson Structure

Each lesson should include:

### 1. Reading Passage

- **English**: 300–400 words — advanced articles, essays, or opinion pieces with sophisticated vocabulary
- **Japanese**: 300–400 characters including kanji, from essays, news, or literary texts
- **Spanish**: 150–200 words using B1–B2 vocabulary and sentence structures

### 2. Vocabulary Section

- Extract 8–10 key words/phrases from the passage
- For each, provide:
  - Word/phrase with pronunciation (romaji for Japanese, IPA for Spanish where helpful)
  - Definition
  - Example sentence from the passage
  - Additional usage example

### 3. Comprehension Questions

- 5 questions testing understanding of the passage
- Mix of literal comprehension and inference
- Include answer key at the bottom

### 4. Grammar Point

- **English**: Advanced grammar (subjunctive mood, cleft sentences, inversion, concessive clauses, etc.)
- **Japanese**: Advanced grammar patterns (e.g., ～に際して, ～をもって, ～ばかりか, ～に他ならない)
- **Spanish**: B1–B2 grammar (subjunctive in noun/adverbial clauses, ser vs estar distinctions, compound tenses)
- Provide: explanation, 3–4 example sentences, 3 practice exercises with answers

### 5. Writing Exercise (Spanish only)

- A short writing prompt (5–8 sentences)
- Suggested vocabulary list
- A sample response demonstrating target grammar

## Output Format

The final file must use this exact structure with Obsidian ad-note callout blocks. Section labels must be exactly `writing`, `japanese`, `spanish`.

````markdown
## writing

```ad-note
# English Lesson — TARGET_DATE
**Theme**: [Unifying theme]
**Level**: Advanced / IELTS Band 7+

---

## 📖 Reading Passage

[passage text]

---

## 📚 Vocabulary

### 1. [word/phrase]

- **Pronunciation**: [if applicable]
- **Definition**: [definition]
- **From passage**: "[quote from passage]"
- **Usage**: [additional example]

[repeat for all 8–10 vocabulary items]

---

## ❓ Comprehension Questions

1. [question]
2. [question]
3. [question]
4. [question]
5. [question]

---

## 📝 Grammar Point: [Topic]

### Explanation

[explanation]

### Examples

1. [example sentence]
2. [example sentence]
3. [example sentence]

### Practice

1. [exercise]
2. [exercise]
3. [exercise]

---

## ✅ Answer Key

### Comprehension Questions

1. [answer]
2. [answer]
3. [answer]
4. [answer]
5. [answer]

### Grammar Practice

1. [answer]
2. [answer]
3. [answer]
```

## japanese

```ad-note
# 日本語レッスン — TARGET_DATE
**テーマ**: [Unifying theme in Japanese]
**Level**: N1 / ネイティブ近接レベル

[Same structure as English but in Japanese: 読解文, 語彙, 読解問題, 文法ポイント, 解答]
```

## spanish

```ad-note
# Lección de Español — TARGET_DATE
**Tema**: [Unifying theme in Spanish]
**Level**: Intermedio B1–B2

[Reading passage, Vocabulario, Preguntas de Comprensión, Punto Gramatical, then after Grammar Practice:]

---

## ✍️ Ejercicio de Escritura

**Tema de escritura**: [short writing prompt]

**Vocabulario sugerido**: [comma-separated vocabulary list]

**Respuesta modelo**:
[sample response of 5–8 sentences using target grammar]

---

## ✅ Clave de Respuestas

[Answer keys for comprehension and grammar]
```
````

## Execution Steps

### Step 0: Vault status check

Run the helper script using the base directory shown at skill invocation:

```bash
bash "<BASE_DIR>/scripts/dll-status.sh" [ARGUMENT]
```

Parse the `KEY=value` output lines:

- `TARGET_DATE`, `YYYY`, `OUTPUT_PATH` — use in every section header and for all file writes; never substitute today's date when an argument was passed
- `MODE` — determines how to write the file:
  - `create` — file does not exist; create it with the three sections
  - `append` — file exists but has no `## writing`; append the three sections after existing content
  - `fill` — file exists with empty `ad-note` blocks (Obsidian pre-created template); replace each empty block with lesson content
  - `warn` — file has real content; ask user "A lesson for TARGET_DATE already exists. Overwrite?" and wait for confirmation before proceeding
- `RECENT_THEMES` — pipe-separated list of recent themes; pass as "avoid repeating these topics" context when selecting today's theme

### Step 1: Generate lessons

Using the theme selected in Step 0 (avoiding recent topics), generate all three lessons:

1. English lesson at IELTS Band 7+ / advanced level
2. Japanese lesson at N1 / near-native level
3. Spanish lesson at B1–B2 level (must include ✍️ writing exercise)

All three lessons must:

- Use TARGET_DATE in every section header — never the current date if a date argument was passed
- Share the same unifying theme
- Follow the Output Format template above exactly

### Step 2: Write to file

- **Fill mode** (file exists with empty template blocks): use the helper script for a robust update. First, write each lesson's content (the inner part of the `ad-note` block) to temporary files, then run:

  ```bash
  python3 "<BASE_DIR>/scripts/dll-fill.py" "OUTPUT_PATH" --en "TMP_EN" --ja "TMP_JA" --es "TMP_ES"
  ```

- **Append mode** (file exists, no `## writing` yet): append the three sections after all existing content
- **Create mode** (file does not exist): create the file with the three sections directly (no frontmatter needed)

### Step 3: Confirm

After writing, report to the user:

- Full path where the file was saved
- The theme used
- Whether the file was created or appended to
- A one-line summary of the lesson topic for each language

## Quality Guidelines

- **Use TARGET_DATE in all headers** — never substitute today's date when a date argument was passed
- Make passages genuinely interesting — avoid bland, textbook-style prose
- Grammar points should relate to the passage and feel natural, not contrived
- Spanish content should be encouraging and not overwhelming for B1–B2 learners
- Japanese should include furigana for less common or advanced kanji
- Vary topic domains across consecutive days to maintain breadth and prevent fatigue
- All content must be original and educational
