"""Repeat Card: show the current card's front again without answering it.

Shortcut in the reviewer: Q.
Nothing is graded or rescheduled and nothing is pushed onto Anki's undo stack,
so it is safe to press as often as you like.
"""

from aqt import mw
from aqt.reviewer import Reviewer

SHORTCUT = "Q"


def repeat_card() -> None:
    reviewer = mw.reviewer
    if mw.state != "review" or reviewer.card is None:
        return
    reviewer._showQuestion()


_original_shortcut_keys = Reviewer._shortcutKeys


def _shortcut_keys_with_repeat(self):
    keys = list(_original_shortcut_keys(self))
    keys.append((SHORTCUT, repeat_card))
    return keys


Reviewer._shortcutKeys = _shortcut_keys_with_repeat
