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
