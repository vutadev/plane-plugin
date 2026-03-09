#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 0.2.0"
  exit 1
fi

VERSION="$1"

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Invalid version format '$VERSION'. Expected semver X.Y.Z (e.g. 0.2.0)"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"

# packages/cli/package.json — top-level "version" field (line 4)
FILE="$ROOT/packages/cli/package.json"
sed -i '4s/"version": "[^"]*"/"version": "'"$VERSION"'"/' "$FILE"
echo "Updated $FILE"

# packages/cli/package-lock.json — lines 3 and 9 (root + package entry)
FILE="$ROOT/packages/cli/package-lock.json"
sed -i '3s/"version": "[^"]*"/"version": "'"$VERSION"'"/' "$FILE"
sed -i '9s/"version": "[^"]*"/"version": "'"$VERSION"'"/' "$FILE"
echo "Updated $FILE"

# .claude-plugin/plugin.json
FILE="$ROOT/.claude-plugin/plugin.json"
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$FILE"
echo "Updated $FILE"

# .claude-plugin/marketplace.json
FILE="$ROOT/.claude-plugin/marketplace.json"
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$FILE"
echo "Updated $FILE"

echo ""
echo "All files bumped to v$VERSION"
