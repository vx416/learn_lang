---
name: explain-english
description: Explain the meaning of an English word, phrase, collocation, or sentence in Traditional Chinese, then always end by asking whether to save it as an Anki vocab card (vocab-to-anki) or grammar card (grammar-to-anki). Use whenever the user asks what some English means (e.g., "X 是啥意思", "X 什麼意思", "這句話是什麼意思", "what does X mean", "X 怎麼用", "X 跟 Y 差在哪"). Do not trigger when the user is asking for correction of their own writing (use correct-writing) or already asked to save something (go straight to vocab-to-anki / grammar-to-anki).
---

# Explain English

Explain what the user asked about, then offer to turn it into a flashcard. The explanation is the main deliverable; the offer is one short line at the end and must never be skipped.

## When to use

- The user quotes English and asks what it means, how it is used, or how it differs from something similar.
- The user asks about a grammar structure they met in a sentence (e.g., "為什麼這裡用 had we", "這是什麼句型").

## Steps

1. **Explain** in Traditional Chinese, keeping English for the examples. Adapt the depth to what was asked:
   - **Word or phrase**: meaning, register or connotation, the structure it takes (e.g., `be subjected to + noun`), 3–5 common collocations, 2–3 C1-level example sentences with translations, and a note on any easily confused form (e.g., `subject to` vs `subjected to`) or pronunciation trap.
   - **Whole sentence**: a natural translation, then break down the parts that make it hard: unfamiliar words, the grammar structure, and any idiom.
   - **Grammar question**: the pattern as a formula, when it is used, one or two more examples, and the common mistake.
2. **Decide what kind of card fits** so the offer is concrete:
   - A word, phrasal verb, collocation, or idiom → vocab card.
   - A sentence pattern, inversion, conditional, verb pattern, or similar structure → grammar card.
   - A sentence that contains both → offer both.
3. **Ask** in one line at the end, naming the item and the card type, e.g.:
   - `要不要把 be subjected to 記成單字卡?`
   - `要不要把「否定副詞置首倒裝」做成文法卡?`
   - `要不要記成卡片?單字卡(be subjected to)或文法卡(had we sat 倒裝)都可以。`
4. **On a yes** ("要", "好", "可以", "記一下", "存單字", "做文法卡"):
   - Vocab → follow `vocab-to-anki`. The word list is exactly the item(s) just explained, so write `.temp/vocab.txt` and go straight to its Stage 2 without a second confirmation round, reusing an example sentence from the explanation as the card's `Sentence`.
   - Grammar → follow `grammar-to-anki`, drafting one card for the structure just explained. Show the draft and confirm as that skill requires, since the cloze span and hint need the user's eye.
   - Both → do vocab first, then grammar.
5. **On a no or no reply**: nothing else to do.

## Output format

Explanation in Markdown with bold headings for the parts (意思、結構、常見搭配、例句、注意區分), then a blank line and the single-line offer. Keep the whole reply under about 250 words unless the user asked for more.

## Notes

- Ask exactly once per explanation. If the user asked about several items in one message, make one combined offer listing them.
- If the item was already saved earlier in the conversation, say so instead of offering again.
