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
2. **Draft `.temp/grammar.json`**: a JSON list of `{"fields": {...}, "tags": ["grammar"]}` objects using the six `Grammar Practice` fields below (do not read `grammar_practice_model.json` or `anki/SKILL.md` unless the model is missing in Anki).
3. **Show the draft** to the user in Markdown (sentence with the blank, answer, explanation), say it is in `.temp/grammar.json`, and ask them to adjust or confirm.

## Content rules

The card shows `Sentence` with the blank, `SentenceMeaning`, and `Prompt` (if any) on the front; the user types the blanked text; the back shows `Target`, `GrammarPoint`, `Explanation`, and reads the completed sentence aloud.

- `Target`: the blanked text exactly as it appears inside `{{c1::...}}` (without the hint). Must be non-empty (first field).
- `GrammarPoint`: short label in Traditional Chinese, e.g. `否定副詞置首倒裝`.
- `Sentence`: one natural C1-level sentence, 10–25 words, with exactly the structure under test wrapped as `{{c1::...}}`. Keep the blank short enough to type (2–6 words). A hint after `::` is allowed only when the answer would otherwise be ambiguous, e.g. `{{c1::had we sat::auxiliary + past participle}}`. Reuse a sentence from the article when possible; extend it if too short.
- `Prompt`: optional (`""` if unused). A rewrite source (`原句改寫：We had hardly sat down when...`) or a base-form cue (`sit`). Never repeats the answer.
- `SentenceMeaning`: natural Traditional Chinese translation of the whole sentence.
- `Explanation`: the rule as a formula plus one line on when to use it, in Traditional Chinese with English pattern words. Include a ❌ common mistake when there is a well-known one.
- `tags`: `["grammar"]`.

## Stage 2: Import to Anki & Cleanup

1. Read `.temp/grammar.json`; apply any edits the user gave in their confirmation.
2. Add to Anki (or `queue/grammar.json` automatically if Anki is offline) and check batch/queue status:
   ```sh
   python3 .agents/skills/anki/scripts/anki.py add --batch --partial --batch-parent English::Grammar --model "Grammar Practice" --json .temp/grammar.json
   python3 .agents/skills/anki/scripts/anki.py batch --batch-parent English::Grammar
   rm -f .temp/grammar.json
   ```
   - If Anki is not running on this machine, `anki.py` automatically appends the cards to `queue/grammar.json`. Stage and commit `queue/` (`git add queue/ && git commit -m "chore(queue): add grammar cards"` and `git push` if a remote exists) so the machine with Anki can pull and run `anki.py flush`.
3. Report the batch deck and fill level (or `queue/grammar.json` pending count and Git sync status), number of cards added/queued, and any skipped duplicates.
