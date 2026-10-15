#!/bin/sh
# Link IDENTITY.md as the global context file of every local AI tool.
# Existing non-symlink files are backed up as <file>.bak once.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
python3 -I "$here/build.py"
for target in \
  "$HOME/.claude/CLAUDE.md" \
  "$HOME/.gemini/GEMINI.md" \
  "$HOME/.codex/AGENTS.md" \
  "$HOME/.config/opencode/AGENTS.md"
do
  mkdir -p "$(dirname "$target")"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.bak"
    echo "backup: $target.bak"
  fi
  ln -sfn "$here/IDENTITY.md" "$target"
  echo "linked: $target"
done
