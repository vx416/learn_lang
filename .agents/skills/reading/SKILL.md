---
name: reading
description: Generate an English reading article (approx. 5-minute read, defaults to CEFR C1 unless specified otherwise) on an open or specified topic, followed by an in-depth breakdown of challenging vocabulary, grammar, and sentence patterns. Saves to .temp/articles/ and offers to read the article aloud via macOS TTS. Use whenever the user asks for an English article (e.g., "給我一篇英文文章", "想讀英文文章") or asks to read aloud the generated article.
---

# English Reading & Analysis

Provides an English reading article adapted to the requested level (defaulting to CEFR C1) along with educational breakdowns of vocabulary, grammar concepts, and sentence structures. Automatically saves the article to `.temp/articles/` and offers to read it aloud via system TTS.

## When to use

- The user asks for an English article to read (e.g., "給我一篇英文文章", "來篇閱讀", "產生一篇英文短文").
- The user requests reading practice or material for learning English (optionally specifying topic or CEFR level).
- The user responds to an article asking to have it read aloud (e.g., "念給我聽", "朗讀文章", "念出來", "用英音念").

## Workflow

1. **Determine Level, Topic & Tone**:
   - **Level**: Default to **CEFR C1**. If the user specifies a different CEFR level (e.g., B1, B2, C2), adapt the vocabulary complexity, syntactic density, and sentence structures to that level.
   - **Topic**: If the user specifies a topic (e.g., AI, economics, psychology, literature), write on that topic. Otherwise, choose an engaging, intellectual subject (e.g., neuroscience, urban architecture, behavioral economics, environmental science, philosophy of mind).
   - **Style**: High-quality editorial/journalistic prose matching the target level (e.g., *The Economist*, *The Atlantic*, *The Guardian* for C1/C2; *BBC News*, *National Geographic* for B2).

2. **Compose Article**:
   - **Length**: Approximately 450–650 words (~5-minute read for thorough learning).
   - **Structure**: 4 to 5 well-structured paragraphs with clear thematic development and transitions.

3. **Analyze Difficult Vocabulary**:
   - Select 5–8 high-value words, collocations, or idiomatic expressions relevant to the target level.
   - For each item, provide:
     - Part of speech & IPA transcription.
     - Traditional Chinese explanation (繁體中文釋義).
     - Original sentence from the text.
     - Common collocations or usage notes.

4. **Analyze Key Grammar & Syntax**:
   - Select 2–3 notable grammatical points demonstrated in the article (e.g., inversion, participle reduction, subjunctive mood, relative clauses, cleft sentences).
   - Explain the grammar rule and its function in Traditional Chinese.

5. **Analyze Key Sentence Patterns**:
   - Select 2–3 sophisticated or representative sentences from the article.
   - Break down their syntactic components (main clause, subordinate clauses, modifiers).
   - Provide a sentence pattern template / imitation example (句型仿寫或換句話說) to help the user master the pattern.

6. **Save the Article**:
   - Write the full output (article and the three analysis sections, exactly as shown to the user) to `.temp/articles/YYYY-MM-DD-<slug>.md`, where `<slug>` is the title in lowercase kebab-case, at most 6 words (e.g. `2026-09-20-the-quiet-rise-of-urban-forests.md`).
   - Create `.temp/articles/` if needed. A second article on the same day gets its own file; never overwrite an existing one (add `-2`, `-3` to the slug if the name is taken).

7. **Offer Read-Aloud**:
   - At the end of the response, ask the user if they would like the English article read aloud.
   - When the user confirms (e.g., "好", "念給我聽", "念出來", "朗讀"): invoke the `read-aloud` skill to play the article body from `.temp/articles/` via the macOS `say` command (defaulting to `Samantha`, 175 wpm, running in the background for longer passages).

## Output Format

Follow this markdown structure:

```markdown
# [Article Title]

> **Level**: CEFR [C1 / Requested Level] | **Estimated Reading Time**: ~5 mins | **Topic**: [Topic Name]

[Paragraph 1]

[Paragraph 2]

[Paragraph 3]

[Paragraph 4]

---

## 📚 重點單字與片語 (Vocabulary & Expressions)

1. **word / phrase** `[IPA]` *(pos.)*
   - **中文釋義**：...
   - **文中例句**："[Sentence from text]"
   - **常見搭配 / 用法**：...

...

## 🔍 文法重點解析 (Grammar Focus)

1. **[Grammar Point Name]**
   - **文中句型**：...
   - **文法說明**：...

...

## ✍️ 精選句型與結構剖析 (Sentence Patterns & Rhetoric)

1. **[Sentence 1]**
   - **結構分析**：...
   - **句型提煉 / 仿寫**：...

---
*已儲存至 `.temp/articles/YYYY-MM-DD-<slug>.md`*

> 🔊 **需要為你朗讀這篇英文文章嗎？**（直接回覆「念給我聽 / 好」，亦可指定美式、英式發音或調整語速）
```
