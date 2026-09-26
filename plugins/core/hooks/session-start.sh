#!/usr/bin/env bash
# Core SessionStart: router + global learnings, then the project's live context.
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PROJ="${CLAUDE_PROJECT_DIR:-$PWD}"
CTX="$PROJ/docs/context"

cat "$ROOT/INDEX.md"; echo
[ -f "$ROOT/LEARNINGS.md" ] && { grep -v '^<!--' "$ROOT/LEARNINGS.md"; echo; }

show() { # file, max lines
  [ -f "$1" ] || return
  echo "### ${1#$PROJ/}"
  head -n "$2" "$1"
  [ "$(wc -l < "$1")" -gt "$2" ] && echo "... (truncated, read the file for the rest)"
  echo
}

if [ -d "$CTX" ]; then
  echo "## Project context (docs/context, read before acting)"
  show "$CTX/STATE.md" 80
  show "$CTX/HANDOFF.md" 40
  if [ -f "$CTX/REQUIREMENTS.md" ]; then
    open=$(grep -cE '^- \[ \] R[0-9]+' "$CTX/REQUIREMENTS.md"); done_=$(grep -cE '^- \[x\] R[0-9]+' "$CTX/REQUIREMENTS.md")
    status=$(grep -m1 -oE 'Status: [A-Z]+' "$CTX/REQUIREMENTS.md")
    echo "### REQUIREMENTS: $open open, $done_ verified. $status"; echo
  fi
  if [ -f "$CTX/DECISIONS.md" ]; then
    echo "### Active decisions (titles only, read DECISIONS.md for detail)"
    grep -E '^## D-[0-9]+' "$CTX/DECISIONS.md" | grep -vi 'superseded' | tail -n 20
    echo
  fi
else
  echo "## Project context"
  echo "No docs/context/ in this repo. If this is a real project, run /kit-init to set it up."
fi
exit 0
