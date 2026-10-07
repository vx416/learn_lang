---
name: explain-english
description: Explain the meaning of an English word, phrase, collocation, or sentence in Traditional Chinese, and automatically save vocabulary items as Anki Vocab Cloze cards (via anki.py / queue/vocab.json) by default without asking first. Use whenever the user asks what some English means (e.g., "X 是啥意思", "X 什麼意思", "這句話是什麼意思", "what does X mean", "X 怎麼用", "X 跟 Y 差在哪") or sends a single word/phrase to look up. Do not trigger when the user is asking for correction of their own writing (use correct-writing).
---

# Explain English

Explain what the user asked about, and **automatically record vocabulary items to Anki (`Vocab Cloze` / `queue/vocab.json`) by default** in the same turn.

## When to use

- The user sends a word/phrase or quotes English and asks what it means, how it is used, or how it differs from something similar.
- The user asks about a grammar structure they met in a sentence (e.g., "為什麼這裡用 had we", "這是什麼句型").

## Steps (Explain-First, Command-Second [HARD RULE])

To ensure the user sees the explanation immediately (`< 2s`) without waiting for tool execution:

1. **Turn 1 — Output the Full Explanation Text FIRST + Attach Single `anki.py add` Call**:
   - Do **NOT** call `view_file` on `vocab-to-anki/SKILL.md` or `anki/SKILL.md`, and do **NOT** run `anki.py list` first.
   - Write the complete explanation in the **message text of Turn 1** (in Traditional Chinese, keeping English for examples, with bold headings `**意思**`、`**結構**`、`**常見搭配**`、`**例句**`、`**注意區分**`, under ~250 words):
     - **Word or phrase**: meaning, register/connotation, structure (e.g., `be subjected to + noun`), 3–5 common collocations, 2–3 C1-level example sentences with translations, and any easily confused form or pronunciation trap.
     - **Whole sentence**: natural translation, then breakdown of unfamiliar words, grammar structure, and idioms.
     - **Grammar question**: pattern formula, when to use it, 1–2 examples, and common mistakes (for pure grammar questions, ask in one line at the end whether to make a `Grammar Practice` card).
   - For any **word, phrasal verb, collocation, or idiom**, attach this single `run_command` call in **that same Turn 1** (right after outputting the explanation text):
     ```sh
     python3 .agents/skills/anki/scripts/anki.py add --batch --partial --model "Vocab Cloze" --json - <<'EOF'
     [{"fields": {"Word": "<base_word>", "Sentence": "<8-20 word C1 sentence with {{c1::word}}>", "WordMeaning": "(<pos.>) <zh-TW gloss>", "SentenceMeaning": "<zh-TW sentence translation>", "SimilarWord": "<b><word></b><br><zh-TW contrast under 60 chars>"}, "tags": ["vocab"]}]
     EOF
     ```
2. **Turn 2 — One-Line Confirmation Only**:
   - Once `anki.py add` finishes, output **only one short line** confirming the card status (e.g., `✅ 已自動加入單字卡佇列：cadence (queue/vocab.json 共 N 筆)` or `⚠️ 已存在於單字庫，略過新增`). Never repeat the explanation.
