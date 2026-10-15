#!/bin/sh
# Link IDENTITY.md as the global context file of every local AI tool.
#   ./install.sh              build, then link; anything already at a target
#                             (file or foreign symlink) is moved to
#                             <target>.bak.<timestamp>, never overwritten
#   ./install.sh --uninstall  remove our links and restore the newest backup
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
src="$here/IDENTITY.md"
targets="$HOME/.claude/CLAUDE.md $HOME/.gemini/GEMINI.md $HOME/.codex/AGENTS.md $HOME/.config/opencode/AGENTS.md"

ours() { [ -L "$1" ] && [ "$(readlink "$1")" = "$src" ]; }

if [ "${1:-}" = "--uninstall" ]; then
  for t in $targets; do
    ours "$t" || continue
    last="$(ls -1t "$t".bak.* 2>/dev/null | head -n 1 || true)"
    if [ -n "$last" ]; then
      # rename over the link: the target is never missing in between
      mv -f "$last" "$t"
      echo "restored: $t <- $last"
    else
      rm "$t"
      echo "unlinked: $t"
    fi
  done
  exit 0
fi

python3 -I "$here/build.py"
stamp="$(date +%Y%m%d-%H%M%S)"
for t in $targets; do
  if ours "$t"; then
    echo "ok: $t"
    continue
  fi
  mkdir -p "$(dirname "$t")"
  if [ -e "$t" ] || [ -L "$t" ]; then
    mv "$t" "$t.bak.$stamp"
    echo "backup: $t.bak.$stamp"
  fi
  ln -s "$src" "$t"
  echo "linked: $t"
done
