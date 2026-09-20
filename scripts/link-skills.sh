#!/usr/bin/env sh
# Refresh Claude Code symlinks: .claude/skills/<name> -> ../../.agents/skills/<name>
set -eu
cd "$(dirname "$0")/.."
mkdir -p .claude/skills

# Remove stale links
for link in .claude/skills/*; do
  [ -L "$link" ] && [ ! -e "$link" ] && rm "$link"
done

# Link every real skill (skip _template and friends)
for dir in .agents/skills/*/; do
  name=$(basename "$dir")
  case "$name" in _*) continue ;; esac
  [ -f "$dir/SKILL.md" ] || continue
  ln -sfn "../../.agents/skills/$name" ".claude/skills/$name"
  echo "linked $name"
done
