#!/usr/bin/env bash
# Robust wrapper that resolves its own script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/setup-hooks.py" "$@"
elif command -v python >/dev/null 2>&1; then
    python "$SCRIPT_DIR/setup-hooks.py" "$@"
elif command -v py >/dev/null 2>&1; then
    py -3 "$SCRIPT_DIR/setup-hooks.py" "$@"
else
    echo "[ERROR] Python 3 not found on PATH. Please install Python."
    exit 1
fi
