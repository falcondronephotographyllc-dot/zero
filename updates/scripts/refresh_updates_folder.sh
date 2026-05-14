#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPDATES_DIR="$ROOT_DIR/updates"

rm -rf "$UPDATES_DIR"
mkdir -p "$UPDATES_DIR"

cd "$ROOT_DIR"

mapfile -t CHANGED_FILES < <(
  {
    git diff --name-only
    git diff --name-only --cached
    git ls-files --others --exclude-standard
  } | \
  grep -v '^$' | \
  grep -v '^updates/' | \
  grep -v '^updates.zip$' | \
  sort -u
)

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  echo "No changed files found. updates/ is empty."
  exit 0
fi

for file in "${CHANGED_FILES[@]}"; do
  if [[ -f "$file" ]]; then
    mkdir -p "$UPDATES_DIR/$(dirname "$file")"
    cp "$file" "$UPDATES_DIR/$file"
  fi
done

echo "Copied ${#CHANGED_FILES[@]} changed paths into $UPDATES_DIR"
