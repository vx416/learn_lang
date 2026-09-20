"""Arrow Grading: grade the current card with the arrow keys.

  Left  = Again    Up = Hard    Right = Good    Down = Easy

Works on the answer side only; on the question side the arrows do nothing
(press Enter to show the answer). Grading advances to the next card exactly
as the 1-4 keys do.
"""

from aqt import mw
from aqt.reviewer import Reviewer

KEYS = {
    "Left": 1,   # Again
    "Up": 2,     # Hard
    "Right": 3,  # Good
    "Down": 4,   # Easy
}


def _grade(ease: int):
    def handler() -> None:
        reviewer = mw.reviewer
        if mw.state != "review" or reviewer.state != "answer":
            return
        reviewer._answerCard(ease)
    return handler


_original_shortcut_keys = Reviewer._shortcutKeys


def _shortcut_keys_with_arrows(self):
    keys = list(_original_shortcut_keys(self))
    keys.extend((key, _grade(ease)) for key, ease in KEYS.items())
    return keys


Reviewer._shortcutKeys = _shortcut_keys_with_arrows
