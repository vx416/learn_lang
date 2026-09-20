# .agents/skills/

Agent skills for language learning. `.agents/skills/` is the cross-tool skill directory scanned natively by OpenAI Codex, Gemini CLI, Google Antigravity, GitHub Copilot, and others. Claude Code is bridged via per-skill symlinks in `.claude/skills/` (see below).

## Format

Skills follow the open [Agent Skills](https://agentskills.io) specification. Each skill is a directory containing a `SKILL.md`:

```markdown
---
name: skill-name
description: One sentence saying what this skill does and when to use it.
---

# Skill Title

## When to use
...

## Steps
1. ...
2. ...

## Output format
...
```

### Rules

- `name`: kebab-case, 1–64 characters, must match the directory name.
- `description`: agents decide whether to load a skill from this line alone, so it must cover both what it does and what triggers it.
- Keep `SKILL.md` concise (under 500 lines). Put long reference material in separate files and say in `SKILL.md` when to read them.
- Directories starting with `_` are templates or internal files, not skills.

## Adding a skill

```sh
cp -r .agents/skills/_template .agents/skills/<new-skill-name>
# edit .agents/skills/<new-skill-name>/SKILL.md
scripts/link-skills.sh   # refresh Claude Code symlinks
```

## Claude Code bridge

Claude Code only scans `.claude/skills/`. `scripts/link-skills.sh` creates one symlink there per skill (`.claude/skills/<name> -> ../../.agents/skills/<name>`) and removes links whose target no longer exists. Symlinking the whole `.claude/skills` directory is avoided because Claude Code has a known regression with directory-level symlinks.
