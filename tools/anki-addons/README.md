# Anki add-ons

Small local add-ons for Anki desktop. Install by copying a folder into Anki's add-on directory and restarting Anki:

```sh
cp -r tools/anki-addons/repeat_card tools/anki-addons/arrow_grading tools/anki-addons/space_shows_answer "$HOME/Library/Application Support/Anki2/addons21/"
```

That path is macOS. On other systems, open Anki, go to **Tools → Add-ons → View Files** to find the `addons21` directory, and copy the folders there instead.

After editing an add-on in this repo, run the same `cp` again and restart Anki; Anki loads add-ons only at startup. To skip the copy step, symlink instead of copying (edits then take effect on the next restart):

```sh
for a in repeat_card arrow_grading space_shows_answer; do
  ln -sfn "$PWD/tools/anki-addons/$a" "$HOME/Library/Application Support/Anki2/addons21/$a"
done
```

If Anki's add-on list shows one as disabled or errored, check **Tools → Add-ons**, select it, and use **Toggle Enabled** or read the error there.

## repeat_card

In the reviewer, **Q** (or **Shift+Q**) shows the current card's front again without grading it. Shift+Q exists because CJK input methods such as Zhuyin swallow a plain `q`. Use it to retype a word right away. It does not touch scheduling or the undo history, unlike Undo (Cmd+Z), which also reverts earlier operations such as notes added or deleted through AnkiConnect.

## arrow_grading

On the answer side of a card, the arrow keys grade it and move on: **←** Again, **↑** Hard, **→** Good, **↓** Easy. On the question side they do nothing; press Enter to show the answer first.

## space_shows_answer

On cards with a typing box, **Space** shows the answer while the box is empty (skip typing). Once you have typed something, Space inserts a space as usual, so multi-word grammar answers still work.
