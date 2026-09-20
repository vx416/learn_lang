---
name: grammar-to-anki
description: Extract grammar points from the current context, draft cloze practice cards into .temp/grammar.json, confirm with the user, and import them into Anki via the anki skill (Grammar Practice model, English::Grammar batches). Use when the user asks to extract grammar exercises, make grammar cards, or save grammar to Anki (e.g., "整理這篇文法到 anki", "提煉文法題目", "做文法卡片", "把文法存到 anki").
---

# Grammar to Anki

Same two-stage workflow as `vocab-to-anki` (draft to `.temp/`, confirm, import through the `anki` skill, clean up). This file only states what differs for grammar.

## When to use

- The user wants grammar exercises or cards from the current context or reading article (e.g., "幫我提煉這篇的文法題目", "把剛剛的文法做成卡片").
- The user replies to a drafted list to adjust, add, or confirm (e.g., "可以", "確認", "新增第3題...").

## Stage 1: Extract & Confirm

1. **Pick 2–4 grammar structures** from the context that a CEFR C1 learner still gets wrong: inversion, participle and reduced relative clauses, subjunctive and unreal conditionals, cleft sentences, correlative conjunctions, preposition and verb-pattern collocations, and similar. Skip basics.
2. **Draft `.temp/grammar.json`**: a JSON list of `{"fields": {...}, "tags": ["grammar"]}` objects. Field names come from `.agents/skills/anki/grammar_practice_model.json` (`inOrderFields`); do not restate them here.
3. **Show the draft** to the user in Markdown (sentence with the blank, answer, explanation), say it is in `.temp/grammar.json`, and ask them to adjust or confirm.

## Content rules

The card shows `Sentence` with the blank, `SentenceMeaning`, and `Prompt` (if any) on the front; the user types the blanked text; the back shows `Target`, `GrammarPoint`, `Explanation`, and reads the completed sentence aloud.

- `Sentence`: one natural C1-level sentence, 10–25 words, with exactly the structure under test wrapped as `{{c1::...}}`. Keep the blank short enough to type (2–6 words). A hint after `::` is allowed only when the answer would otherwise be ambiguous, e.g. `{{c1::had we sat::auxiliary + past participle}}`. Reuse a sentence from the article when possible; extend it if too short.
- `Target`: the blanked text exactly as it appears inside `{{c1::...}}` (without the hint).
- `GrammarPoint`: short label in Traditional Chinese, e.g. `否定副詞置首倒裝`.
- `Prompt`: optional. A rewrite source (`原句改寫：We had hardly sat down when...`) or a base-form cue (`sit`). Never repeats the answer.
- `SentenceMeaning`: natural Traditional Chinese translation of the whole sentence.
- `Explanation`: the rule as a formula plus one line on when to use it, in Traditional Chinese with English pattern words. Include a ❌ common mistake when there is a well-known one.
- `tags`: `["grammar"]`.

## Stage 2: Import to Anki & Cleanup

1. Read `.temp/grammar.json`; apply any edits the user gave in their confirmation.
2. Follow the "Grammar cards" section of `.agents/skills/anki/SKILL.md`: check duplicates on `Target`, add with `add --batch --batch-parent English::Grammar --model "Grammar Practice" --json .temp/grammar.json`, then run `batch --batch-parent English::Grammar`.
3. `rm -f .temp/grammar.json`.
4. Report the batch deck and fill level, number of cards added, and any skipped duplicates.
