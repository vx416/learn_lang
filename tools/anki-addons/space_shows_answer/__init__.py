"""Space Shows Answer: on cards with a typing box, Space shows the answer
when the box is still empty; once you have typed something, Space is a
normal space (multi-word answers need it). Cards without a typing box
already use Space to show the answer, so nothing changes there.
"""

from aqt import gui_hooks, mw

JS = r"""
(function () {
  var el = document.getElementById("typeans");
  if (!el || el.dataset.spaceShowsAnswer) return;
  el.dataset.spaceShowsAnswer = "1";
  el.addEventListener("keydown", function (e) {
    if (e.key === " " && el.value.trim() === "") {
      e.preventDefault();
      pycmd("ans");
    }
  });
})();
"""


def install_space_handler(card) -> None:
    mw.reviewer.web.eval(JS)


gui_hooks.reviewer_did_show_question.append(install_space_handler)
