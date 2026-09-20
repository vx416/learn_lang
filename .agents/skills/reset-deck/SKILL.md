---
name: reset-deck
description: Reset an Anki deck so every card in it becomes new again (AnkiConnect forgetCards), so the whole deck shows up for study from scratch. Use when the user says "reset <deck>", "重設 <deck>", "forget <deck>", or "讓 <deck> 的卡重新出現", naming a deck like "vocab/001", "grammar/001", "vocab" (all vocab batches), or a full Anki name like English::Vocab::001.
---

# Reset Deck

Turn every card in a deck back into a new card. Nothing is deleted; only the scheduling (learning steps, intervals, due dates, review history counts) is cleared, so the cards appear under **New** again.

## Steps

1. **Resolve the deck name.** Short forms map onto the `English` tree:
   - `vocab/001`, `vocab 001`, `vocab::001` → `English::Vocab::001`
   - `grammar/001` → `English::Grammar::001`
   - `vocab` or `grammar` alone → the parent deck, which resets every batch under it
   - A name that already contains `::` is used as-is.
   Check it exists with `anki.py decks`. If it does not, list the decks and ask; never guess.

2. **Find and forget the cards** (one pipeline, from the project root):
   ```sh
   python3 .agents/skills/anki/scripts/anki.py raw findCards '{"query": "deck:English::Vocab::001"}' \
     | python3 -c 'import json,sys; print(json.dumps({"cards": json.load(sys.stdin)}))' \
     | xargs -0 python3 .agents/skills/anki/scripts/anki.py raw forgetCards
   ```
   `deck:` matches sub-decks too, so a parent name resets all batches. Count the ids from `findCards` for the report.

3. **Report** in one line: deck name and how many cards were reset. If `findCards` returned an empty list, say the deck has no cards and stop.

## Notes

- The user asks for this on purpose, so run it directly; no confirmation step. Only stop to ask when the deck name cannot be resolved.
- `forgetCards` also resets the repetition and lapse counters. Cards keep their original position in the new-card queue.
- Anki must be open with AnkiConnect (see `.agents/skills/anki/SKILL.md` for the exit codes if the call fails).
