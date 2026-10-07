---
name: anki
description: Create, find, queue, flush, and update Anki flashcards through AnkiConnect or the Git-tracked offline queue (queue/). Use when the user wants to add vocabulary or grammar to Anki, sync queued cards from Git into Anki ("把 queue 同步到 anki", "flush anki queue"), check duplicates, list decks or note types, see which batch is current, or review recent/due cards.
---

# Anki

Talk to the local Anki desktop app through AnkiConnect (HTTP JSON on `127.0.0.1:8765`), with automatic offline fallback to the Git-tracked `queue/` directory when Anki is not installed or not running. All calls go through `scripts/anki.py` next to this file:

```sh
python3 .agents/skills/anki/scripts/anki.py <command> [options]
```

Python 3 standard library only, no install step. `--help` on any command shows its options.

## Prerequisites & Dual-Machine Offline Queue (`queue/`)

- **Online (machine with Anki open + AnkiConnect `2055492159`)**: `list`, `batch`, and `add` talk directly to AnkiConnect and automatically refresh `queue/existing_index.json` (which tracks all existing `Vocab Cloze` words and `Grammar Practice` targets).
- **Offline (machine without Anki)**: When `127.0.0.1:8765` is unreachable, `list`, `batch`, and `add` **automatically fall back to `queue/`** without failing:
  - `list` checks duplicates against `queue/existing_index.json`, `queue/vocab.json`, and `queue/grammar.json`.
  - `add --batch` validates fields against local `*_model.json` and appends new cards to `queue/vocab.json` or `queue/grammar.json`.
  - After queuing cards offline, commit and push `queue/` (`git add queue/ && git commit -m "chore(queue): add anki cards" && git push`) so the machine with Anki can pull and import them.
- **Syncing Queue to Anki (`flush`)**: On the machine with Anki open, run:
  ```sh
  python3 .agents/skills/anki/scripts/anki.py flush
  ```
  This creates any missing models/decks, imports all pending cards from `queue/vocab.json` and `queue/grammar.json` into `English::Vocab::NNN` and `English::Grammar::NNN` batches, clears `queue/*.json`, and updates `queue/existing_index.json`. Commit and push `queue/` afterwards.
- Exit codes: `0` ok (including offline queue fallback), `1` Anki unreachable on online-only commands (`decks`, `models`, `flush`, `reset`, `update`, `raw`), `2` AnkiConnect/duplicate error, `3` bad input.

## Vocabulary cards (the main use)

Vocabulary uses the **`Vocab Cloze`** note type and is grouped into **batches of 200 words**, one sub-deck per batch: `English::Vocab::001`, `English::Vocab::002`, ... The user practices by picking a batch deck in Anki.

Fields of `Vocab Cloze`:

| Field | Content |
|---|---|
| `Word` | the word or phrase, plain (base/dictionary form) |
| `Sentence` | an example sentence with the word wrapped as `{{c1::word}}` (this is what gets blanked out) |
| `WordMeaning` | `(pos.)` + Traditional Chinese meaning of the word |
| `SentenceMeaning` | Traditional Chinese translation of the sentence |
| `SimilarWord` | `<b>word</b><br>...` one similar word and how the two differ in use (back side only) |

The card shows a typing box on the front (`{{type:cloze:Sentence}}`) and reads the word and sentence aloud on the back with Anki's built-in TTS (`{{tts en_US speed=1.2:...}}`, macOS system voice, no audio files).

Vocab decks use the `Vocab` deck options preset: learning steps `1m 10m 1h`, so a new card must be answered correctly three times before it is scheduled for the next day. New batch decks copy the parent's preset automatically.

The model definition is in `vocab_cloze_model.json`. If `anki.py models` does not list `Vocab Cloze`, create it with `anki.py raw createModel "$(cat .agents/skills/anki/vocab_cloze_model.json)"`.

### Adding vocabulary

1. **Check duplicates in one query**: `anki.py list --query 'Word:ubiquitous OR Word:ephemeral'`. `Showing 0 of 0 notes.` means no duplicate. If any exist, skip or ask whether to update.
2. **Write the notes as JSON** (a list; `tags` optional):
   ```json
   [{"fields": {"Word": "ubiquitous",
                "Sentence": "Smartphones have become {{c1::ubiquitous}} in modern life.",
                "WordMeaning": "(adj.) 無所不在的",
                "SentenceMeaning": "智慧型手機在現代生活中已無所不在。",
                "SimilarWord": "<b>pervasive</b><br>ubiquitous 強調隨處可見；pervasive 強調滲透各處（常帶負面或抽象意涵）"},
     "tags": ["vocab"]}]
   ```
   For more than 5 notes, show the user the list and get confirmation first.
3. **Add with `--batch --partial`**, which picks the current batch deck and rolls over to the next one when it reaches 200:
   ```sh
   anki.py add --batch --partial --model "Vocab Cloze" --json words.json     # or --json - for stdin
   ```
   Never pass `--deck` for vocabulary; `--batch` decides the deck.
4. **Report** each created note (the command prints one line per note with its id and deck) and, if a rollover happened, tell the user a new batch was started.

`anki.py batch` shows the current batch deck and how full it is, e.g. `English::Vocab::003 (57/200)`.

## Grammar cards

Grammar uses the **`Grammar Practice`** note type (definition in `grammar_practice_model.json`, same typing box and TTS as vocabulary) and is grouped into batches of 200 exercises: `English::Grammar::001`, `English::Grammar::002`, ...

Fields of `Grammar Practice`:

| Field | Content |
|---|---|
| `Target` | the exact blanked text inside `{{c1::...}}` (without any `::hint`) |
| `GrammarPoint` | short grammar label in Traditional Chinese (e.g. `否定副詞置首倒裝`) |
| `Sentence` | practice sentence wrapped with `{{c1::answer}}` or `{{c1::answer::hint}}` |
| `Prompt` | optional rewrite source (`原句改寫：...`) or base-form cue; never repeats the answer |
| `SentenceMeaning` | Traditional Chinese sentence translation |
| `Explanation` | core formula, when to use it, and a ❌ common mistake if applicable |

If `anki.py models` does not list `Grammar Practice`, create it with `anki.py raw createModel "$(cat .agents/skills/anki/grammar_practice_model.json)"`.

### Adding grammar

```sh
anki.py list --query 'Target:"had we sat" OR Target:"were it not for"'        # batch duplicate check
anki.py add --batch --partial --batch-parent English::Grammar --model "Grammar Practice" --json .temp/grammar.json
anki.py batch --batch-parent English::Grammar
```

## Other note types and decks

`add` works for any note type and deck. It validates field names against the note type and refuses unknown ones.

```sh
anki.py decks
anki.py models
anki.py fields --model Basic
anki.py update --id 1234567890 --field "Back=..." --add-tags x --remove-tags y
anki.py reset --deck English::Vocab::001
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
