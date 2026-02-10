# Daily Language Lesson Skill

Generate comprehensive daily language learning lessons for English, Japanese, and Spanish at customized proficiency levels.

## Features

- **English lessons** at native level: Advanced literature, idioms, sophisticated grammar
- **Japanese lessons** at native level: Advanced kanji, keigo, literary expressions
- **Spanish lessons** at entry level: Basic vocabulary, simple grammar for beginners

Each lesson includes:

- Reading passage appropriate for the level
- Vocabulary extraction with definitions and examples
- Comprehension questions with answer key
- Grammar point with explanations and practice exercises

## Usage

Run the skill using any of these commands:

```bash
/daily-language-lesson
/dll
/lesson
```

## Output

Lessons are saved to dated folders:

```text
lessons/
  2026-01-28/
    english.md
    japanese.md
    spanish.md
```

## Customization

You can modify the proficiency levels or lesson structure by editing `prompt.md`.

## Example Workflow

1. Run `/lesson` each morning
2. Open the generated markdown files
3. Study one or all three languages
4. Complete the exercises and check your answers
5. Track your progress over time by reviewing past lessons

## Tips

- The skill generates fresh content each day with diverse topics
- Grammar points build progressively (though each lesson is standalone)
- Spanish content is designed to be encouraging for beginners
- Japanese includes furigana references where helpful
- You can regenerate lessons if you want different content
