---
name: daily-language-lesson
description: Generate comprehensive daily language learning lessons for English (native), Japanese (native), and Spanish (entry level) with reading passages, vocabulary, comprehension questions, and grammar practice
metadata:
  author: haru
  version: 1.0.0
  aliases: ["dll", "lesson"]
context: fork
disable-model-invocation: true
---

# Daily Language Lesson Generator

Generate today's language lessons and save them as markdown files in a dated folder structure.

## Language Levels

- **English**: Native level (advanced literature, idioms, nuanced grammar)
- **Japanese**: Native level (advanced kanji, keigo, literary expressions)
- **Spanish**: Entry level (basic vocabulary, simple grammar, present tense focus)

## Lesson Structure

Each lesson should include:

### 1. Reading Passage

- **English**: 300-400 words from literature, essays, or advanced articles with sophisticated vocabulary
- **Japanese**: 300-400 characters including kanji, from novels, news, or cultural texts
- **Spanish**: 150-200 words using basic vocabulary and simple sentence structures

### 2. Vocabulary Section

- Extract 8-10 key words/phrases from the passage
- Provide:
  - Word/phrase with pronunciation (romanji for Japanese)
  - Definition
  - Example sentence from the passage
  - Additional usage example

### 3. Comprehension Questions

- 5 questions testing understanding of the passage
- Mix of literal comprehension and inference
- Include answer key at the bottom

### 4. Grammar Point

- **English**: Advanced grammar (subjunctive mood, cleft sentences, inversion, etc.)
- **Japanese**: Advanced grammar patterns (e.g., ～に際して, ～をもって, ～ばかりか)
- **Spanish**: Basic grammar (present tense conjugation, gender agreement, basic prepositions)
- Provide:
  - Clear explanation
  - 3-4 example sentences
  - 3 practice exercises with answers

## File Organization

Create lessons in this structure:

```text
lessons/YYYY-MM-DD/
  english.md
  japanese.md
  spanish.md
```

## Format Example

Each markdown file should follow this template:

```markdown
# [Language] Lesson - [Date]

## 📖 Reading Passage

[passage text]

---

## 📚 Vocabulary

### 1. [word/phrase]

- **Pronunciation**: [if applicable]
- **Definition**: [definition]
- **From passage**: "[example from passage]"
- **Usage**: [additional example]

[repeat for all vocabulary items]

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

[clear explanation of the grammar point]

### Examples

1. [example sentence with translation]
2. [example sentence with translation]
3. [example sentence with translation]

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

## Execution Steps

1. Get today's date in YYYY-MM-DD format
2. Create the lessons directory structure: `lessons/YYYY-MM-DD/`
3. Generate the English lesson at native level and save to `english.md`
4. Generate the Japanese lesson at native level and save to `japanese.md`
5. Generate the Spanish lesson at entry level and save to `spanish.md`
6. Confirm completion and show the user where the lessons were saved

## Quality Guidelines

- Ensure passages are engaging and culturally relevant
- Choose diverse topics (culture, science, daily life, history, etc.)
- Grammar points should build progressively over time
- Spanish content should be encouraging for beginners
- Japanese should include furigana for kanji when helpful for reference
- All content should be original and educational

Start generating today's lessons now.
