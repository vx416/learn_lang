# Anki add-ons

Small local add-ons for Anki desktop. Install by copying a folder into Anki's add-on directory and restarting Anki:

```sh
cp -r tools/anki-addons/repeat_card tools/anki-addons/arrow_grading "$HOME/Library/Application Support/Anki2/addons21/"
```

## repeat_card

In the reviewer, **Ctrl+R** (Cmd+R on macOS) shows the current card's front again without grading it. Use it to retype a word right away. It does not touch scheduling or the undo history, unlike Undo (Cmd+Z), which also reverts earlier operations such as notes added or deleted through AnkiConnect.

## arrow_grading

On the answer side of a card, the arrow keys grade it and move on: **←** Again, **↑** Hard, **→** Good, **↓** Easy. On the question side they do nothing; press Enter to show the answer first.
