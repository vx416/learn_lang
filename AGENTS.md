# AGENTS.md

This is a personal language-learning project. The rules in this file apply to every AI agent working here (Claude Code, OpenAI Codex, Google Antigravity / Gemini CLI, and others).

## Skills

All skills live in `.agents/skills/<skill-name>/SKILL.md`, following the open [Agent Skills](https://agentskills.io) specification. This is the cross-tool location that Codex, Gemini CLI, Antigravity, and others scan natively.

If your tool does not scan `.agents/skills/` on its own:

1. At the start of the session, list `.agents/skills/*/SKILL.md` and read each file's frontmatter (`name`, `description`).
2. When the user's request matches a skill's description, or the user invokes it by name, read that skill's full `SKILL.md` and follow it.
3. Directories starting with `_` are templates, not skills.

Claude Code reads `.claude/skills/`, which contains one symlink per skill pointing into `.agents/skills/`. Run `scripts/link-skills.sh` after adding or removing a skill to refresh those links. Never write skill content into `.claude/skills/` directly.

See `.agents/skills/README.md` for the skill format and how to add one.

## Fast-Paths (Zero `view_file` Overhead & Stream Explanation First)

### Word / Phrase Lookup (`explain-english` Fast-Path)
Whenever the user sends a single English word/phrase or asks what an English expression means (e.g. `cadence`, `X 是啥意思`, `what does X mean`):
1. **NEVER call `view_file`** on `explain-english/SKILL.md` or `vocab-to-anki/SKILL.md`, and **NEVER run a separate `anki.py list` call** beforehand.
2. **Stream the full explanation text FIRST in Turn 1 [HARD RULE]**:
   - In your **very first response turn**, you **MUST output the complete explanation in the message body FIRST** (so the user sees the explanation immediately in `< 2s` while reading), and attach the single `anki.py add` tool call at the end of that same turn:
     - Headings: `**意思**`, `**結構**`, `**常見搭配**` (3–5 items), `**例句**` (2–3 C1 sentences with `zh-TW` translations), `**注意區分**` (pronunciation traps / near-synonyms).
   - In the **same first turn** (after the explanation text), invoke a single `run_command` to save/queue the card (`--partial` handles duplicate checks automatically):
     ```sh
     python3 .agents/skills/anki/scripts/anki.py add --batch --partial --model "Vocab Cloze" --json - <<'EOF'
     [{"fields": {"Word": "<base_word>", "Sentence": "<C1 sentence with {{c1::word}}>", "WordMeaning": "(<pos.>) <zh-TW meaning>", "SentenceMeaning": "<zh-TW translation>", "SimilarWord": "<b><synonym></b><br><zh-TW contrast under 60 chars>"}, "tags": ["vocab"]}]
     EOF
     ```
3. **Turn 2 (after `anki.py add` completes)**: Reply with **only one short status line** (e.g. `✅ 已自動加入單字卡佇列：cadence (queue/vocab.json 共 N 筆)` or `✅ 已自動加入 Anki：English::Vocab::001`)—never repeat the explanation.

