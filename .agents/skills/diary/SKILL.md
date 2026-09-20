---
name: diary
description: Turn an English diary entry the user wrote into a corrected version and an expanded, richer version, score the original, and append all of it to a weekly file in .temp/diary/. Use when the user says the text is their diary or journal (e.g., "這是我的日記", "今天的日記", "diary:", "journal") and pastes English prose.
---

# Diary

The user writes a diary entry in English. Run the full `correct-writing` treatment (correct, C1–C2 rewrite, score), then expand the rewrite into a fuller entry, and keep a weekly log.

## Steps

1. **Correct, rewrite, and score** the entry following steps 1–3 of `.agents/skills/correct-writing/SKILL.md`: the corrected version that keeps the user's wording, the C1–C2 rewrite, and the score with the key changes.
2. **Expand** the C1–C2 rewrite into a richer diary entry, about 1.5–2× its length, same level, first person, same day and events:
   - Build only on what the user wrote: add sensory detail, feelings, a reflection or a takeaway, and linking sentences between events.
   - Do not invent new events, people, or facts. Where a detail is needed to make a sentence work, keep it generic ("the café", "later that evening") rather than specific.
   - Keep the diary voice: informal but well-written, no essay structure, no headings inside the entry.
3. **Append to the weekly file** (below).
4. **Offer to read it aloud.** After the reply, ask in one line whether the user wants to hear the C1–C2 rewrite. If they say yes, follow `.agents/skills/read-aloud/SKILL.md` with the rewrite text.

## Output format

```
## Original
<the user's entry exactly as they sent it>

## Corrected
<corrected entry>

## C1–C2 rewrite
<rewritten entry>

## Expanded
<expanded entry>

## Score
<same format as correct-writing>
```

Explanations in Traditional Chinese; quoted English stays English. One short line with the log path and entry number after the score, e.g. `已記錄到 .temp/diary/2026-09-w3.txt #2`.

## Weekly file

Path: `.temp/diary/YYYY-MM-wN.txt`, where `N` is the week of the month (days 1–7 → w1, 8–14 → w2, 15–21 → w3, 22–28 → w4, 29–31 → w5). Same file for the whole week; append, never overwrite. The `[original]` block is the user's input exactly as they sent it: same spelling mistakes, punctuation, and line breaks, nothing trimmed or cleaned up. It is the point of the log, so never skip it, even when there was nothing to correct. Do not also write to `.temp/writing/`.

```sh
mkdir -p .temp/diary
f=".temp/diary/$(date +%Y-%m)-w$(( ($(date +%-d) - 1) / 7 + 1 )).txt"
n=$(( $(cat "$f" 2>/dev/null | grep -c '^=== #') + 1 ))
{
  printf '=== #%s  %s  overall 7/10  (B2)\n\n' "$n" "$(date '+%Y-%m-%d (%a) %H:%M')"
  cat <<'EOF_LOG'
[original]
<the user's text verbatim>

[corrected]
<corrected entry>

[rewrite]
<rewritten entry>

[expanded]
<expanded entry>

EOF_LOG
} >> "$f"
```

The body goes through a quoted heredoc so the user's text is stored verbatim; only the header line is built by the shell. `#N` is the entry's sequence number within that weekly file, starting at 1. Do the append silently.
