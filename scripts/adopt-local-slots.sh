#!/bin/sh
# Move hand-installed copies out of the agent skill slots before a machine-managed
# install (home-manager) owns them. Only touches the skill names in this repo.
#
# Rules:
#   - an entry whose real path already points into this clone is kept untouched
#   - a plain directory or an old symlink is moved into a timestamped backup
#   - anything else (a plain file, a broken special path) stops the run
#
# Usage: scripts/adopt-local-slots.sh [clone-root]
set -eu

repo=${1:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}
names="tikz-diagramming inkscape-diagramming scala-best-practices de-ai-flavor org-inline-code-spacing design-scope-discipline"

[ -d "$repo/skills" ] || { echo "not a skill clone: $repo" >&2; exit 1; }
for name in $names; do
  [ -f "$repo/skills/$name/SKILL.md" ] || { echo "missing skill in clone: $name" >&2; exit 1; }
done

# Moving an entry leaves its slot empty: this script never installs the replacement
# link. Run the machine activation (ee / nix-rebuild) in the same window, or those
# skills stay invisible on this host until you do.
echo "warning: moved entries are not replaced here; run the machine activation immediately after." >&2

state="$HOME/.local/share"
mkdir -p "$state"
# mktemp -d gives this run an exclusive directory: a second run in the same second
# cannot reuse the name, so its "nothing to move" cleanup can never delete a
# previous run's backup.
backup=$(mktemp -d "$state/agent-skills-backup-$(date +%Y%m%d-%H%M%S)-XXXXXX")
moved=0

for slot in agents claude; do
  for name in $names; do
    target="$HOME/.$slot/skills/$name"
    [ -e "$target" ] || [ -L "$target" ] || continue

    real=$(readlink -f "$target" 2>/dev/null || true)
    if [ "$real" = "$repo/skills/$name" ]; then
      echo "keep  $target (already points into the clone)"
      continue
    fi

    if [ -L "$target" ]; then
      echo "move  $target (symlink -> $(readlink "$target"))"
      mkdir -p "$backup/$slot"
      mv "$target" "$backup/$slot/$name"
    elif [ -d "$target" ]; then
      echo "move  $target (plain directory)"
      mkdir -p "$backup/$slot"
      mv "$target" "$backup/$slot/$name"
    else
      echo "stop  $target is neither a directory nor a symlink; resolve it by hand" >&2
      exit 1
    fi
    moved=$((moved + 1))
  done
done

if [ "$moved" -eq 0 ]; then
  rmdir "$backup" 2>/dev/null || true
  echo "nothing to move; no conflicting entries under $HOME/.agents/skills or $HOME/.claude/skills"
else
  echo "moved $moved entr(y/ies) to $backup"
  echo "verify the backup, then re-run the machine activation"
fi
