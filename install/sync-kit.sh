#!/usr/bin/env bash
# Fallback for environments where marketplace plugins don't auto-install.
# Copies the chosen plugins' skills into the user skill folder and prints their routing.
# Usage (SessionStart hook in a project): bash .claude/sync-kit.sh core design
set -e
REPO="${KIT_REPO:-sufianweb3/claude-kit}"
KIT="${HOME}/.cache/claude-kit"
if [ -d "$KIT/.git" ]; then git -C "$KIT" pull -q --ff-only || true
else git clone -q --depth 1 "https://github.com/$REPO" "$KIT"; fi
mkdir -p "$HOME/.claude/skills"
for p in "${@:-core}"; do
  [ -d "$KIT/plugins/$p/skills" ] && cp -r "$KIT/plugins/$p/skills/." "$HOME/.claude/skills/"
  if [ "$p" = core ]; then CLAUDE_PLUGIN_ROOT="$KIT/plugins/core" bash "$KIT/plugins/core/hooks/session-start.sh"
  else cat "$KIT/plugins/$p/INDEX.md"; fi
done
