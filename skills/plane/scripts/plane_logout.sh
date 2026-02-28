#!/usr/bin/env bash
# Plane skill logout — remove stored credential files.
# Usage: bash scripts/plane_logout.sh --confirm
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
DEFAULT_ENV_FILE="$PROJECT_DIR/.plane.env"
ENV_FILE="${PLANE_ENV_FILE:-$DEFAULT_ENV_FILE}"
if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$PROJECT_DIR/$ENV_FILE"
fi
LEGACY_ENV_FILE="$SKILL_DIR/.plane.env"

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
  - $ENV_FILE
  - $LEGACY_ENV_FILE (legacy location, if present)

Notes:
  - This cannot unset variables in your parent shell process.
  - After running, also execute:
      unset PLANE_API_KEY PLANE_ACCESS_TOKEN PLANE_WORKSPACE_SLUG PLANE_BASE_URL PLANE_ENV_FILE
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
if [ -f "$ENV_FILE" ]; then
  rm -f "$ENV_FILE"
  ok "Removed $ENV_FILE"
  removed_any=true
fi

if [ -f "$LEGACY_ENV_FILE" ] && [ "$LEGACY_ENV_FILE" != "$ENV_FILE" ]; then
  rm -f "$LEGACY_ENV_FILE"
  ok "Removed legacy file $LEGACY_ENV_FILE"
  removed_any=true
fi

if [ "$removed_any" = false ]; then
  warn "No .plane.env file found in expected locations."
fi

echo ""
info "To clear current shell variables, run:"
echo "unset PLANE_API_KEY PLANE_ACCESS_TOKEN PLANE_WORKSPACE_SLUG PLANE_BASE_URL PLANE_ENV_FILE"
