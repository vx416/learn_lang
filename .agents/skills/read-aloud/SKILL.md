---
name: read-aloud
description: Read English text aloud through the Mac's speakers with the macOS `say` command. Use when the user asks to hear text ("唸給我聽", "read this to me", "唸一遍"), whether they paste the text or point at something saved in .temp/ (e.g., "唸 diary #2", "唸今天 writing 的第 3 篇的 rewrite", "唸剛才那篇文章"). Also invoked by correct-writing and diary when the user accepts the offer to hear the rewrite.
---

# Read Aloud

Play English text through the speakers with `say`. Nothing is written or changed.

## 1. Resolve the text

- **Pasted text**: read exactly what the user gave, English only. If the message mixes Chinese instructions with English text, read only the English.
- **From `.temp/writing/` or `.temp/diary/`**: the user names the folder, optionally a date or week, an entry number `#N`, and which block. Entries in those files start with `=== #N`. Blocks are `[original]`, `[corrected]`, `[rewrite]`, `[expanded]`. Defaults: the most recent file, the last entry, the `[rewrite]` block (writing files have only `[original]` and `[corrected]`; there the default is `[corrected]`). Find it with `grep -n '^=== #'` and read the block between its heading and the next blank-line-separated heading.
- **From `.temp/articles/`**: the user names a date, a title fragment, or "剛才那篇" (most recent file). Read only the article body: from the first paragraph after the `> **Level**` line up to the `---` that precedes the analysis sections. Skip the title unless asked.
- If the reference is ambiguous (several entries or files match), list the candidates in one line and ask.

## 2. Play

```sh
say -v Samantha -r 175 "<text>"
```

- **Voice**: `Samantha` (US) by default. `Daniel` for British, `Karen` for Australian, or whatever the user asks for. If an Enhanced or Premium voice with the same name is installed, `say` uses it automatically.
- **Speed**: `-r` is words per minute. 175 normal, 140 for "慢一點", 200 for "快一點". A number from the user wins.
- **Long text**: `say` blocks until playback ends, roughly 1 minute per 175 words. For anything over about 250 words, run the command in the background so the reply is not blocked, and tell the user it is playing.
- **Quoting**: pass the text through a heredoc or a file (`say -f file.txt`) rather than inline quotes when it contains quotes or apostrophes.
- **Save instead of play**: only when asked. `say -v Samantha -r 175 -o out.aiff -f file.txt` writes a file; put it in `.temp/audio/` and give the path.

## 3. Reply

One short line: what was read (source and block, or "你貼的段落"), voice, and speed. Do not echo the text back.
