#!/usr/bin/env bash
# Plane skill setup — install Python, dependencies, and configure .planerc
# Usage: bash scripts/plane_setup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REQ_FILE="$SKILL_DIR/requirements.txt"
GLOBAL_RC="$HOME/.planerc"
LOCAL_RC="$PWD/.planerc"

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

# --- Step 4: Configure .planerc ---
echo ""
info "Checking Plane configuration..."

# Check existing configs for required fields (supports both KEY=VALUE and JSON)
needs_setup=true
existing_config=""
if [ -f "$LOCAL_RC" ]; then
  existing_config="$LOCAL_RC"
elif [ -f "$GLOBAL_RC" ]; then
  existing_config="$GLOBAL_RC"
fi

if [ -n "$existing_config" ]; then
  if PLANERC_PATH="$existing_config" "$PYTHON" -c "
import os, sys
path = os.environ['PLANERC_PATH']
text = open(path).read().strip()
config = {}
if text.startswith('{'):
    import json
    config = json.loads(text)
else:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, _, v = line.partition('=')
            config[k.strip()] = v.strip()
if config.get('api_key') or config.get('access_token') or config.get('apiKey') or config.get('accessToken'):
    if config.get('workspace_slug') or config.get('workspace'):
        sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    needs_setup=false
    ok "Plane configured (source: $existing_config)"
  fi
fi

if [ "$needs_setup" = true ]; then
  if [ ! -t 0 ]; then
    err ".planerc not configured and stdin is not interactive."
    err "Create ~/.planerc with: api_key=... and workspace_slug=..."
    exit 1
  fi

  echo ""
  info "Let's configure your Plane connection."
  echo "  Get your API key from: Plane > Settings > API Tokens > Create new token"
  echo "  Find workspace slug in your URL: https://app.plane.so/<workspace-slug>/..."
  echo ""

  # Config location choice
  echo "Where should the config be saved?"
  echo "  1) Global  (~/.planerc) — shared across all projects"
  echo "  2) Local   ($LOCAL_RC) — this project only"
  read -rp "Choice [1]: " location_choice
  case "${location_choice:-1}" in
    1) RC_FILE="$GLOBAL_RC" ;;
    2)
      RC_FILE="$LOCAL_RC"
      ;;
    *) err "Invalid choice"; exit 1 ;;
  esac

  # API Key
  read -rp "Plane API Key [required]: " api_key
  if [ -z "$api_key" ]; then
    err "API key is required."
    exit 1
  fi

  # Workspace slug
  read -rp "Workspace slug [required]: " workspace_slug
  if [ -z "$workspace_slug" ]; then
    err "Workspace slug is required."
    exit 1
  fi

  # Base URL
  read -rp "Base URL [https://api.plane.so]: " base_url
  base_url="${base_url:-https://api.plane.so}"

  # Write KEY=VALUE config with 0o600 permissions (pass values via env vars to avoid injection)
  API_KEY="$api_key" WORKSPACE="$workspace_slug" BASE_URL="$base_url" TARGET_RC="$RC_FILE" \
    "$PYTHON" -c "
import os
path = os.environ['TARGET_RC']
parent = os.path.dirname(path)
if parent:
    os.makedirs(parent, exist_ok=True)
with open(path, 'w') as f:
    f.write('# Plane API Configuration\n')
    f.write(f\"api_key={os.environ['API_KEY']}\n\")
    f.write(f\"workspace_slug={os.environ['WORKSPACE']}\n\")
    f.write(f\"base_url={os.environ['BASE_URL']}\n\")
    f.write('disable_delete_issue=true\n')
os.chmod(path, 0o600)
"

  ok "Saved to $RC_FILE"

  # Add .planerc to project .gitignore
  PROJECT_GITIGNORE="$PWD/.gitignore"
  if [ -f "$PROJECT_GITIGNORE" ]; then
    if ! grep -qxF '.planerc' "$PROJECT_GITIGNORE"; then
      echo '.planerc' >> "$PROJECT_GITIGNORE"
      ok "Added .planerc to $PROJECT_GITIGNORE"
    fi
  else
    echo '.planerc' > "$PROJECT_GITIGNORE"
    ok "Created $PROJECT_GITIGNORE with .planerc"
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
