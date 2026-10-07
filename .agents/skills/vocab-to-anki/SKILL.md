---
name: vocab-to-anki
description: Summarize key vocabulary from the current context into a comma-separated .txt file in .temp/, confirm the list and allow user additions, and import the final list into Anki via the anki skill (Vocab Cloze model) upon confirmation, deleting the temp file afterwards. Use when the user asks to extract, organize, or save vocabulary from the conversation/reading into Anki (e.g., "整理單字", "把單字存到 anki", "歸納單字").
---

# Vocab to Anki

Extracts and organizes key vocabulary from the current conversation context into a simple comma-separated `.txt` file under `.temp/`, allows the user to review and supplement words, imports them into Anki as "Vocab Cloze" flashcards upon user confirmation, and cleans up the temporary file.

## When to use

- The user wants to extract or summarize vocabulary from the current context or reading article (e.g., "幫我整理剛剛的單字", "把這篇的重要單字存起來", "整理單字到 anki").
- The user responds to an extracted vocabulary list to add more words, edit the list, or give confirmation to proceed (e.g., "可以", "OK", "確認加入", "再幫我加上...").

## Workflow

The workflow proceeds in two stages: **Extract & Confirm**, followed by **Import to Anki & Cleanup**.

### Stage 1: Extract & Confirm

1. **Extract Vocabulary**:
   - Identify key, high-value, or challenging words from the current context (e.g., from the recent reading text or discussion).
   - Use base/dictionary forms (lemmatized, lowercase unless proper nouns).

2. **Save to `.temp/`**:
   - File path: `.temp/vocab.txt`
   - **Strict format**: Comma-separated English words only, without definitions, IPA, or example sentences.
   - Example format:
     ```text
     ubiquitous, serendipity, delineate, ephemeral, tenacious
     ```
   - Write or overwrite this file into `.temp/vocab.txt`.

3. **Confirm with User**:
   - Present the extracted word list clearly to the user.
   - Inform the user that the list is written to `.temp/vocab.txt`.
   - Remind the user they can:
     - Directly reply to add more words.
     - Edit `.temp/vocab.txt` directly.
     - Say "可以" / "OK" to proceed with creating Anki flashcards.

### Stage 2: Import to Anki & Cleanup (After User Confirms)

When the user gives approval (e.g. "可以", "確認", "沒問題"):

1. **Read Final Word List**:
   - Read `.temp/vocab.txt`. If the user provided additional words in their confirmation message, append them to the file and list first.
   - Parse all words (splitting by commas, stripping whitespace and empty entries).

2. **Check Duplicates (Single Query)**:
   - Before generating example sentences, check all words at once:
     ```sh
     python3 .agents/skills/anki/scripts/anki.py list --query 'Word:word1 OR Word:word2 OR ...'
     ```
   - Skip any words already in Anki and note them for the final summary.

3. **Card Specification (`Vocab Cloze` model, `--batch` into `English::Vocab::NNN`)**:
   - Do not read `vocab_cloze_model.json` or `anki/SKILL.md` unless `Vocab Cloze` is missing in Anki; all required fields (`inOrderFields`) are listed below:
     - `Word`: base/dictionary form, lowercase unless a proper noun.
     - `Sentence`: one natural sentence at CEFR C1 level (idiomatic, mature register, may use subordinate clauses or collocations a C1 reader meets in editorials and literary non-fiction), 8–20 words, with the target word wrapped as `{{c1::...}}` exactly as it appears. Prefer the base form so what the user types matches `Word`; if an inflected form reads better, the cloze wraps the inflected form and that is what the user must type. Never leave the word unblanked elsewhere in the sentence. Reuse the sentence from the article/context when possible; if it is shorter than 8 words, extend it rather than replace it.
     - `WordMeaning`: the part of speech as used in the sentence, in parentheses, followed by a short Traditional Chinese gloss for that sense; separate multiple senses with `、`. Labels: `n.`, `v.`, `adj.`, `adv.`, `prep.`, `conj.`, `phr. v.` (phrasal verb), `phr.` (other multi-word phrase), `idiom`. Examples: `(adj.) 無所不在的`, `(phr. v.) 被迫承受、遭受`. No other English. It is shown on the front as a hint.
     - `SentenceMeaning`: natural Traditional Chinese translation of the whole sentence. Also shown on the front.
     - `SimilarWord`: one near-synonym or easily confused word, then how the two differ in use. Format: `<b>word</b><br>` followed by one line per word in Traditional Chinese, separated by `；`, each naming the word and the situation it fits, e.g. `<b>thorough</b><br>meticulous 強調對細節一絲不苟，形容人或做事態度；thorough 強調完整、沒有遺漏，形容檢查或調查`. Shown on the back only. Keep it under about 60 Chinese characters.
     - `tags`: `["vocab"]`.

4. **Import via `anki.py` & Cleanup (Never pass `--deck`)**:
   ```sh
   python3 .agents/skills/anki/scripts/anki.py add --batch --partial --model "Vocab Cloze" --json - <<'EOF'
   [{"fields": {"Word": "...", "Sentence": "...", "WordMeaning": "...", "SentenceMeaning": "...", "SimilarWord": "..."}, "tags": ["vocab"]}]
   EOF
   python3 .agents/skills/anki/scripts/anki.py batch
   rm -f .temp/vocab.txt
   ```
   - **Offline Auto-Queue**: If Anki is not running on this machine, `anki.py` automatically checks `queue/existing_index.json` and appends the cards to `queue/vocab.json`. When output shows `queued note to 'queue/vocab.json'`, stage and commit `queue/` (`git add queue/ && git commit -m "chore(queue): add vocab cards"` and `git push` if a remote exists) so the machine with Anki can pull and run `anki.py flush`.

5. **Report Summary**:
   - Report the outcome to the user: either the Anki batch deck (`English::Vocab::001`) and its fill level, or the offline queue count in `queue/vocab.json` (and Git commit/push status), number of cards created/queued, any skipped duplicates, and confirm that `.temp/vocab.txt` has been cleaned up.
