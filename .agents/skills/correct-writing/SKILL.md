---
name: correct-writing
description: Correct an English passage the user wrote, rewrite it at C1–C2 level, score the original, and append both the original and the corrected version to a dated log in .temp/writing/. Use whenever the user writes English and asks for correction, feedback, or a rewrite (e.g., "幫我改這段", "correct this", "這樣寫對嗎"), AND whenever a message consists of one or more longer English sentences of prose with no instruction attached; treat that as writing practice to correct. Do not trigger on English that is a question or instruction addressed to you.
---

# Correct Writing

The user writes English; you give three things back and keep a dated log.

## When to trigger

- The user asks for correction, feedback, or a rewrite of English they wrote.
- The user's message is itself a longer English sentence or passage of prose (roughly 12+ words, or several sentences) with no request attached. Treat it as writing practice and run this skill without asking.
- Not when the English is a question or instruction to you ("can you list the decks?"), a quoted excerpt from an article, or code.

## Steps

1. **Corrected version.** Keep the user's own words, phrases, and sentence structure wherever they are usable. Fix only what is wrong or unnatural: grammar, word choice, collocation, punctuation, word order. The result must read as fluent English that still sounds like the user wrote it. Do not upgrade vocabulary or restructure sentences beyond what fluency requires.
2. **C1–C2 rewrite.** Rewrite the whole passage freely at CEFR C1–C2 level: precise vocabulary, idiomatic collocations, varied sentence structure, mature register. Same meaning, same length give or take 20%.
3. **Score the original** on a 10-point scale for each of grammar, vocabulary, and fluency, plus an overall score and an estimated CEFR level. Follow with the changes that mattered most, at most five, each as "what you wrote → what it should be → why" in one line.
4. **Append to the log** (see below).
5. **Offer to read it aloud.** After the reply, ask in one line whether the user wants to hear the C1–C2 rewrite. If they say yes, follow `.agents/skills/read-aloud/SKILL.md` with the rewrite text.

## Output format

Reply in this order, using these exact headings:

```
## Original
<the user's text exactly as they sent it>

## Corrected
<corrected text>

## C1–C2 rewrite
<rewritten text>

## Score
Grammar 7/10 · Vocabulary 6/10 · Fluency 6/10 · Overall 6.5/10 · Estimated level: B2
- "<what you wrote>" → "<correction>" — <reason>
- ...
```

Explanations are in Traditional Chinese; quoted English stays English. Do not add anything before "## Original".

## Log

Path: `.temp/writing/YYYY-MM-DD.txt` using today's local date. Create the directory if needed. One file per day; if the file exists, append to the end, never overwrite. The `[original]` block is the user's input exactly as they sent it: same spelling mistakes, punctuation, and line breaks, nothing trimmed or cleaned up. It is the point of the log, so never skip it, even when there was nothing to correct. Each entry:

```
=== #N  HH:MM  overall 6.5/10  (B2)

[original]
<the user's text verbatim>

[corrected]
<corrected text>

```

`N` is the entry's sequence number within that file, starting at 1. Compute it by counting existing entries before appending.

Write it like this. The body goes through a quoted heredoc so `$`, backticks, and quotes in the text are stored verbatim; only the header line is built by the shell:

```sh
mkdir -p .temp/writing
f=".temp/writing/$(date +%F).txt"
n=$(( $(cat "$f" 2>/dev/null | grep -c '^=== #') + 1 ))
{
  printf '=== #%s  %s  overall 6.5/10  (B2)\n\n' "$n" "$(date +%H:%M)"
  cat <<'EOF_LOG'
[original]
...

[corrected]
...

EOF_LOG
} >> "$f"
```

Do the append silently; do not print the file contents back. Mention the file path and entry number in one short line after the score, e.g. `已記錄到 .temp/writing/2026-09-20.txt #3`.

## Notes

- If the user pastes a single sentence, do all three steps anyway; keep the rewrite to one or two sentences.
- If the passage is already C1–C2 with nothing to fix, say so in the score section and still produce the rewrite as an alternative phrasing.
- Never log anything other than what the user wrote and the corrected version.
