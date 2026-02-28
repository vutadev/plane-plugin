#!/usr/bin/env bash
# Plane skill setup — install Python, dependencies, and configure .plane.env
# Usage: bash scripts/plane_setup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
DEFAULT_ENV_FILE="$PROJECT_DIR/.plane.env"
ENV_FILE="${PLANE_ENV_FILE:-$DEFAULT_ENV_FILE}"
# Resolve relative override against project dir
if [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$PROJECT_DIR/$ENV_FILE"
fi
LEGACY_ENV_FILE="$SKILL_DIR/.plane.env"
REQ_FILE="$SKILL_DIR/requirements.txt"

# Colors (fallback to plain if no tty)
if [ -t 1 ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; CYAN=''; NC=''
fi

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

load_env_from_file() {
  local file="$1"
  [ -f "$file" ] || return 0

  set -a
  while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    [[ -z "$key" || "$key" == \#* ]] && continue
    value=$(echo "$value" | xargs)
    # Only set if not already in environment
    if [ -z "${!key:-}" ]; then
      export "$key=$value"
    fi
  done < "$file"
  set +a
}

# --- Step 1: Detect or install Python ---
detect_python() {
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
      local ver
      ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
      local major minor
      major=$(echo "$ver" | cut -d. -f1)
      minor=$(echo "$ver" | cut -d. -f2)
      if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
        PYTHON="$cmd"
        ok "Python found: $($cmd --version) at $(command -v "$cmd")"
        return 0
      fi
    fi
  done
  return 1
}

if ! detect_python; then
  err "Python >= 3.10 not found."
  echo ""
  info "Install Python using one of:"
  echo "  macOS:   brew install python3"
  echo "  Ubuntu:  sudo apt install python3 python3-pip"
  echo "  Fedora:  sudo dnf install python3 python3-pip"
  echo "  Windows: https://www.python.org/downloads/"
  echo ""
  exit 1
fi

# --- Step 2: Install pip if missing ---
if ! "$PYTHON" -m pip --version &>/dev/null; then
  warn "pip not found. Attempting to install..."
  if "$PYTHON" -m ensurepip --default-pip &>/dev/null; then
    ok "pip installed via ensurepip"
  else
    err "pip not available. Install it manually:"
    echo "  $PYTHON -m ensurepip --default-pip"
    echo "  OR: curl https://bootstrap.pypa.io/get-pip.py | $PYTHON"
    exit 1
  fi
fi

# --- Step 3: Install plane-sdk ---
if "$PYTHON" -c "import plane" &>/dev/null; then
  ok "plane-sdk already installed"
else
  info "Installing dependencies from $REQ_FILE..."
  "$PYTHON" -m pip install -r "$REQ_FILE" --quiet
  ok "plane-sdk installed"
fi

# --- Step 4: Configure .plane.env ---
echo ""
info "Checking Plane configuration..."

ACTIVE_ENV_FILE="$ENV_FILE"
if [ -f "$ENV_FILE" ]; then
  load_env_from_file "$ENV_FILE"
elif [ -f "$LEGACY_ENV_FILE" ]; then
  warn "Using legacy env file at $LEGACY_ENV_FILE"
  ACTIVE_ENV_FILE="$LEGACY_ENV_FILE"
  load_env_from_file "$LEGACY_ENV_FILE"
fi

needs_setup=false
[ -z "${PLANE_API_KEY:-}" ] && [ -z "${PLANE_ACCESS_TOKEN:-}" ] && needs_setup=true
[ -z "${PLANE_WORKSPACE_SLUG:-}" ] && needs_setup=true

if [ "$needs_setup" = true ]; then
  if [ ! -t 0 ]; then
    err ".plane.env not configured and stdin is not interactive."
    err "Create $ENV_FILE with: PLANE_API_KEY (or PLANE_ACCESS_TOKEN), PLANE_WORKSPACE_SLUG"
    exit 1
  fi

  echo ""
  info "Let's configure your Plane connection."
  echo "  Get your API key from: Plane → Settings → API Tokens → Create new token"
  echo "  Find workspace slug in your URL: https://app.plane.so/<workspace-slug>/..."
  echo ""

  # API Key
  current_key="${PLANE_API_KEY:-${PLANE_ACCESS_TOKEN:-}}"
  read -rp "Plane API Key [$( [ -n "$current_key" ] && echo '***set***' || echo 'required')]: " input_key
  api_key="${input_key:-$current_key}"
  if [ -z "$api_key" ]; then
    err "API key is required."
    exit 1
  fi

  # Workspace slug
  current_slug="${PLANE_WORKSPACE_SLUG:-}"
  read -rp "Workspace slug [$( [ -n "$current_slug" ] && echo "$current_slug" || echo 'required')]: " input_slug
  workspace_slug="${input_slug:-$current_slug}"
  if [ -z "$workspace_slug" ]; then
    err "Workspace slug is required."
    exit 1
  fi

  # Base URL
  current_url="${PLANE_BASE_URL:-https://api.plane.so}"
  read -rp "Base URL [$current_url]: " input_url
  base_url="${input_url:-$current_url}"

  # Write .plane.env to project-local location (or override via PLANE_ENV_FILE)
  mkdir -p "$(dirname "$ENV_FILE")"
  cat > "$ENV_FILE" <<EOF
# Plane API Configuration
PLANE_API_KEY=$api_key
PLANE_WORKSPACE_SLUG=$workspace_slug
PLANE_BASE_URL=$base_url
EOF

  ACTIVE_ENV_FILE="$ENV_FILE"
  ok "Saved to $ACTIVE_ENV_FILE"

  # Reload
  export PLANE_API_KEY="$api_key"
  export PLANE_WORKSPACE_SLUG="$workspace_slug"
  export PLANE_BASE_URL="$base_url"
else
  ok "Plane environment configured (source: $ACTIVE_ENV_FILE)"
  if [ "$ACTIVE_ENV_FILE" = "$LEGACY_ENV_FILE" ] && [ "$ENV_FILE" != "$LEGACY_ENV_FILE" ]; then
    warn "Consider moving env file to $ENV_FILE"
  fi
fi

# --- Step 5: Verify connection ---
echo ""
info "Verifying Plane connection..."
if "$PYTHON" "$SCRIPT_DIR/plane_verify.py"; then
  echo ""
  ok "Setup complete! Plane skill is ready to use."
else
  echo ""
  err "Verification failed. Check your API key and workspace slug."
  err "Re-run: bash scripts/plane_setup.sh"
  exit 1
fi
