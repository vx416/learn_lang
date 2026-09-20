---
name: review-writing
description: Go through the writing logs in .temp/writing/ and .temp/diary/, find the user's recurring mistakes and the words or phrases they do not yet use well, present a summary, and on confirmation turn the chosen items into Anki grammar cards (grammar-to-anki) and vocab cards (vocab-to-anki) built from the user's own corrected sentences. Use when the user asks to review their writing, see what they keep getting wrong, or make cards from their writing logs (e.g., "整理我的寫作錯誤", "看我最近常錯什麼", "把我的錯誤做成卡片").
---

# Review Writing

Mine the logs that `correct-writing` and `diary` keep, show the user what keeps going wrong, and file the useful items into Anki through the existing card skills.

## Stage 1: Analyze & Confirm

1. **Read the logs.** Every `.txt` in `.temp/writing/` and `.temp/diary/`. Default to all entries; if the user names a period ("這週", "這個月", "最近 10 篇"), filter by the date in the filename and the entry header. Each entry has `[original]`, `[corrected]`, and for diaries `[rewrite]` and `[expanded]`. If there are no entries, say so and stop.

2. **Diff original against corrected** for every entry and collect each change. Classify:
   - **Grammar / usage patterns**: articles, tense and aspect, subject–verb agreement, prepositions, word order, run-ons and fragments, countability, comparatives, relative clauses, and similar. Group the same pattern across entries and count occurrences.
   - **Vocabulary**: words or phrases the user misused, or that the correction/rewrite replaced with a better one. Also take words from `[rewrite]` and `[expanded]` that are clearly above what the user wrote (C1 level) and worth learning. Count repeats.

3. **Report** in Traditional Chinese, most frequent first:

   ```
   ## 常犯錯誤（N 篇紀錄，YYYY-MM-DD ~ YYYY-MM-DD）
   1. **[pattern]** — 出現 k 次
      - "<your sentence>" → "<corrected>"   (date)
      - ...（最多 3 例）
      一句話說明規則。
   ...（最多 8 項）

   ## 不熟的單字與片語
   | 單字 / 片語 | 你的寫法 | 修正 / 重寫用法 | 次數 |
   ...（最多 15 項）

   ## 建議做成卡片
   文法：[1, 2, 4]    單字：[ubiquitous, take into account, ...]
   ```

   Ask the user which items to turn into cards, or to confirm the suggestion.

## Stage 2: Make cards (after the user confirms)

- **Grammar** → follow Stage 2 of `.agents/skills/grammar-to-anki/SKILL.md`. Build each item's `Sentence` from the user's own **corrected** sentence, blanking the structure they got wrong; put the user's original wording in `Explanation` as the ❌ example. `Prompt` may quote the original sentence as a rewrite cue.
- **Vocabulary** → follow Stage 2 of `.agents/skills/vocab-to-anki/SKILL.md`. Use the corrected or rewritten sentence from the log as the example sentence whenever it meets that skill's sentence rules.
- Both skills handle duplicate checks, batching, and reporting. Do not call `anki.py` directly except as those skills describe.

## Notes

- Never edit or delete the log files.
- Do not report one-off slips (typos, a single missing comma) as patterns unless they recur.
- Report the card outcome exactly as the two card skills print it: batch decks, counts, skipped duplicates.
