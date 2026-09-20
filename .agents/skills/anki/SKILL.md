---
name: anki
description: Create, find, and update Anki flashcards through the AnkiConnect API. Use when the user wants to add vocabulary, sentences, or grammar points to Anki, check whether a card already exists, list decks or note types, see which vocab batch is current, or review what was recently added or is due.
---

# Anki

Talk to the local Anki desktop app through AnkiConnect (HTTP JSON on `127.0.0.1:8765`). All calls go through `scripts/anki.py` next to this file. Run it as:

```sh
python3 .agents/skills/anki/scripts/anki.py <command> [options]
```

Python 3 standard library only, no install step. `--help` on any command shows its options.

## Prerequisites

- Anki desktop is open and the AnkiConnect add-on (code `2055492159`) is installed. Anki must be restarted once after installing the add-on.
- Exit codes: `1` Anki unreachable, `2` AnkiConnect rejected the request (duplicate, bad deck, etc.), `3` bad input (unknown field, missing deck). Read stderr and tell the user; do not retry blindly.

## Vocabulary cards (the main use)

Vocabulary uses the **`Vocab Cloze`** note type and is grouped into **batches of 200 words**, one sub-deck per batch: `English::Vocab::001`, `English::Vocab::002`, ... The user practices by picking a batch deck in Anki.

Fields of `Vocab Cloze`:

| Field | Content |
|---|---|
| `Word` | the word or phrase, plain |
| `Sentence` | an example sentence with the word wrapped as `{{c1::word}}` (this is what gets blanked out) |
| `WordMeaning` | Traditional Chinese meaning of the word |
| `SentenceMeaning` | Traditional Chinese translation of the sentence |
| `SimilarWord` | one similar word and how the two differ in use (back side only) |

The card shows a typing box on the front (`{{type:cloze:Sentence}}`) and reads the word and sentence aloud on the back with Anki's built-in TTS (`{{tts en_US:...}}`, macOS system voice, no audio files).

Vocab decks use the `Vocab` deck options preset: learning steps `1m 10m 1h`, so a new card must be answered correctly three times before it is scheduled for the next day. New batch decks copy the parent's preset automatically.

The model definition is in `vocab_cloze_model.json`. If `anki.py models` does not list `Vocab Cloze`, create it with `anki.py raw createModel "$(cat .agents/skills/anki/vocab_cloze_model.json)"`.

### Adding vocabulary

1. **Check duplicates** for each word: `anki.py list --query 'Word:ubiquitous'`. `Showing 0 of 0 notes.` means no duplicate. If it exists, show it and ask whether to update or skip.
2. **Write the notes as JSON** (a list; `tags` optional):
   ```json
   [{"fields": {"Word": "ubiquitous",
                "Sentence": "Smartphones have become {{c1::ubiquitous}} in modern life.",
                "WordMeaning": "無所不在的",
                "SentenceMeaning": "智慧型手機在現代生活中已無所不在。"},
     "tags": ["vocab"]}]
   ```
   For more than 5 notes, show the user the list and get confirmation first.
3. **Add with `--batch`**, which picks the current batch deck and rolls over to the next one when it reaches 200:
   ```sh
   anki.py add --batch --model "Vocab Cloze" --json words.json     # or --json - for stdin
   ```
   Never pass `--deck` for vocabulary; `--batch` decides the deck.
4. **Report** each created note (the command prints one line per note with its id and deck) and, if a rollover happened, tell the user a new batch was started.

`anki.py batch` shows the current batch deck and how full it is, e.g. `English::Vocab::003 (57/200)`.

## Grammar cards

Grammar uses the **`Grammar Practice`** note type and is grouped into batches of 200 exercises: `English::Grammar::001`, `English::Grammar::002`, ...

Fields of `Grammar Practice`:

| Field | Content |
|---|---|
| `GrammarPoint` | Grammar point title (e.g. `否定副詞置首倒裝`) |
| `Sentence` | Practice sentence wrapped with cloze syntax `{{c1::answer::hint}}` |
| `Prompt` | Source sentence to rewrite or clue (e.g. `原句改寫：...`) |
| `SentenceMeaning` | Traditional Chinese sentence translation |
| `Explanation` | Core formula and grammar explanation |
| `CommonMistake` | Typical pitfalls, wrong pattern (❌), or contrast pair (⭕️) |

The back of the card automatically reads the sentence aloud via TTS (`{{tts en_US speed=1.2:Sentence}}`).
The model definition is in `grammar_practice_model.json`.

### Adding grammar

Add with `--batch` and `--batch-parent English::Grammar`:
```sh
anki.py add --batch --batch-parent "English::Grammar" --batch-size 200 --model "Grammar Practice" --json grammar.json
```

## Grammar cards

Grammar uses the **`Grammar Practice`** note type (definition in `grammar_practice_model.json`, same typing box and TTS as vocabulary) and its own batches `English::Grammar::001`, `002`, ... Same steps as vocabulary with these differences:

```sh
anki.py list --query 'Target:"had we sat"'                                   # duplicate check
anki.py add --batch --batch-parent English::Grammar --model "Grammar Practice" --json .temp/grammar.json
anki.py batch --batch-parent English::Grammar
```

If `anki.py models` does not list `Grammar Practice`, create it with `anki.py raw createModel "$(cat .agents/skills/anki/grammar_practice_model.json)"`.

## Other note types and decks

`add` works for any note type and deck. It validates field names against the note type and refuses unknown ones.

```sh
anki.py decks
anki.py models
anki.py fields --model Basic
anki.py update --id 1234567890 --field "Back=..." --add-tags x --remove-tags y
```

Ask the user which deck to use if it is not obvious. Never invent a deck or note type name. `add` refuses exact duplicates of the first field; rejected items are reported with a reason, and nothing is added unless every item passes or you pass `--partial`.

## Reviewing what is in Anki

```sh
anki.py list --deck English::Vocab --added 7      # added in the last 7 days, all batches
anki.py list --deck English::Vocab::002 --due      # due now in batch 2
anki.py list --tag grammar --limit 50
anki.py list --query "tag:vocab rated:1:1"         # raw Anki search syntax
anki.py list ... --json                            # machine-readable
```

## Anything else

`anki.py raw <action> '<json params>'` calls any AnkiConnect action, e.g. `raw sync '{}'`. Create decks by hand or sync only when the user explicitly asks. Full API reference: https://git.sr.ht/~foosoft/anki-connect

## Notes

- Field values are HTML. Use `<br>` for line breaks and escape `<`, `>`, `&` in content. Cloze markers `{{c1::...}}` are the exception and must stay as-is.
- Never delete notes or decks unless the user explicitly asks in the current request, and confirm the exact ids first.
- This skill is only the transport to Anki. Rules about what a good card looks like (word choice, sentence quality) live in the card-writing skills.
