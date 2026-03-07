#!/usr/bin/env bash
# Plane skill logout — remove stored credential files.
# Usage: bash scripts/plane_logout.sh --confirm
set -euo pipefail

GLOBAL_RC="$HOME/.planerc"
LOCAL_RC="${CLAUDE_PROJECT_DIR:+$CLAUDE_PROJECT_DIR/.planerc}"

if [ -t 1 ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; CYAN=''; NC=''
fi

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
  cat <<EOF
Usage: bash scripts/plane_logout.sh [--confirm]

Removes saved Plane credentials from:
  - $GLOBAL_RC (global config — affects ALL projects)
  - \$CLAUDE_PROJECT_DIR/.planerc (project-local config, if set)

WARNING: Removing ~/.planerc will affect all projects using that config.
EOF
}

confirm=false
case "${1:-}" in
  --confirm) confirm=true ;;
  -h|--help) usage; exit 0 ;;
  "") ;;
  *) err "Unknown argument: $1"; usage; exit 1 ;;
esac

if [ "$confirm" != true ]; then
  err "Destructive operation — pass --confirm to proceed."
  exit 1
fi

removed_any=false
if [ -f "$GLOBAL_RC" ]; then
  rm -f "$GLOBAL_RC"
  ok "Removed $GLOBAL_RC"
  removed_any=true
fi

if [ -n "$LOCAL_RC" ] && [ -f "$LOCAL_RC" ]; then
  rm -f "$LOCAL_RC"
  ok "Removed $LOCAL_RC"
  removed_any=true
fi

if [ "$removed_any" = false ]; then
  warn "No .planerc file found in expected locations."
fi
